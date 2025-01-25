# import sounddevice as sd
# from scipy.io import wavfile
# from TTS.api import TTS
# import torch
#
# # Set device
# device = "cuda" if torch.cuda.is_available() else "cpu"
#
# # Load local XTTS model
# local_model_path = "modelfiles/xtts_v2"
# tts_model = TTS(local_model_path).to(device)
#
# # Define reference speaker
# reference_wav = "Speakers/1.wav"
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
#
#
# # Example usage
# speak_text("Hello, this is an XTTS voice model running locally!")

#
# import tensorflow as tf
# print("TensorFlow GPU:", tf))
#
# import torch
# print("PyTorch GPU:", torch.cuda.is_available())