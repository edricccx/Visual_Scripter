from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import os
import subprocess
import json
from moviepy.editor import VideoFileClip
import librosa
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from .youtube import extract_transcript_details, generate_summary





def upload_video(request):
    if request.method == 'POST' and request.FILES.get('file'):
        video_file = request.FILES['file']
        file_path = os.path.join(settings.BASE_DIR, 'visualapp', 'static', 'movie.mp4')

        # Save the uploaded file
        with open(file_path, 'wb') as destination:
            for chunk in video_file.chunks():
                destination.write(chunk)

        return JsonResponse({'message': 'File uploaded successfully!'})
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

def play_video(request):
    file_path = os.path.join(settings.BASE_DIR, 'visualapp', 'static', 'movie.mp4')
    if os.path.exists(file_path):
        with open(file_path, 'rb') as video_file:
            video_data = video_file.read()
        return HttpResponse(video_data, content_type='video/mp4')
    else:
        return JsonResponse({'error': 'Video file not found'}, status=404)

def convert_to_mp3():
    # Load the mp4 file
    video = VideoFileClip(os.path.join(settings.BASE_DIR, 'visualapp', 'static', 'movie.mp4'))

    # Extract audio from video
    video.audio.write_audiofile(os.path.join(settings.BASE_DIR, 'visualapp', 'static', 'movie.wav'))

    return redirect('index')

def execute_script(request):
    # Call convert_to_mp3 function
    convert_to_mp3()
    # Load model
    processor = WhisperProcessor.from_pretrained("openai/whisper-base.en")
    model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-base.en")

    # Load audio file
    audio_file = os.path.join(settings.BASE_DIR, 'visualapp', 'static', 'movie.wav')

    # Check if the audio file exists
    if not os.path.exists(audio_file):
        return HttpResponse("Audio file not found", status=404)

    try:
        # Load audio waveform and rate
        waveform, rate = librosa.load(audio_file, sr=16000) 

        # Split audio into 5s chunks
        chunk_length = 5 * rate  
        chunks = [waveform[i:i+chunk_length] for i in range(0, len(waveform), chunk_length)]
        times = [i*5 for i in range(len(chunks))]

        # Transcribe each chunk
        transcripts = []
        for chunk in chunks:
            input_features = processor(chunk, sampling_rate=16000, return_tensors="pt").input_features   
            predicted_ids = model.generate(input_features)
            transcript = processor.batch_decode(predicted_ids)
            transcripts.append(transcript)

        # Construct response with formatted transcripts and timing
        formatted_transcripts = []
        for i, transcript in enumerate(transcripts):
            split_transcript = transcript[0].split("|")
            content = split_transcript[0] if len(split_transcript) > 0 else ""
            formatted_transcripts.append(f"{times[i]}s: {content} ")

        return render(request, 'visualapp/sum.html', {'transcripts': formatted_transcripts})
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)

def generate_preview(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            reference_sentence = data.get('referenceSentence', '')
        except json.JSONDecodeError:
            return HttpResponse("Invalid request data", status=400)

        script_path = os.path.join(settings.BASE_DIR, 'visualapp', 'static', 'preview.py')
        output_path = os.path.join(settings.BASE_DIR, 'visualapp', 'static', 'preview.mp4')

        # Open a subprocess and capture its output in real-time
        process = subprocess.Popen(['python', script_path, reference_sentence], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

        # Print the output in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())

        # Wait for the process to complete
        process.wait()

        # Check the process return code
        if process.returncode == 0:
            # Load the generated preview file
            with open(output_path, 'rb') as f:
                preview = f.read()

            # Delete the preview file after loading
            os.remove(output_path)

            return HttpResponse(preview, content_type='video/mp4')
        else:
            return HttpResponse("Preview generation failed", status=500)
    else:
        return render(request, 'prev.html')

def translate(request):
    if request.method == "POST":
        input_text = request.POST.get("input-text")
        target_lang = request.POST.get("target-language")
        translated_text = translate_text(input_text, target_lang)  # Corrected function name
        return HttpResponse(translated_text)
    return render(request, "visualapp/translate.html")

def youtube_transcripter(request):
    if request.method == 'POST':
        youtube_link = request.POST.get('youtube_link')
        if youtube_link:
            try:
                transcript_text = extract_transcript_details(youtube_link)
                if transcript_text:
                    summary = generate_summary(transcript_text, max_tokens=1024)  # Pass max_tokens as an integer
                    context = {'summary': summary}
                    return render(request, 'visualapp/youtube_transcripter.html', context)
            except Exception as e:
                context = {'error': str(e)}
                return render(request, 'visualapp/youtube_transcripter.html', context)
    return render(request, 'visualapp/youtube_transcripter.html')

def index(request):
    return render(request, 'visualapp/index.html')

def sum(request):
    return render(request, 'visualapp/sum.html')

def prev(request):
    return render(request, 'visualapp/prev.html')

def generate_srt(request):
    # Your code for generating SRT file goes here
    pass

def format_time(seconds):
    # Your code for formatting time goes here
    pass
