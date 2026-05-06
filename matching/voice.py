import os
import tempfile
import imageio_ffmpeg

from faster_whisper import WhisperModel


# ==========================================
# PORTABLE FFMPEG
# ==========================================

ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

os.environ["FFMPEG_BINARY"] = ffmpeg_path


# ==========================================
# LOAD WHISPER MODEL
# ==========================================

model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)


# ==========================================
# TRANSCRIBE
# ==========================================

def transcribe_bytes(audio_bytes):

    with tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    ) as temp_audio:

        temp_audio.write(audio_bytes)

        temp_audio_path = temp_audio.name

    segments, _ = model.transcribe(temp_audio_path)

    final_text = ""

    for segment in segments:
        final_text += segment.text + " "

    return final_text.strip()