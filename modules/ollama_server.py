import subprocess
import psutil
import ollama
from config import MODEL_BASE

def is_ollama_running():
    for process in psutil.process_iter(['name']):
        if 'ollama' in process.info['name'].lower():
            return True
    return False

def start_ollama_server():
    print(f"Pulling Ollama model {MODEL_BASE}")
    subprocess.run(["ollama", "pull", MODEL_BASE], shell=True, text=True)
    if not is_ollama_running():
        print("Starting Ollama server...")
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
