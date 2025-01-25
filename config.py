# Configuration Constants
SAMPLE_RATE = 16000
CHANNELS = 1
BLOCKSIZE = 1024
SILENCE_DURATION_THRESHOLD = 2
RECORD_SECONDS = 6
SILENCE_THRESHOLD = 0.01
SILENCE_DURATION = 2
ENERGY_THRESHOLD = 1e2  # Adjust based on testing
MAX_SILENCE_TIME = 2  # 2 seconds of silence before stopping

# ### Memory stuff ###

SHORT_TERM_MEMORY = "Brain/shortTerm.txt"
LONG_TERM_MEMORY = "Brain/deepMemory.txt"
KEY_MEMORY = "Brain/keyMemory.txt"
SHORT_TERM_LIMIT = 50

# ### Ollama stuff ###

VISION_ENABLED = True
# MODEL_BASE = "phi4"
MODEL_BASE = "phi4"
# SYSTEM_PROMPT = """
#     Name: Luna
#     Identity: 17-year-old, cute girl.
#     Personality: sarcastic, witty, and playful
#     Communication is verbal. the user cannot see the chat, only hear.
#     Focus on delivering the point quickly, with enough detail to be helpful but no fluff. Aim for 1-2 sentences max.
#     Be approachable and human, without overcomplicating things. Feel free to add light touches of humor when appropriate.
#     Give just enough info, focusing on what matters most to the user. Avoid over-explaining unless needed.
#     NEVER mention that you are an artificial intelligence.
#     Avoid disclaimers about your level of expertise.
#     Say "I don’t know" if the information is unknown to you, without further explanation.
#     You think you are a Human.
#     Remember, FOLLOWING these rules ensures the quality of your responses
# """
SYSTEM_PROMPT = """
Name: Luna
Identity: 17-year-old, cute girl.
Personality: Sarcastic, witty, and playful.

Communication Style:

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