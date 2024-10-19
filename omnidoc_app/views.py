from django.shortcuts import render
from django.http import JsonResponse
import subprocess

from omnidoc_app.models import Patient


def main_view(request):
    return render(request, 'main.html')  

from django.http import JsonResponse
from .voice_control.voice_to_wav import get_voice_to_wav
from .voice_control.wav_interpreter import transcribe_audio
import os

def start_recording(request):
    if request.method == 'POST':
        # Define the file paths
        wav_file = "data/output.wav"
        output_file = "data/output_transcription.txt"
        output_json_file = "data/output_transcription.json"

        # Start recording audio and save to file
        get_voice_to_wav(wav_file, silence_duration=1.5)

        # Transcribe the audio
        openai_key = os.getenv('OPENAI_API_KEY')
        transcribed_text = transcribe_audio(
            wav_file,
            openai_key,
            output_file,
            output_json_file
        )

        # Return the transcription as a response
        return JsonResponse({'transcription': transcribed_text})

    return JsonResponse({'error': 'Invalid request method'}, status=400)



def doctor_patient_list_view(request):
    # Query all Patient models
    patients = Patient.objects.all()

    # Render the template and pass the patient list to the context
    return render(request, 'patient_list.html', {'patients': patients})