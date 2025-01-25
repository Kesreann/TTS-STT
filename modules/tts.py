# import sounddevice as sd
# from scipy.io import wavfile
# from TTS.api import TTS
# import torch
#
# device = "cuda" if torch.cuda.is_available() else "cpu"
# tts_model = TTS("tts_models/en/jenny/jenny").to(device)
#
#
# def speak_text(text):
#     output_wav = "response.wav"
#     tts_model.tts_to_file(text, file_path=output_wav)
#     samplerate, data = wavfile.read(output_wav)
#     sd.play(data, samplerate)
#     sd.wait()

# import sounddevice as sd
# from scipy.io import wavfile
# from TTS.api import TTS
# import torch
#
# # Select device
# device = "cuda" if torch.cuda.is_available() else "cpu"
#
# # Load XTTS model
# tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
#
# # Define reference audio for speaker adaptation
# reference_wav = "TTS-Voices/Furina/1.wav"  # Path to a sample voice
# # reference_wav = "TTS-Voices/Nahida/VO_Nahida_Hello.wav"  # Path to a sample voice
#
#
# def speak_text(text):
#     output_wav = "response.wav"
#
#     # Generate speech with speaker adaptation
#     tts_model.tts_to_file(
#         text=text,
#         file_path=output_wav,
#         speaker_wav=reference_wav,  # Use reference speaker
#         language="en"  # Adjust language as needed
#     )
#
#     # Play the generated audio
#     samplerate, data = wavfile.read(output_wav)
#     sd.play(data, samplerate)
#     sd.wait()

from RealtimeTTS import TextToAudioStream, CoquiEngine
import time

# Global initialization of the engine and stream
engine = None
stream = None

def setup_tts():
    global engine, stream
    if engine is None and stream is None:  # Only initialize once
        reference_wav = "TTS-Voices/Furina/1.wav"  # Path to a sample voice
        engine = CoquiEngine(model_name="tts_models/multilingual/multi-dataset/xtts_v2", voice=reference_wav)
        stream = TextToAudioStream(engine)

def speak_text(text_stream):
    print(dir(text_stream))
    if engine is None or stream is None:
        setup_tts()  # Ensure TTS is initialized

    stream.feed(text_stream['message']['content'])
    stream.play_async()


# import sounddevice as sd
# from scipy.io import wavfile
# from TTS.api import TTS
# import torch
#
# device = "cuda" if torch.cuda.is_available() else "cpu"
#
# # Load local XTTS model
# local_model_path = "modelfiles/xtts_v2"
# tts_model = TTS(local_model_path).to(device)
#
# # Define reference speaker
# reference_wav = "D:\\Dokumente\\workspace\\python_scripts\\TTS-STT\\TTS-Voices\\Furina\\1.wav"
#
#
# def speak_text(text):
#     output_wav = "response.wav"
#
#     # Generate speech using the locally stored model
#     tts_model.tts_to_file(
#         text=text,
#         file_path=output_wav,
#         speaker_wav=reference_wav,  # Use reference speaker
#         language="en"  # Adjust as needed
#     )
#
#     # Play the output
#     samplerate, data = wavfile.read(output_wav)
#     sd.play(data, samplerate)
#     sd.wait()

# import sounddevice as sd
# from TTS.api import TTS
# import torch
#
# tts_model = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False)
#
# def speak_text(text):
#     speaker_wav = "TTS-Voices/Furina/1.wav"
#     language = "en"
#     """
#     Convert text to speech using the XTTS v2 model with voice cloning.
#
#     :param text: Text to be converted to speech.
#     :param speaker_wav: Path to the reference speaker audio file for voice cloning.
#     :param language: Language code for the desired output language (default is "en" for English).
#     """
#     # Load the XTTS v2 model
#
#     # Move model to the appropriate device (CPU or GPU)
#     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#     tts_model.to(device)
#
#     # Generate speech
#     audio_output = tts_model.tts(
#         text=text,
#         speaker_wav=speaker_wav,
#         language=language
#     )
#
#     # Stream audio directly
#     sd.play(audio_output, samplerate=24000)  # Adjust samplerate if needed
#     sd.wait()
#
