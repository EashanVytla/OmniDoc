import os

from dotenv import load_dotenv
from voice_to_wav import get_voice_to_wav
from wav_interpreter import transcribe_audio

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key
openai_key = os.getenv('OPENAI_API_KEY')

print(openai_key)

wav_file = "data/output.wav"

get_voice_to_wav(wav_file, silence_duration=1.5)

output_file = "data/output_transcription.txt"
output_json_file = "data/output_transcription.json"

transcribed_text = transcribe_audio(
    wav_file, 
    openai_key, 
    output_file,
    output_json_file
)

print(transcribed_text)
