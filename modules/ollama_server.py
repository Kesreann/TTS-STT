import subprocess
from concurrent.futures import ThreadPoolExecutor

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
    if not is_ollama_running():
        logger.info("Starting Ollama server...")
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)

    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(pull_model, MODEL_BASE)
        executor.submit(pull_model, MODEL_SUMMARY)

def pull_model(modelname):
    logger.info(f"Pulling Ollama model {modelname}")
    subprocess.run(["ollama", "pull", modelname], shell=True, text=True)