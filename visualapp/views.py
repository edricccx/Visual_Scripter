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
import subprocess


def index(request):
    return render(request, 'visualapp/index.html')


    # Serve the audio file for download
    
def convert_to_mp3(request):
    # Load the mp4 file
    video = VideoFileClip("visualapp/static/movie.mp4")

    # Extract audio from video
    video.audio.write_audiofile("eventapp/static/movie.wav")

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

        return render(request, 'eventapp/index.html', {'transcripts': formatted_transcripts})
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)
def generate_preview(request):
    script_path = "visualapp/static/preview.py"
    output_path = "eventapp/static/movie.mp4"

    # Open a subprocess and capture its output in real-time
    process = subprocess.Popen(['python', script_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

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
from .utils import translate_text

def translate(request):
    if request.method == "POST":
        input_text = request.POST.get("input-text")
        target_lang = request.POST.get("target-language")
        translated_text = translate_text(input_text, target_lang)  # Corrected function name
        return HttpResponse(translated_text)
    return render(request, "visualapp/translate.html")

