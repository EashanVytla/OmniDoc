from openai import OpenAI
import json

# Function to transcribe audio using OpenAI's Whisper API
def transcribe_audio(file_path, openai_key, output_text_file, output_json_file):
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

        # Save the transcribed text to the specified output file
        with open(output_text_file, "w") as text_file:
            text_file.write(transcribed_text)

        print(f"Transcription saved to {output_text_file}")

        # Convert transcription object to dictionary and save it as JSON
        transcription_dict = transcription.__dict__
        with open(output_json_file, "w") as json_file:
            json.dump(transcription_dict, json_file, indent=4)

        print(f"Full JSON response saved to {output_json_file}")

        return transcribed_text

    except Exception as e:
        print(f"Error during transcription: {e}")
        return None
