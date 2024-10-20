from django.shortcuts import render
from django.http import JsonResponse
import subprocess
import socket
from omnidoc_app.models import Patient
from .voice_control.voice_to_wav import get_voice_to_wav
from .voice_control.wav_interpreter import transcribe_audio
import os
import requests
from django.views.decorators.csrf import csrf_exempt
from . import llm_chat
import json

def main_view(request):
    return render(request, 'main.html')  

@csrf_exempt
def send_to_llm(transcribed):
    url = "http://localhost:8000/receive-data/"
    data = {'transcription': transcribed}
    response = requests.post(url, json=data, verify=False)
    return response.json()

#send_to_llm("")

@csrf_exempt
def start_recording(request):
    if request.method == 'POST':
        # Define the file paths
        wav_file = "./output.wav"
        output_file = "./output_transcription.txt"
        output_json_file = "./output_transcription.json"

        # Start recording audio and save to file
        get_voice_to_wav(wav_file, silence_duration=0.5)

        # Transcribe the audio
        openai_key = os.getenv('OPENAI_API_KEY')
        transcribed_text = transcribe_audio(
            wav_file,
            openai_key,
            output_file,
            output_json_file
        )

        return JsonResponse(llm_chat.receive_data(transcribed_text))
        # return JsonResponse({'transcription': transcribed_text})

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def doctor_patient_list_view(request):
    # Query all Patient models
    patients = Patient.objects.all()

    # Render the template and pass the patient list to the context
    return render(request, 'patient_list.html', {'patients': patients})