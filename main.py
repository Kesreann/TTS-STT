import atexit
from modules.ollama_server import start_ollama_server
from modules.audio_recorder import record_audio
from modules.stt import transcribe_audio
from modules.tts import speak_text, setup_tts
from modules.ollama_client import generate_response
from modules.memory import update_short_term_memory, memory_on_exit
import torch
import logging

from utils.string_utils import remove_emojis

# Set up the logger
logging.basicConfig(
    level=logging.INFO,  # Set the default log level
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
    print()

    start_ollama_server()
    # flush_short_term_memory()
    # load_long_term_into_session()

    while True:
        # ######################################
        #   USER
        # ######################################

        audio_path = record_audio()
        if not audio_path:
            print("No audio captured, retrying...")
            continue

        user_input = transcribe_audio(audio_path)
        if not user_input:
            print("Invalid input, try again.")
            continue

        print(f"You said: {user_input}")
        if user_input.lower() == "exit." or user_input.lower() == "done":
            print("User wants to end the conversation")
            break

        if len(user_input.split(" ")) < 2:  # Correct placement of parentheses
            print("One word detected. Skipping")
            continue
        if user_input == "Thank you.":
            continue

        update_short_term_memory("user", user_input)

        # ######################################
        #   LLM
        # ######################################

        response = generate_response(user_input)
        full_message = ""
        for chunk in response:
            # Extract the content from the chunk and feed it to TTS
            message_content = chunk['message']['content']
            message_content = remove_emojis(message_content)
            print(message_content, end='', flush=True)  # Print the content (optional)
            full_message = full_message + message_content

            # Call the TTS function to speak the message content
            speak_text(chunk)
        update_short_term_memory("You", full_message)
    memory_on_exit()


if __name__ == "__main__":
    setup_tts()
    main()
