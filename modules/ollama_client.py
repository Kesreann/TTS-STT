import ollama
import re

import pyautogui

from config import MODEL_BASE, SHORT_TERM_MEMORY, SYSTEM_PROMPT, VISION_ENABLED, KEY_MEMORY
from modules.memory import load_memory_on_start, load_memory, update_short_term_memory
from utils.string_utils import remove_emojis


def generate_response(prompt):
    memory_context = load_memory_on_start() or []
    short_term = load_memory(SHORT_TERM_MEMORY, as_list=True)
    key_memories = load_memory(KEY_MEMORY, as_list=True)

    messages = [{"role": "system", "content": "".join(memory_context)},
                {"role": "system", "content": "".join(key_memories)}]  # Add memory_context first

    for msg in short_term:
        msg = msg.strip()
        if msg:
            role, content = ("user", msg[6:]) if msg.startswith("user:") else ("assistant", msg[5:])
            messages.append({"role": role, "content": content.strip()})

    messages.append({"role": "system", "content": SYSTEM_PROMPT})
    messages.append({"role": "user", "content": prompt})

    print(f"is Vision enabled? {VISION_ENABLED}")
    if VISION_ENABLED:
        # Add screenshot
        screenshot = pyautogui.screenshot()
        screenshot.save("screenshot.png")
        messages.append({"role": "system", "content": "", "images": ["screenshot.png"]})

    response = ollama.chat(model=MODEL_BASE, messages=messages)
    reply = response.get('message', {}).get('content', '').strip()
    reply = remove_emojis(reply)

    update_short_term_memory("You", reply)
    return reply
