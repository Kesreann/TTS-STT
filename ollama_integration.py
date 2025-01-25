import ollama
import numpy as np
import queue
import tempfile
import os
import sounddevice as sd
from scipy.io import wavfile
from faster_whisper import WhisperModel
from TTS.api import TTS
from scipy.io.wavfile import write
import subprocess
import psutil
import threading
from scipy.io import wavfile as wav
import time
import re

from config import LONG_TERM_MEMORY
from modules.memory import load_memory

# STT Model (Whisper)
whisper_model = WhisperModel("small", compute_type="int8")

# TTS Model (TTS)
tts_model = TTS("tts_models/en/jenny/jenny")

# Audio recording parameters
SAMPLE_RATE = 16000
CHANNELS = 1
BLOCKSIZE = 1024
RECORD_SECONDS = 6  # Max recording duration

# LLM parameters
MODEL = "luna"
# MODEL = "mistral"

# Queue for audio data
audio_queue = queue.Queue()


def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    audio_queue.put(indata.copy())


def record_audio():
    """Records audio and returns the file path of the recorded WAV file."""
    temp_wav = tempfile.mktemp(suffix=".wav")
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=audio_callback, blocksize=BLOCKSIZE):
        print("Listening...")
        audio_data = []
        for _ in range(0, int(SAMPLE_RATE / BLOCKSIZE * RECORD_SECONDS)):
            data = audio_queue.get()
            audio_data.append(data)
        print("Processing...")

    if not audio_data:
        print("No audio data recorded.")
        return None  # Return None if no data was captured

    # Save the recorded audio as a proper WAV file
    audio_array = np.concatenate(audio_data, axis=0)
    audio_array = (audio_array * 32767).astype(np.int16)  # Convert to 16-bit PCM
    write(temp_wav, SAMPLE_RATE, audio_array)  # Save with scipy.io.wavfile

    return temp_wav


def transcribe_audio(audio_path):
    """Converts speech to text using Whisper."""
    segments, _ = whisper_model.transcribe(audio_path, language="en")
    text = " ".join(segment.text for segment in segments)
    return text.strip()


def generate_response(prompt):
    """Generates a response using Ollama."""
    response = ollama.chat(model=MODEL, messages=[{"role": "system", "content": load_memory(LONG_TERM_MEMORY)}, {"role": "user", "content": prompt}])
    response_content = response['message']['content']

    match = re.match(r"^\[<(.*?)>\]\s*(.*)", response_content)
    cleaned_response_content = ""
    if match:
        emotion = match.group(1)  # Content inside the first set of brackets
        cleaned_response_content = match.group(2)  # The rest of the prompt after the first [<something>]
    else:
        emotion = None
        cleaned_response_content = response_content
    return cleaned_response_content


# def speak_text(text):
#     """Converts text to speech using TTS and plays it back."""
#     # Join the sentences into one string (if needed)
#     if isinstance(text, list):
#         text = " ".join(text)
#
#     output_wav = "response.wav"
#     tts_model.tts_to_file(text, file_path=output_wav)
#
#     # Load the WAV file using scipy.io.wavfile and play it using sounddevice
#     samplerate, data = wav.read(output_wav)
#     sd.play(data, samplerate)
#     sd.wait()  # Wait until the audio has finished playing

def speak_text(text):
    """Converts text to speech using TTS and plays it back."""
    # Start measuring total execution time
    start_time = time.time()

    # Join the sentences into one string (if needed)
    if isinstance(text, list):
        text = " ".join(text)

    # Timing the TTS file generation
    tts_start_time = time.time()
    output_wav = "response.wav"
    tts_model.tts_to_file(text, file_path=output_wav)
    tts_end_time = time.time()

    # Print the time taken to generate the TTS file
    print(f"TTS file generation took {tts_end_time - tts_start_time:.4f} seconds")

    # Timing the WAV file loading and playing
    play_start_time = time.time()
    samplerate, data = wavfile.read(output_wav)
    sd.play(data, samplerate)
    sd.wait()  # Wait until the audio has finished playing
    play_end_time = time.time()

    # Print the time taken to load and play the WAV file
    print(f"Audio playback took {play_end_time - play_start_time:.4f} seconds")

    # Print the total execution time
    total_end_time = time.time()
    print(f"Total execution time: {total_end_time - start_time:.4f} seconds")


def is_ollama_running():
    # Check if Ollama process is running
    for process in psutil.process_iter(['pid', 'name']):
        if 'ollama' in process.info['name'].lower():
            return True
    return False


def start_ollama_server():
    print(f"Pulling ollama Model {MODEL}")
    subprocess.run(["ollama", "pull", MODEL], shell=True, text=True)
    if not is_ollama_running():
        print("Ollama server is not running. Starting the server...")
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        print("Ollama server is already running.")


def main():
    start_ollama_server()
    while True:
        print("Say something...")
        audio_path = record_audio()

        # Check if audio was successfully recorded
        if audio_path is None:
            print("No audio captured, retrying...")
            continue

        user_input = transcribe_audio(audio_path)
        print(f"You said: {user_input}")

        if user_input:
            response = generate_response(user_input)
            print(f"LLM: {response}")
            speak_text(response)
        else:
            print("No speech detected, please try again.")

if __name__ == "__main__":
    main()
