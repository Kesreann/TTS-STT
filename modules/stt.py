from faster_whisper import WhisperModel

whisper_model = WhisperModel("large-v3", compute_type="int8", device="cuda")

def transcribe_audio(audio_path):
    segments, _ = whisper_model.transcribe(audio_path, language="en")
    return " ".join(segment.text for segment in segments).strip()
