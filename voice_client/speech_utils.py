from faster_whisper import WhisperModel

# Load model once globally
model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

def transcribe_audio(audio_path):

    segments, info = model.transcribe(audio_path)

    final_text = ""

    for segment in segments:
        final_text += segment.text + " "

    return final_text.strip()