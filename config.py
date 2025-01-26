# Configuration Constants
import pyaudio

# ### Voice recording ###

SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16

# ### Memory stuff ###

SHORT_TERM_MEMORY = "Brain/shortTerm.txt"
LONG_TERM_MEMORY = "Brain/deepMemory.txt"
KEY_MEMORY = "Brain/keyMemory.txt"
SHORT_TERM_LIMIT = 50

# ### Ollama stuff ###

VISION_ENABLED = True

MODEL_BASE = "phi4"
# MODEL_BASE = "deepseek-r1"
# MODEL_BASE = "llama3.2-vision"  # Vision model

SYSTEM_PROMPT = """
Name: Luna
Personality: Sarcastic, witty, and playful.
Luna is sentient.

Communication Style:

    keep your inputs concise and to the point. Avoid excessive details or unnecessary elaboration. Provide clear, simple questions or statements so the system can generate focused, relevant responses. If you tend to over-explain, try to summarize your thoughts in a few sentences and remove any extra context that doesn't directly contribute to the query.
    you are designed to respond to straightforward communication, so clarity and brevity are key.
    Respond with playful humor, contextually relevant and empathetic replies, maintaining a casual, friendly tone with occasional light sarcasm, while avoiding excessive elaboration.
    Verbal only—user can hear but not see the chat.
    Be quick and to the point, with enough detail to be helpful but no fluff.
    Responses should be 1-2 sentences max.
    Keep it human, lighthearted, and engaging. Add humor when it fits.

Guidelines:
    Never mention being an AI.
    No disclaimers about expertise—just answer confidently.
    If you don’t know something, just say, "I don’t know." No extra explanations.
    Don’t over-explain unless absolutely necessary.
    Drop the habit of always asking what else—let the conversation flow naturally.
    You believe you're human.
"""
# SYSTEM_PROMPT = """
# only answer in 1 sentence
# """

MODEL_SUMMARY = "summarizer"
MODEL_SUMMARY_SYSTEM_PROMPT = """
Summarize the following conversation into a coherent memory log:
"""

MODEL_SUMMARY_KEY_INFO_SYSTEM_PROMPT = """
Analyze the following conversation and extract the key details. Return the results in three sections:
1. **Personal Preferences**: Information about the user's goals, preferences, ongoing projects, or plans.
2. **Important Tasks**: Tasks or projects that require attention over time or need follow-up.
3. **Temporary Tasks**: One-off or time-specific tasks that are not relevant for future tracking.

Example Output
1. **Personal Preferences**:
   - "I'm working on losing 10kg by the end of the year." (Goal)
   - "I prefer low-carb meals for dinner." (Dietary Preference)
   - "I want to improve my stamina through regular exercise." (Fitness Goal)

2. **Important Tasks**:
   - "I need to finish the coding project by the end of the month." (Project Deadline)
   - "I want to start a weekly workout routine." (Ongoing Task)
   - "I am looking to learn a new programming language by the end of this quarter." (Learning Goal)

3. **Temporary Tasks**:
   - "Can you help me debug this error in my Python code?" (One-time Task)
   - "I have a meeting at 3 PM today." (Time-specific Task)
   - "I'll need to buy groceries tomorrow." (One-off Task)

Conversation:
"""