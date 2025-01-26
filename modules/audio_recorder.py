import pyaudio
import numpy as np
import wave
import logging

from config import CHANNELS, SAMPLE_RATE, CHUNK_SIZE

logger = logging.getLogger(__name__)

FORMAT = pyaudio.paInt16

# Set up the microphone
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=1024)

def save_audio(frames, filename):
    """Save the recorded frames as a .wav file."""
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b''.join(frames))
    logger.info(f"Audio saved to {filename}")
    return filename


def record_audio():
    """Record audio when speech is detected, stop when it ends."""
    frames = []
    recording = False
    audio_file_path = None
    logger.info(f"Listening...")
    while True:
        # Read data from the microphone
        data = np.frombuffer(stream.read(CHUNK_SIZE), dtype=np.int16)

        # Calculate the energy (loudness) of the audio data
        energy = np.sum(np.abs(data)) / len(data)

        # If energy exceeds the threshold, start recording
        if energy > 1 and not recording:
            logger.info("Speech detected! Start recording...")
            recording = True
            frames = []  # Clear previous frames
        elif energy < 1 and recording:
            # Stop recording when speech ends
            logger.info("No speech detected. Stopping recording...")
            audio_file_path = save_audio(frames, 'temp_recording.wav')  # Save recorded audio
            break  # Exit the loop after saving

        if recording:
            # Append the audio data to the frames while recording
            frames.append(data.tobytes())

    return audio_file_path  # Return the path to the saved WAV file