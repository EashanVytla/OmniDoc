import os
from dotenv import load_dotenv
from voice_to_wav import get_voice_to_wav
from wav_interpreter import transcribe_audio
import socket

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key
openai_key = os.getenv('OPENAI_API_KEY')

wav_file = "output.wav"

get_voice_to_wav(wav_file, silence_duration=0.5)

output_file = "output_transcription.txt"
output_json_file = "output_transcription.json"

transcribed_text = transcribe_audio(
    wav_file, 
    openai_key, 
    output_file,
    output_json_file
)