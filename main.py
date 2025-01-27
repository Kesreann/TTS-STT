import time
from concurrent.futures import ThreadPoolExecutor

from modules.ollama_server import start_ollama_server
from modules.audio_recorder import record_audio
from modules.stt import transcribe_audio
from modules.tts import speak_text, setup_tts, tts_on_exit, stop_talking
from modules.ollama_client import generate_response
from modules.memory import update_short_term_memory, memory_on_exit
import torch
import logging
from utils.string_utils import remove_emojis

# Set up the logger
logging.basicConfig(
    level=logging.ERROR,  # Set the default log level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    handlers=[
        logging.StreamHandler(),  # Output to console
        logging.FileHandler("conversation_memory.log")  # Optionally log to a file
    ]
)

# Get a logger instance
logger = logging.getLogger(__name__)


def main():
    logger.debug("Using CUDA or CPU? " + "cuda" if torch.cuda.is_available() else "cpu")

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_ollama = executor.submit(start_ollama_server)
        future_tts = executor.submit(setup_tts)

        future_ollama.result()  # Wait for Ollama setup
        future_tts.result()      # Wait for TTS setup

    show_listening_print = True

    while True:
        # ######################################
        #   USER
        # ######################################

        if show_listening_print:
            print("\033[0mListening...")
            show_listening_print = False

        audio_path = record_audio()
        if not audio_path:
            logger.info("No audio captured, retrying...")
            continue

        user_input = transcribe_audio(audio_path)
        if not user_input:
            logger.info("Invalid input, try again.")
            continue

        if user_input.lower().startswith("exit") or user_input.lower() == "done":
            logger.info("User wants to end the conversation")
            print("\033[0mEnding the conversation")
            break

        if user_input.lower() == "stop" or user_input.lower() == "stop.":
            stop_talking()
            continue

        if len(user_input.split(" ")) < 2:  # Correct placement of parentheses
            logger.info("One word detected. Skipping")
            continue

        # no idea why whitenoise is interpreted like that
        if user_input.startswith("Thank you.") or user_input.startswith("Thank you for watching"):
            continue

        logger.info(f"\033[32m You said: {user_input}")
        print(f"You said: {user_input}")
        update_short_term_memory("User", user_input)
        show_listening_print = True

        # ######################################
        #   LLM
        # ######################################

        start_time = time.time()
        response = generate_response(user_input)
        end_time = time.time()
        print(f"got response from lama in: {end_time - start_time:.4f} seconds")

        is_thinking = False
        full_message = ""
        for chunk in response:
            # Extract the content from the chunk and feed it to TTS
            message_content = chunk['message']['content']
            message_content = remove_emojis(message_content)
            full_message = full_message + message_content


            # Remove everything in the <think> tag from deepseek, since we dont want to hear that, but its important from the llm i guess
            if message_content.startswith("</think>"):
                is_thinking = False
                continue

            if message_content.startswith("<think>") or is_thinking:
                is_thinking = True
                continue

            # Call the TTS function to speak the message content
            speak_text(chunk)

        logger.info(f"LLM: {full_message}")
        print(f"\033[93m LLM: {full_message}")
        update_short_term_memory("Assistant", full_message)

    tts_on_exit()
    print("Updating Memory")
    memory_on_exit()


if __name__ == "__main__":
    main()
