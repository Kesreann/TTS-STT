import os
import re

import ollama
from config import SHORT_TERM_MEMORY, LONG_TERM_MEMORY, MODEL_SUMMARY, SHORT_TERM_LIMIT, MODEL_SUMMARY_SYSTEM_PROMPT, \
    MODEL_SUMMARY_KEY_INFO_SYSTEM_PROMPT, KEY_MEMORY

import logging
from datetime import datetime
import concurrent.futures

logger = logging.getLogger(__name__)

def load_memory(file_path, as_list=True):
    """Loads memory from a file, returning it as a list or a single string."""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.readlines() if as_list else file.read()
    return [] if as_list else ""


def save_memory(file_path, data, as_list=True):
    """Saves memory to a file, handling list or string formats."""
    with open(file_path, "w", encoding="utf-8") as file:
        if as_list:
            file.writelines(data)
        else:
            file.write(data)


def update_short_term_memory(agent, message):
    """Appends new conversation data while maintaining a rolling window."""
    short_term = load_memory(SHORT_TERM_MEMORY)
    short_term.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {agent}: {message}\n")

    # Trim to keep only the last SHORT_TERM_LIMIT exchanges
    if len(short_term) > SHORT_TERM_LIMIT:
        short_term = short_term[-SHORT_TERM_LIMIT:]

    save_memory(SHORT_TERM_MEMORY, short_term)


def summarize_memory(full_conversation):
    """Summarizes the full conversation using the Ollama model."""
    logging.info("Sending convo to ollama to summarize")
    response = ollama.chat(model=MODEL_SUMMARY, messages=[
        {"role": "system", "content": MODEL_SUMMARY_SYSTEM_PROMPT},
        {"role": "user", "content": full_conversation}
    ])
    logging.info(f"Got the response from ollama: {response['message']['content']}")
    return response['message']['content'].strip()


def extract_key_information(full_conversation):
    """Extracts key information from the full conversation."""
    logging.info("Sending convo to ollama for key information extraction")
    response = ollama.chat(model=MODEL_SUMMARY, messages=[
        {"role": "system", "content": MODEL_SUMMARY_KEY_INFO_SYSTEM_PROMPT},
        {"role": "user", "content": full_conversation}
    ])
    logging.debug("Key memory response: " + response['message']['content'])
    return response['message']['content'].strip()


def update_memory_files(summary, key_info, key_memories):
    """Updates the memory files with the new summary and key information."""
    if summary:
        logging.info("Saving summarized memory in file")
        save_memory(LONG_TERM_MEMORY, summary, as_list=False)
        save_memory(SHORT_TERM_MEMORY, "", as_list=False)  # Clear short-term memory

    if key_info:
        logging.info("Saving key memory in file")
        save_memory(KEY_MEMORY, merge_conversations(key_info, key_memories), as_list=False)


def update_long_term_memory():
    """Summarizes short-term memory and appends it to long-term memory reliably."""
    logging.info("Updating Long-term Memory")
    short_term = load_memory(SHORT_TERM_MEMORY, as_list=False).strip()
    long_term = load_memory(LONG_TERM_MEMORY, as_list=False).strip()
    key_memories = load_memory(KEY_MEMORY, as_list=False).strip()
    logger.info("Loaded memory files")

    if not short_term:
        logging.info("No short-term memory to process.")
        return

    full_conversation = f"{long_term}\n\n{short_term}" if long_term else short_term

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_summary = executor.submit(summarize_memory, full_conversation)
        future_key_info = executor.submit(extract_key_information, full_conversation)

        summary = future_summary.result()
        key_info = future_key_info.result()


def load_memory_on_start():
    """Loads long-term memory into the system on startup."""
    return load_memory(LONG_TERM_MEMORY, as_list=False).strip()


def memory_on_exit():
    """Handles memory saving on program exit."""
    logger.info("Memory on exit triggered")
    update_long_term_memory()
    logger.info("Memory update complete")


def merge_conversations(memory_1, memory_2):
    """
    Merges two structured conversation logs while ensuring:
    - Proper formatting is maintained
    - Duplicates are removed
    - Entries stay in order

    Arguments:
    memory_1 -- String representing the first structured memory log.
    memory_2 -- String representing the second structured memory log.

    Returns:
    Merged structured memory as a string.
    """

    # Ensure both inputs are strings, default to empty string if None
    memory_1 = memory_1.strip() if isinstance(memory_1, str) else ""
    memory_2 = memory_2.strip() if isinstance(memory_2, str) else ""
    # Define categories
    categories = ["Personal Preferences", "Important Tasks", "Temporary Tasks"]

    # Function to extract category content
    def extract_category(text, category):
        """Extracts the list under a given category."""
        pattern = rf"\d+\.\s\*\*{re.escape(category)}\*\*:\n(.*?)(?=\n\d+\.\s\*\*|\Z)"  # Stops at next category or end of text
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip().split("\n") if match else []

    # Function to merge two lists while removing duplicates and keeping order
    def merge_lists(list1, list2):
        seen = set()
        merged = []
        for item in list1 + list2:
            item = item.strip()
            if item and item not in seen:
                seen.add(item)
                merged.append(item)
        return merged

    # Process each category
    merged_memory = []
    for category in categories:
        items_1 = extract_category(memory_1, category)
        items_2 = extract_category(memory_2, category)
        merged_items = merge_lists(items_1, items_2)

        merged_memory.append(f"1. **{category}**:\n" + "\n".join(merged_items))

    return "\n\n".join(merged_memory)  # Reconstruct final formatted memory