import json
import base64
import requests

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from matching.voice import transcribe_bytes


BASE_URL = "http://127.0.0.1:8000"

QUESTIONS = [
    "What subjects do you enjoy the most?",
    "Do you currently work or study?",
    "Which aspect of work or study do you enjoy the most?",
    "Are you a more practical or theoretical person?"
]

MAX_QUESTIONS = 4


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.session_id = self.scope["url_route"]["kwargs"]["session_id"]

        self.question_index = 0

        print(f"WebSocket CONNECTED: {self.session_id}")

        await self.accept()

        # ==========================================
        # SEND FIRST QUESTION
        # ==========================================

        await self.send(json.dumps({
            "type": "question",
            "text": QUESTIONS[self.question_index]
        }))

    async def disconnect(self, close_code):

        print(f"WebSocket DISCONNECTED: {close_code}")

    async def receive(self, text_data):

        # ==========================================
        # PARSE JSON
        # ==========================================

        try:

            data = json.loads(text_data)

        except Exception:

            await self.send(json.dumps({
                "error": "Invalid JSON"
            }))

            return

        msg_type = data.get("type", "text")

        # ==========================================
        # HANDLE TEXT INPUT
        # ==========================================

        if msg_type == "text":

            user_input = data.get("message", "").strip()

            if not user_input:

                await self.send(json.dumps({
                    "error": "Empty message"
                }))

                return

        # ==========================================
        # HANDLE AUDIO INPUT
        # ==========================================

        elif msg_type == "audio":

            b64_audio = data.get("audio")

            if not b64_audio:

                await self.send(json.dumps({
                    "error": "No audio provided"
                }))

                return

            try:

                audio_bytes = base64.b64decode(b64_audio)

            except Exception:

                await self.send(json.dumps({
                    "error": "Invalid base64 audio"
                }))

                return

            # ==========================================
            # TRANSCRIBE AUDIO
            # ==========================================

            try:

                user_input = await sync_to_async(
                    transcribe_bytes
                )(audio_bytes)

            except Exception as e:

                await self.send(json.dumps({
                    "error": f"Transcription failed: {str(e)}"
                }))

                return

            # ==========================================
            # SEND TRANSCRIPT BACK
            # ==========================================

            await self.send(json.dumps({
                "type": "transcript",
                "text": user_input
            }))

            if not user_input:

                await self.send(json.dumps({
                    "error": "Empty transcription"
                }))

                return

        else:

            await self.send(json.dumps({
                "error": "Unknown message type"
            }))

            return

        # ==========================================
        # SAVE RESPONSE
        # ==========================================

        try:

            respond_response = await sync_to_async(
                requests.post
            )(
                f"{BASE_URL}/conversation/respond/{self.session_id}/",
                json={
                    "answer": user_input
                }
            )

            respond_data = respond_response.json()

        except Exception as e:

            await self.send(json.dumps({
                "error": f"Respond API failed: {str(e)}"
            }))

            return

        # ==========================================
        # STREAM FEATURES
        # ==========================================

        await self.send(json.dumps({
            "type": "stream",
            "chunk": f"\nFeatures Extracted: {json.dumps(respond_data.get('features', {}), indent=2)}\n\n"
        }))

        # ==========================================
        # NEXT QUESTION
        # ==========================================

        self.question_index += 1

        # ASK NEXT QUESTION
        if self.question_index < MAX_QUESTIONS:

            next_question = QUESTIONS[self.question_index]

            await self.send(json.dumps({
                "type": "question",
                "text": next_question
            }))

            return

        # ==========================================
        # FINAL RECOMMENDATION
        # ==========================================

        try:

            final_response = await sync_to_async(
                requests.get
            )(
                f"{BASE_URL}/recommendations/final/{self.session_id}/"
            )

            final_data = final_response.json()

        except Exception as e:

            await self.send(json.dumps({
                "error": f"Final recommendation failed: {str(e)}"
            }))

            return

        # ==========================================
        # FORMAT FINAL RESPONSE
        # ==========================================

        final_text = f"""

Final Career Recommendation

Career:
{final_data.get("career", "")}

Reason:
{final_data.get("reason", "")}

Skills To Learn:
{", ".join(final_data.get("skills_to_learn", []))}

Roadmap:
"""

        for step in final_data.get("roadmap", []):

            final_text += f"\n- {step}"

        # ==========================================
        # STREAM FINAL RESPONSE
        # ==========================================

        for word in final_text.split():

            await self.send(json.dumps({
                "type": "final_stream",
                "chunk": word + " "
            }))

        # ==========================================
        # DONE
        # ==========================================

        await self.send(json.dumps({
            "type": "done"
        }))