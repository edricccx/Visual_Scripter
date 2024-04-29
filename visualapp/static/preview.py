import sys
import os
import site
import cv2
from transformers.pipelines import pipeline
from moviepy.editor import VideoFileClip, concatenate_videoclips
from sentence_transformers import SentenceTransformer, util

captioner = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")

# Function to caption frames from the video
def caption_frames(video_path, interval=10):
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    captions = []
    frame_number = 0
    while True:
        # Read the next frame
        ret, frame = cap.read()
        if not ret:
            break

        # Caption the frame using the image captioning pipeline (replace this with your captioning logic)
        frame_filename = f"frame_{frame_number}.png"
        cv2.imwrite(frame_filename, frame)
        caption = f"{captioner(frame_filename)[0]['generated_text']} {frame_number}"
        captions.append(caption)

        # Increment the frame number
        frame_number += 1

        # Skip frames to achieve the desired interval
        cap.set(cv2.CAP_PROP_POS_MSEC, (frame_number * interval) * 1000)

    # Release the video capture object
    cap.release()

    for i in range(frame_number):
        frame_filename = f"frame_{i}.png"
        if os.path.exists(frame_filename):
            os.remove(frame_filename)

    return captions

if __name__ == "__main__":
    if len(sys.argv) > 1:
        reference_sentence = sys.argv[1]
    else:
        reference_sentence = ""

    video_path = "visualapp/static/movie.mp4"
    interval = 2  # Interval in seconds

    # Generate captions for frames in the video
    frame_captions = caption_frames(video_path, interval)

    # List of sentences to compare to the reference sentence
    sentences_to_compare = frame_captions

    # Load the Sentence Transformer model
    model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')

    # Encode the reference sentence and the list of sentences to compare
    reference_embedding = model.encode([reference_sentence])
    compare_embeddings = model.encode(sentences_to_compare)

    # Calculate cosine similarities
    similarities = util.pytorch_cos_sim(reference_embedding, compare_embeddings)

    # Create a list of tuples with (sentence, similarity_score)
    results = [(sentences_to_compare[i], similarities[0][i]) for i in range(len(sentences_to_compare))]

    # Sort the results by similarity score in descending order
    results.sort(key=lambda x: x[1], reverse=True)

    # Print the top 10 similarity scores and their corresponding sentences
    print("Top 10 Similarity Scores:")
    for i, (sentence, similarity) in enumerate(results[:10]):
        print(f"{i + 1}. Sentence: {sentence}, Similarity Score: {similarity:.4f}")

    # Extract top 10 frame numbers
    top_10_frames = [result[0].split()[-1] for result in results[:10]]

    # Prepare 1-second clips for each frame
    clips = []
    for frame_number in top_10_frames:
        start_time = max(int(frame_number) - 1, 0)  # Start 1 second before the frame
        end_time = min(int(frame_number) + 1, len(frame_captions) - 1)  # End 1 second after the frame
        clip = VideoFileClip(video_path).subclip(start_time, end_time)
        clips.append(clip)

    # Concatenate all clips
    final_clip = concatenate_videoclips(clips)

    # Write the final clip to an MP4 file
    final_clip.write_videofile("visualapp/static/preview.mp4", codec='libx264', audio_codec='aac')

    # Close the clips
    final_clip.close()