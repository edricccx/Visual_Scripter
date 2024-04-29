from django.shortcuts import render
from django.http import HttpResponse
import moviepy
from django.shortcuts import render, redirect
from django.template import TemplateDoesNotExist
from django.http import HttpResponse
from .forms import VideoForm
from moviepy.editor import VideoFileClip
from moviepy.editor import *
import librosa
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration 
import os
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import subprocess
import json

def upload_video(request):
    if request.method == 'POST' and request.FILES.get('file'):
        video_file = request.FILES['file']
        file_path = 'visualapp/static/movie.mp4' 

        # Save the uploaded file
        with open(file_path, 'wb') as destination:
            for chunk in video_file.chunks():
                destination.write(chunk)

        return JsonResponse({'message': 'File uploaded successfully!'})
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
def play_video(request):
    file_path = 'visualapp/static/movie.mp4' 
    if os.path.exists(file_path):
        with open(file_path, 'rb') as video_file:
            video_data = video_file.read()
        return HttpResponse(video_data, content_type='video/mp4')
    else:
        return JsonResponse({'error': 'Video file not found'}, status=404)

def convert_to_mp3():
    # Load the mp4 file
    video = VideoFileClip("visualapp/static/movie.mp4")

    # Extract audio from video
    video.audio.write_audiofile("visualapp/static/movie.wav")

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
        transcripts = []
        formatted_transcripts = []
        for chunk in chunks:
            input_features = processor(chunk, sampling_rate=16000, return_tensors="pt").input_features   
            predicted_ids = model.generate(input_features)
            transcript = processor.batch_decode(predicted_ids)
            transcripts.append(transcript)

        # Construct response with formatted transcripts and timing
        for i, transcript in enumerate(transcripts):
            split_transcript = transcript[0].split("<|startoftranscript|><|notimestamps|>")
            split_transcript2 = split_transcript[1].split("<|endoftext|>")
            cleaned_transcript = split_transcript[0]  # "|startoftranscript|>"

            content = split_transcript2[0] if len(split_transcript) > 1 else ""  # Extract content, or empty string if not present
            print(f"{times[i]}s: {content} ")
            formatted_transcripts.append(f"{times[i]}s: {content} ")

        return render(request, 'visualapp/sum.html', {'transcripts': formatted_transcripts})
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)


def index(request):
    return render(request, 'visualapp/index.html')

def sum(request):
    return render(request, 'visualapp/sum.html')

def prev(request):
    return render(request, 'visualapp/prev.html')

def generate_srt(request):
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

        # Generate SRT content
        srt_content = ""
        counter = 1
        for i, transcript in enumerate(transcripts):
            split_transcript = transcript[0].split("<|startoftranscript|><|notimestamps|>")
            split_transcript2 = split_transcript[1].split("<|endoftranscript|>")
            cleaned_transcript = split_transcript[0]  # "|startoftranscript|>"
            content = split_transcript2[0] if len(split_transcript) > 1 else ""  # Extract content, or empty string if not present
            start_time = times[i]
            end_time = times[i] + 5  # Assuming 5-second chunks

            srt_content += f"{counter}\n{format_time(start_time)} --> {format_time(end_time)}\n{content}\n\n"
            counter += 1

        # Create a file response for download
        response = HttpResponse(srt_content, content_type='text/srt')
        response['Content-Disposition'] = 'attachment; filename="transcript.srt"'
        return response
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def generate_preview(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            reference_sentence = data.get('referenceSentence', '')
        except json.JSONDecodeError:
            return HttpResponse("Invalid request data", status=400)

        script_path = "visualapp/static/backupig.py"
        output_path = "visualapp/static/preview.mp4"

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

from .utils import translate_text

def translate(request):
    if request.method == "POST":
        input_text = request.POST.get("input-text")
        target_lang = request.POST.get("target-language")
        translated_text = translate_text(input_text, target_lang)
        return HttpResponse(translated_text)