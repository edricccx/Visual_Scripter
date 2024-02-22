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


def index(request):
    return render(request, 'visualapp/index.html')


    # Serve the audio file for download
    
def convert_to_mp3(request):
    # Load the mp4 file
    video = VideoFileClip("visualapp/static/panda.mp4")

    # Extract audio from video
    video.audio.write_audiofile("visualapp/static/finallynoo.wav")

    return redirect('index')

def execute_script(request):
    # Load model
    processor = WhisperProcessor.from_pretrained("openai/whisper-base.en")
    model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-base.en")

    # Load audio file
    audio_file = os.path.join(settings.BASE_DIR, 'visualapp', 'static', 'audio.wav')

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
        for i, (time, transcript_list) in enumerate(zip(times, transcripts)):
            for sentence in transcript_list[0].split('.'):
                sentence = sentence.strip()
                if sentence:
                    formatted_transcripts.append(f"{time}s: {sentence}")

        return render(request, 'visualapp/index.html', {'transcripts': formatted_transcripts})
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)
