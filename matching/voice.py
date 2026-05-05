import whisper
import tempfile

_model = None

def get_model():
    global _model
    if _model is None:
        _model = whisper.load_model("base")  # fast enough for dev
    return _model


def transcribe_bytes(audio_bytes: bytes, suffix=".webm") -> str:
    """
    Takes raw audio bytes (from browser), writes to temp file, runs Whisper.
    """
    model = get_model()

    with tempfile.NamedTemporaryFile(delete=True, suffix=suffix) as f:
        f.write(audio_bytes)
        f.flush()
        result = model.transcribe(f.name)
        return result.get("text", "").strip()