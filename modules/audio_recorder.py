# import queue
# import tempfile
# import numpy as np
# import sounddevice as sd
# from scipy.io.wavfile import write
# from config import SAMPLE_RATE, CHANNELS, BLOCKSIZE, RECORD_SECONDS
#
# audio_queue = queue.Queue()
#
#
# def audio_callback(indata, frames, time, status):
#     if status:
#         print(status)
#     audio_queue.put(indata.copy())
#
#
# def record_audio():
#     temp_wav = tempfile.mktemp(suffix=".wav")
#     with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=audio_callback, blocksize=BLOCKSIZE):
#         print("Listening...")
#         audio_data = [audio_queue.get() for _ in range(int(SAMPLE_RATE / BLOCKSIZE * RECORD_SECONDS))]
#
#     if not audio_data:
#         print("No audio recorded.")
#         return None
#
#     audio_array = np.concatenate(audio_data, axis=0)
#     audio_array = (audio_array * 32767).astype(np.int16)
#     write(temp_wav, SAMPLE_RATE, audio_array)
#     return temp_wav


import pyaudio
import numpy as np
import wave

# Set up the microphone
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=1024)

# Define parameters for audio recording
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK_SIZE = 1024

def save_audio(frames, filename):
    """Save the recorded frames as a .wav file."""
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    print(f"Audio saved to {filename}")
    return filename


def record_audio():
    """Record audio when speech is detected, stop when it ends."""
    frames = []
    recording = False
    audio_file_path = None
    print("Listening...")
    while True:
        # Read data from the microphone
        data = np.frombuffer(stream.read(CHUNK_SIZE), dtype=np.int16)

        # Calculate the energy (loudness) of the audio data
        energy = np.sum(np.abs(data)) / len(data)

        # If energy exceeds the threshold, start recording
        if energy > 1 and not recording:
            print("Speech detected! Start recording...")
            recording = True
            frames = []  # Clear previous frames
        elif energy < 1 and recording:
            # Stop recording when speech ends
            print("No speech detected. Stopping recording...")
            audio_file_path = save_audio(frames, 'temp_recording.wav')  # Save recorded audio
            recording = False
            frames = []  # Clear frames for next recording
            break  # Exit the loop after saving

        if recording:
            # Append the audio data to the frames while recording
            frames.append(data.tobytes())

    return audio_file_path  # Return the path to the saved WAV file