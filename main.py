import atexit
from modules.ollama_server import start_ollama_server
from modules.audio_recorder import record_audio
from modules.stt import transcribe_audio
from modules.tts import speak_text
from modules.ollama_client import generate_response
from modules.memory import update_short_term_memory, memory_on_exit
import torch
import logging

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

        response = generate_response(user_input)
        print(f"LLM: {response}")
        # for chunk in response:
        #     print(f"LLM: {chunk['message']['content']}", end='', flush=True)
        speak_text(response)

    memory_on_exit()


if __name__ == "__main__":
    main()
