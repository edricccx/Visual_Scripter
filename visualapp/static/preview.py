import os
from django.conf import settings
from moviepy.editor import VideoFileClip, concatenate_videoclips
from langchain import LLMChain, PromptTemplate
from langchain.llms import OllaMa
from django.http import HttpResponse

def load_srt_file(srt_file_path):
    with open(srt_file_path, 'r', encoding='utf-8') as f:
        srt_content = f.read()

    captions = []
    for entry in srt_content.split('\n\n'):
        lines = entry.strip().split('\n')
        if lines:
            start_time, end_time = lines[1].split(' --> ')
            caption = ' '.join(lines[2:])
            captions.append((start_time, end_time, caption))

    return captions

def generate_preview(request):
    srt_file_path = os.path.join(settings.STATIC_ROOT, 'transcript.srt')
    video_path = os.path.join(settings.STATIC_ROOT, 'movie.mp4')

    # Load the SRT file
    captions = load_srt_file(srt_file_path)

    # Load the OllaMa model
    llm = OllaMa()

    # Define the prompt template
    prompt_template = PromptTemplate(
        input_variables=["input_text"],
        template="Summarize the following text: {input_text}",
    )

    # Create the LLMChain
    llm_chain = LLMChain(llm=llm, prompt=prompt_template)

    # Generate summaries for the captions
    summaries = []
    for _, _, caption in captions:
        summary = llm_chain.run(caption)
        summaries.append(summary)

    # Extract top 10 captions based on summary lengths
    top_10_captions = sorted([(summary, i) for i, summary in enumerate(summaries)], key=lambda x: len(x[0]), reverse=True)[:10]
    top_10_indices = [caption[1] for caption in top_10_captions]

    # Prepare clips for the top 10 captions
    clips = []
    video = VideoFileClip(video_path)
    for index in top_10_indices:
        start_time, end_time, _ = captions[index]
        start_time = sum(map(float, start_time.split(':')))
        end_time = sum(map(float, end_time.split(':')))
        clip = video.subclip(start_time, end_time)
        clips.append(clip)

    # Concatenate all clips
    final_clip = concatenate_videoclips(clips)

    # Write the final clip to an MP4 file
    preview_file_path = os.path.join(settings.STATIC_ROOT, 'preview.mp4')
    final_clip.write_videofile(preview_file_path, codec='libx264')

    # Close the clips
    final_clip.close()
    video.close()

    return HttpResponse('Preview generated successfully')