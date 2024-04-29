from transformers import pipeline
from youtube_transcript_api import YouTubeTranscriptApi

# Load the Hugging Face summarization pipeline
summarization_pipeline = pipeline("summarization", model="google/pegasus-large")

def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([i["text"] for i in transcript_text])
        return transcript
    except Exception as e:
        raise e

def generate_summary(transcript_text, max_tokens=1024):
    # Split the input text into chunks
    chunk_size = max_tokens // 2  # Adjust this value as needed
    chunks = [transcript_text[i:i+chunk_size] for i in range(0, len(transcript_text), chunk_size)]

    # Generate summaries for each chunk
    summaries = []
    for chunk in chunks:
        input_length = len(chunk.split())
        max_length = int(input_length * 0.5)  # Adjust the ratio as needed
        summary = summarization_pipeline(chunk, max_length=max_length, min_length=max_length // 4, do_sample=False, truncation=True)[0]["summary_text"]
        summaries.append(summary)

    # Combine the summaries
    final_summary = " ".join(summaries)
    return final_summary