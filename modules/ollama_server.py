import subprocess
import psutil
import ollama
from config import MODEL_BASE, MODEL_SUMMARY
import logging
logger = logging.getLogger(__name__)

def is_ollama_running():
    for process in psutil.process_iter(['name']):
        if 'ollama' in process.info['name'].lower():
            return True
    return False

def start_ollama_server():
    pull_model(MODEL_BASE)
    pull_model(MODEL_SUMMARY)
    if not is_ollama_running():
        logger.info("Starting Ollama server...")
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)

def pull_model(modelname):
    logger.info(f"Pulling Ollama model {modelname}")
    subprocess.run(["ollama", "pull", modelname], shell=True, text=True)