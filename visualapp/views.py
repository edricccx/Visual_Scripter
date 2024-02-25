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

@csrf_exempt
def upload_video(request):
    if request.method == 'POST' and request.FILES.get('videoFile'):
        video_file = request.FILES['videoFile']

        # Specify the destination file path
        destination_path = 'visualapp/static/movie.mp4'

        # Open the destination file in binary write mode and write chunks to it
        try:
            with open(destination_path, 'wb') as destination:
                for chunk in video_file.chunks():
                    destination.write(chunk)

            return JsonResponse({'message': 'File uploaded successfully!'})

        except Exception as e:
            return JsonResponse({'error': f'Error uploading file: {str(e)}'})

    return JsonResponse({'error': 'Invalid request'})


def index(request):
    return render(request, 'visualapp/index.html')


    # Serve the audio file for download
    
def convert_to_mp3(request):
    # Load the mp4 file
    video = VideoFileClip("visualapp/static/movie.mp4")

    # Extract audio from video
    video.audio.write_audiofile("visualapp/static/movie.wav")

    return redirect('index')

def execute_script(request):
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

        return render(request, 'visualapp/index.html', {'transcripts': formatted_transcripts})
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}",status=500)