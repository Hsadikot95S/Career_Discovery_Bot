import asyncio
import websockets
import json
import base64
import sounddevice as sd
from scipy.io.wavfile import write
import uuid
from gtts import gTTS
from playsound import playsound
import os
import requests


# ==========================================
# CONFIG
# ==========================================

BASE_HTTP_URL = "http://127.0.0.1:8000"
BASE_WS_URL = "ws://127.0.0.1:8000/ws/chat"

SAMPLE_RATE = 16000
DURATION = 5

assistant_response = ""


# ==========================================
# START SESSION
# ==========================================

def start_session():

    response = requests.post(
        f"{BASE_HTTP_URL}/conversation/start/"
    )

    data = response.json()

    return data


# ==========================================
# RECORD AUDIO
# ==========================================

def record_audio():

    filename = f"{uuid.uuid4()}.wav"

    print("\n🎤 Speak now...")

    recording = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype='int16'
    )

    sd.wait()

    write(filename, SAMPLE_RATE, recording)

    print("✅ Recording finished")

    return filename


# ==========================================
# AUDIO -> BASE64
# ==========================================

def audio_to_base64(audio_path):

    with open(audio_path, "rb") as f:

        encoded = base64.b64encode(
            f.read()
        ).decode("utf-8")

    return encoded


# ==========================================
# TEXT TO SPEECH
# ==========================================

def speak(text):

    filename = f"{uuid.uuid4()}.mp3"

    print("\n🤖 Assistant:")
    print(text)

    tts = gTTS(
        text=text,
        lang='en'
    )

    tts.save(filename)

    playsound(filename)

    os.remove(filename)


# ==========================================
# MAIN CHAT LOOP
# ==========================================

async def chat():

    global assistant_response

    # ==========================================
    # CREATE SESSION
    # ==========================================

    session_data = start_session()

    session_id = session_data["session_id"]

    print("\n✅ SESSION CREATED")
    print("Session ID:", session_id)

    # ==========================================
    # DYNAMIC WEBSOCKET URL
    # ==========================================

    ws_url = f"{BASE_WS_URL}/{session_id}/"

    # ==========================================
    # CONNECT WEBSOCKET
    # ==========================================

    async with websockets.connect(ws_url) as websocket:

        while True:

            response = await websocket.recv()

            data = json.loads(response)

            print("\n📩 RAW SERVER RESPONSE:")
            print(data)

            msg_type = data.get("type")

            # ==========================================
            # HANDLE SERVER ERRORS
            # ==========================================

            if "error" in data:

                print("\n❌ SERVER ERROR:")
                print(data["error"])

                break

            # ==========================================
            # QUESTION EVENT
            # ==========================================

            elif msg_type == "question":

                question = data["text"]

                print("\n🤖 Assistant Question:")
                print(question)

                speak(question)

                # RECORD AUDIO
                audio_path = record_audio()

                # AUDIO -> BASE64
                encoded_audio = audio_to_base64(audio_path)

                # SEND AUDIO
                payload = {
                    "type": "audio",
                    "audio": encoded_audio
                }

                await websocket.send(
                    json.dumps(payload)
                )

            # ==========================================
            # TRANSCRIPT
            # ==========================================

            elif msg_type == "transcript":

                print("\n📝 Transcript:")
                print(data["text"])

            # ==========================================
            # NORMAL STREAM (PRINT ONLY)
            # ==========================================

            elif msg_type == "stream":

                chunk = data["chunk"]

                print(chunk, end="", flush=True)

            # ==========================================
            # FINAL STREAM (PRINT + SPEAK)
            # ==========================================

            elif msg_type == "final_stream":

                chunk = data["chunk"]

                assistant_response += chunk

                print(chunk, end="", flush=True)

            # ==========================================
            # DONE
            # ==========================================

            elif msg_type == "done":

                print("\n")

                if assistant_response.strip():

                    speak(assistant_response)

                break

            # ==========================================
            # UNKNOWN MESSAGE
            # ==========================================

            else:

                print("\n⚠️ Unknown message:")
                print(data)


# ==========================================
# ENTRYPOINT
# ==========================================

if __name__ == "__main__":

    asyncio.run(chat())