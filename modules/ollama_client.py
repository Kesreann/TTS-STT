import ollama
import re

import pyautogui

from config import MODEL_BASE, SHORT_TERM_MEMORY, SYSTEM_PROMPT, VISION_ENABLED, KEY_MEMORY
from modules.memory import load_memory_on_start, load_memory, update_short_term_memory
from utils.string_utils import remove_emojis
import logging as logger
from datetime import datetime

def generate_response(prompt):
    memory_context = load_memory_on_start() or []
    short_term = load_memory(SHORT_TERM_MEMORY, as_list=True)
    key_memories = load_memory(KEY_MEMORY, as_list=True)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": "".join(memory_context)},
        {"role": "system", "content": "".join(key_memories)},
        {"role": "system", "content": datetime.now().strftime("Current date and time: %Y-%m-%d %H:%M:%S")},
    ]

    for msg in short_term:
        msg = msg.strip()
        if msg:
            role, content = ("user", msg[6:]) if msg.startswith("user:") else ("assistant", msg[5:])
            messages.append({"role": role, "content": content.strip()})



    logger.debug(f"is Vision enabled? {VISION_ENABLED}")
    if VISION_ENABLED:
        # Add screenshot
        screenshot = pyautogui.screenshot()
        screenshot.save("vision/screenshot.png")
        messages.append({"role": "system", "content": "", "images": ["vision/screenshot.png"]})


    logger.info("Ollama Thinking...")
    logger.debug(f"Message Object sent to Ollama: {messages}")

    response = ollama.chat(model=MODEL_BASE, messages=messages, stream=True)

    logger.info("Ollama Thinking done")

    return response
