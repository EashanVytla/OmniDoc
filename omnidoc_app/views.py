from django.shortcuts import render
from django.http import JsonResponse
import subprocess
import platform

from omnidoc_app.models import Patient, Session, Report
import socket
from omnidoc_app.models import Patient
from .voice_control.voice_to_wav import get_voice_to_wav
from .voice_control.wav_interpreter import transcribe_audio
import requests
from django.views.decorators.csrf import csrf_exempt
from . import llm_chat
import json

from django.http import JsonResponse
from .voice_control.voice_to_wav import get_voice_to_wav
from .voice_control.wav_interpreter import transcribe_audio
from dotenv import load_dotenv
import os
from django.shortcuts import get_object_or_404, render
from django.http import Http404
from .models import Session

def main_view(request, session_id=None):
    if session_id is None:
        return render(request, 'session_not_found.html', status=404)

    session = get_object_or_404(Session, id=session_id)
    return render(request, 'session.html', {'session': session})

@csrf_exempt
def send_to_llm(transcribed):
    url = f"{os.getenv('ROOT_URL')}receive-data/"
    data = {'transcription': transcribed}
    response = requests.post(url, json=data, verify=False)
    return response.json()

@csrf_exempt
def start_recording(request, session_id):
    if request.method == 'POST':
        # Define the file paths
        wav_file = "./output.wav"
        output_file = "./output_transcription.txt"
        output_json_file = "./output_transcription.json"

        # Start recording audio and save to file
        get_voice_to_wav(wav_file, silence_duration=1.5)

        load_dotenv()
        # Transcribe the audio
        openai_key = os.getenv('OPENAI_API_KEY')
        transcribed_text = transcribe_audio(
            wav_file,
            openai_key,
            output_file,
            output_json_file
        )

        data = json.loads(request.body)
        state = data.get("state", "")
        traj = data.get("traj", "")

        if not state:
            state = ""

        if not traj:
            traj = ""

        json_res = llm_chat.receive_data(transcribed_text, state, traj)

        try:
            system = platform.system().lower()
            audio_file = os.path.abspath('speech.mp3')
            
            if system in ['darwin', 'linux']:  # macOS or Linux
                subprocess.run(['afplay', audio_file], check=True)
            else:  # Windows
                from .voice_control.audio_player import play_audio
                play_audio(audio_file)
        except Exception as e:
            print(f"Error playing audio: {e}")

        if json_res["state"] == 1:
            try:
                # Find the existing session
                session = Session.objects.get(id=session_id)
                # Update the session data
                session.session_data = json_res["json"]
                session.save()
                return JsonResponse({"question": "You have completed the screening. Thank you for your time!"})
            except Session.DoesNotExist:
                return JsonResponse({'error': 'Session not found'}, status=404)
        
        return JsonResponse(json_res)
        # return JsonResponse({'transcription': transcribed_text})

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def doctor_patient_list_view(request):
    # Query all Patient models
    patients = Patient.objects.all()

    # Render the template and pass the patient list to the context
    return render(request, 'patient_list.html', {'patients': patients})

def doctor_session_view(request, patient_id):
    patient = Patient.objects.get(pk=patient_id)
    sessions = Session.objects.filter(patient=patient)
    return render(request, 'session_list.html', {'sessions': sessions})

def doctor_session_detail(request, patient_id, session_id):
    session = Session.objects.get(pk=session_id)  # Single session
    patient = Patient.objects.get(pk=patient_id)
    reports = Report.objects.filter(session=session)  # Reports are not currently being used in the template
    return render(request, 'session_detail.html', {'session': session, 'patient': patient})
