import pyaudio
import wave
# import webrtcvad

def get_voice_to_wav(filename="output.wav", silence_duration=1.5):
    """
    Record audio from the microphone and save it as a WAV file using Voice Activity Detection (VAD).

    Args:
        filename (str): The name of the output WAV file.
        silence_duration (float): Duration of silence in seconds to stop recording.
    """
    # Parameters
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 320  # 20 ms chunk size (16000 Hz * 0.02 seconds)

    # Initialize PyAudio and WebRTC Voice Activity Detection (VAD)
    audio = pyaudio.PyAudio()
    vad = webrtcvad.Vad()
    vad.set_mode(1)  # Set aggressiveness: 0 (least), 3 (most aggressive)

    # Start Recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    print("Recording...")

    frames = []
    silent_chunks = 0
    silence_chunk_threshold = int(silence_duration * (RATE / CHUNK))

    while True:
        data = stream.read(CHUNK)
        frames.append(data)

        # Use the webrtcvad library to check for speech
        is_speech = vad.is_speech(data, RATE)

        if not is_speech:
            silent_chunks += 1
        else:
            silent_chunks = 0  # Reset if speech is detected

        # Stop recording after a period of continuous silence
        if silent_chunks > silence_chunk_threshold:
            print("Detected silence, stopping recording.")
            break

    print("Recording finished.")

    # Stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save as WAV file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    print(f"Audio saved as {filename}")
