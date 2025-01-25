import os
import ollama
from config import SHORT_TERM_MEMORY, LONG_TERM_MEMORY, MODEL_SUMMARY, SHORT_TERM_LIMIT, MODEL_SUMMARY_SYSTEM_PROMPT, \
    MODEL_SUMMARY_KEY_INFO_SYSTEM_PROMPT, KEY_MEMORY
import logging
import json

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
    short_term.append(f"{agent}: {message}\n")

    # Trim to keep only the last SHORT_TERM_LIMIT exchanges
    if len(short_term) > SHORT_TERM_LIMIT:
        short_term = short_term[-SHORT_TERM_LIMIT:]

    save_memory(SHORT_TERM_MEMORY, short_term)


def update_long_term_memory():
    """Summarizes short-term memory and appends it to long-term memory reliably."""
    logging.info("Updating Longterm Memory")
    short_term = load_memory(SHORT_TERM_MEMORY, as_list=False).strip()
    long_term = load_memory(LONG_TERM_MEMORY, as_list=False).strip()
    key_memories = load_memory(KEY_MEMORY, as_list=False).strip()
    print("loaded both files")

    if short_term:
        full_conversation = f"{long_term}\n\n{short_term}" if long_term else short_term
        logging.info("Sending convo to ollama to summarize")
        response = ollama.chat(model=MODEL_SUMMARY, messages=[
            {"role": "system", "content": MODEL_SUMMARY_SYSTEM_PROMPT},
            {"role": "user", "content": full_conversation}
        ])
        logging.info("got the response from ollama")

        summary = response.get('message', {}).get('content', '').strip()
        if summary:  # Ensure valid summary before saving
            logging.info("save response memory in file")
            save_memory(LONG_TERM_MEMORY, summary, as_list=False)
            save_memory(SHORT_TERM_MEMORY, "", as_list=False)  # Clear short-term memory

        #
        # logging.info("Sending convo to ollama for key information extraction")
        # response_key_memory = ollama.chat(model=MODEL_SUMMARY, messages=[
        #     {"role": "system", "content": MODEL_SUMMARY_KEY_INFO_SYSTEM_PROMPT},
        #     {"role": "user", "content": full_conversation}
        # ])
        #
        # if response_key_memory:
        #     save_memory(KEY_MEMORY, merge_conversations(response_key_memory['message']['content'], key_memories), as_list=False)
        #
        # print(response_key_memory['message']['content'])
        # logging.debug("key memory response: " + response_key_memory['message']['content'])


def load_memory_on_start():
    """Loads long-term memory into the system on startup."""
    return load_memory(LONG_TERM_MEMORY, as_list=False).strip()


def memory_on_exit():
    """Handles memory saving on program exit."""
    update_long_term_memory()


def merge_conversations(memory_1, memory_2):
    """
    Merges two structured conversations and returns the updated memory.

    Arguments:
    memory_1 -- Dictionary (or JSON string) representing the first conversation's extracted categories.
    memory_2 -- Dictionary (or JSON string) representing the second conversation's extracted categories.

    Returns:
    Merged dictionary.
    """

    # Ensure inputs are dictionaries (if they're strings, attempt to parse them)
    def ensure_dict(memory):
        if isinstance(memory, str):
            try:
                return json.loads(memory)  # Convert JSON string to dict
            except json.JSONDecodeError:
                print("Error: Invalid JSON string.")
                return {}  # Default to an empty dict if parsing fails
        elif isinstance(memory, dict):
            return memory
        else:
            return {}  # Default to an empty dict if type is unknown

    # Ensure that both memory_1 and memory_2 are dictionaries
    memory_1 = ensure_dict(memory_1)
    memory_2 = ensure_dict(memory_2)

    # Merging function for categories
    def merge_category(category_1, category_2):
        # Combine both categories and remove duplicates
        return list(set(category_1 + category_2))

    # Initialize merged memory with empty lists, ensuring keys exist in both dictionaries
    merged_memory = {
        "Personal Preferences": merge_category(
            memory_1.get("Personal Preferences", []),
            memory_2.get("Personal Preferences", [])
        ),
        "Important Tasks": merge_category(
            memory_1.get("Important Tasks", []),
            memory_2.get("Important Tasks", [])
        ),
        "Temporary Tasks": merge_category(
            memory_1.get("Temporary Tasks", []),
            memory_2.get("Temporary Tasks", [])
        )
    }

    return json.dumps(merged_memory, indent=4)