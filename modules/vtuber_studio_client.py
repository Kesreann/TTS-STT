import asyncio
import websockets
import pyttsx3

# Local WebSocket Server (server script must be running)
LOCAL_SERVER_URL = "ws://localhost:8765"

def speak_text(text):
    """Generates speech from text and triggers mouth animation."""
    engine = pyttsx3.init()

    async def send_speak_command():
        async with websockets.connect(LOCAL_SERVER_URL) as ws:
            await ws.send("speak")

    # Run mouth movement in parallel
    asyncio.run(send_speak_command())

    # Speak the text
    engine.say(text)
    engine.runAndWait()
