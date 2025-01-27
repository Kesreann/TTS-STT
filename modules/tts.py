from RealtimeTTS import TextToAudioStream, CoquiEngine

# Global initialization of the engine and stream
engine = None
stream = None

def setup_tts():
    global engine, stream
    if engine is None and stream is None:  # Only initialize once
        reference_wav = "TTS-Voices/Furina/3.wav"  # Path to a sample voice
        engine = CoquiEngine(model_name="tts_models/multilingual/multi-dataset/xtts_v2", voice=reference_wav)
        stream = TextToAudioStream(engine)

def speak_text(text_stream):
    if engine is None or stream is None:
        setup_tts()  # Ensure TTS is initialized

    stream.feed(text_stream['message']['content'])
    stream.play_async()

def tts_on_exit():
    stop_talking()
    engine.shutdown()

def stop_talking():
    if stream.is_playing():
        print("Stopping TTS Talk")
        stream.stop()