from openai import OpenAI
import json
import os
import platform

# Function to transcribe audio using OpenAI's Whisper API
def transcribe_audio(file_path, openai_key, output_text_file, output_json_file):
    # Convert to proper path format for the current OS
    file_path = os.path.normpath(file_path)
    output_text_file = os.path.normpath(output_text_file)
    output_json_file = os.path.normpath(output_json_file)

    # Check file accessibility
    if not os.path.exists(file_path):
        print(f"Error: Audio file not found at {file_path}")
        return None

    # Initialize the OpenAI client with your API key
    client = OpenAI(api_key=openai_key)

    try:
        # Load the audio file
        with open(file_path, "rb") as audio_file:
            # Send the audio file to the Whisper API for transcription
            transcription = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )

        # Extract the transcribed text
        transcribed_text = transcription.text

        # Save the transcribed text using UTF-8 encoding
        with open(output_text_file, "w", encoding='utf-8') as text_file:
            text_file.write(transcribed_text)

        print(f"Transcription saved to {output_text_file}")

        # Convert transcription object to dictionary and save it as JSON with UTF-8 encoding
        transcription_dict = transcription.__dict__
        with open(output_json_file, "w", encoding='utf-8') as json_file:
            json.dump(transcription_dict, json_file, indent=4, ensure_ascii=False)

        print(f"Full JSON response saved to {output_json_file}")

        return transcribed_text

    except PermissionError as pe:
        print(f"Permission error accessing files: {pe}")
        return None
    except UnicodeEncodeError as ue:
        print(f"Character encoding error: {ue}")
        # Fallback to ASCII encoding if UTF-8 fails
        with open(output_text_file, "w", encoding='ascii', errors='ignore') as text_file:
            text_file.write(transcribed_text)
        return transcribed_text
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None
