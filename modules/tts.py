from RealtimeTTS import TextToAudioStream, CoquiEngine, PiperEngine, PiperVoice

from config import TTS_ENGINE

# Global initialization of the engine and stream
engine = None
stream = None

def setup_tts():
    global engine, stream
    if engine is None and stream is None:  # Only initialize once
        engine = __get_engine()
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


def __get_engine():
    match TTS_ENGINE:
        case "coqui":
            return __get_coqui_engine()
        case "piper":
            return __get_piper_engine()
        case _:
            raise Exception(f"TTS Enging '{TTS_ENGINE}' not found.")

def __get_coqui_engine():
    reference_wav = "TTS-Voices/Furina/3.wav"  # Path to a sample voice
    return CoquiEngine(
        model_name="tts_models/multilingual/multi-dataset/xtts_v2",
        voice=reference_wav
    )


def __get_piper_engine():
    voice = PiperVoice(
        model_file="D:\Dokumente\workspace\python_scripts\TTS-STT\piper\\voices\en_US-amy-low.onnx",
        config_file="D:\Dokumente\workspace\python_scripts\TTS-STT\piper\\voices\en_US-amy-low.onnx.json"
    )

    return PiperEngine(
        piper_path="D:\Dokumente\workspace\python_scripts\TTS-STT\piper\piper.exe",
        voice=voice,
    )
