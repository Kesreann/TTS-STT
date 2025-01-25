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
import atexit

# STT Model (Whisper)
whisper_model = WhisperModel("small", compute_type="int8")

# TTS Model (TTS)
tts_model = TTS("tts_models/en/jenny/jenny")

# Audio recording parameters
SAMPLE_RATE = 16000
CHANNELS = 1
BLOCKSIZE = 1024
SILENCE_DURATION_THRESHOLD = 2  # Silence duration in seconds to trigger stop
RECORD_SECONDS = 6  # Max recording duration (adjust for continuous recording)

SILENCE_THRESHOLD = 0.01  # Adjust based on sensitivity
SILENCE_DURATION = 2  # How long to wait for silence before stopping

# LLM parameters
MODEL = "luna"
# MODEL = "mistral"
SHORT_TERM_MEMORY = "shortTerm.txt"
LONG_TERM_MEMORY = "deepMemory.txt"


# Queue for audio data
audio_queue = queue.Queue()



def audio_callback(indata, frames, time, status):
    """Callback function to collect audio data."""
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
    text = " ".join(segment.text for segment in segments).strip()  # Join and strip any extra spaces

    return text


def generate_response(prompt):
    """Generates a response using Ollama."""
    response = ollama.chat(model=MODEL, messages=[{"role": "user", "content": prompt}])
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


def speak_text(text):
    """Converts text to speech using TTS and plays it back."""
    # Join the sentences into one string (if needed)
    if isinstance(text, list):
        text = " ".join(text)

    output_wav = "response.wav"
    tts_model.tts_to_file(text, file_path=output_wav)

    # Load the WAV file using scipy.io.wavfile and play it using sounddevice
    samplerate, data = wavfile.read(output_wav)
    sd.play(data, samplerate)
    sd.wait()  # Wait until the audio has finished playing


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


def load_memory(file_path):
    """Load memory from a file if it exists."""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.readlines()
    return []


def save_memory(file_path, data):
    """Save memory to a file."""
    with open(file_path, "w", encoding="utf-8") as file:
        file.writelines(data)


def ollama_summarize(full_conversation):
    """Use Ollama to summarize the entire conversation history."""
    prompt = f"Summarize the following conversation while keeping key details:\n\n{''.join(full_conversation)}"
    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"].split("\n")


def load_long_term_into_session():
    """Load deepMemory into Ollama at the start of the session."""
    long_term_memory = load_memory(LONG_TERM_MEMORY)
    if long_term_memory:
        ollama.chat(model=MODEL, messages=[{"role": "system", "content": "".join(long_term_memory)}])


def update_long_term_memory():
    """On exit, merge short-term and long-term memory, summarize, and update deepMemory."""
    short_term_memory = load_memory(SHORT_TERM_MEMORY)
    long_term_memory = load_memory(LONG_TERM_MEMORY)

    if short_term_memory:
        # Merge both memories
        full_conversation = long_term_memory + short_term_memory

        # Summarize using Ollama
        summarized_content = ollama_summarize(full_conversation)

        # Save summarized conversation as new long-term memory
        save_memory(LONG_TERM_MEMORY, summarized_content)

        # Clear short-term memory
        save_memory(SHORT_TERM_MEMORY, [])


# Register the update function to run on program exit
atexit.register(update_long_term_memory)


def main():
    start_ollama_server()
    load_long_term_into_session()
    while True:
        print("Say something...")

        audio_path = record_audio()

        # Check if audio was successfully recorded
        if audio_path is None:
            print("No audio captured, retrying...")
            continue

        user_input = transcribe_audio(audio_path)

        # If None is returned (because of "Thank you" or empty input), continue the loop
        if user_input is None:
            print("Invalid input (either 'Thank you' or empty input detected), please try again.")
            continue

        print(f"You said: {user_input}")
        with open(SHORT_TERM_MEMORY, "a", encoding="utf-8") as file:
            file.write(f"You: {user_input}\n")

        if user_input.lower() == "quit" or user_input.lower() == "exit":
            break

        # Filter out one-word responses
        if len(user_input.split()) > 1:
            response = generate_response(user_input)
            print(f"LLM: {response}")
            with open(SHORT_TERM_MEMORY, "a", encoding="utf-8") as file:
                file.write(f"You: {response}\n")
            speak_text(response)
        else:
            print("One-word response detected, please try again.")


if __name__ == "__main__":
    main()
