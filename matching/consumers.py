import json
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from user_sessions.models import Session
from matching.hybrid_engine import hybrid_recommendation
from matching.utils import build_user_profile
from matching.llm_engine import stream_explanation
from matching.voice import transcribe_bytes


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.session_id = self.scope["url_route"]["kwargs"]["session_id"]
        print(f"WebSocket CONNECTED: {self.session_id}")
        await self.accept()

    async def disconnect(self, close_code):
        print(f"WebSocket DISCONNECTED: {close_code}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except Exception:
            await self.send(json.dumps({"error": "Invalid JSON"}))
            return

        msg_type = data.get("type", "text")

        # 🔹 1) Resolve user input (text OR audio)
        if msg_type == "text":
            user_input = data.get("message", "").strip()
            if not user_input:
                await self.send(json.dumps({"error": "Empty message"}))
                return

        elif msg_type == "audio":
            b64 = data.get("audio")
            if not b64:
                await self.send(json.dumps({"error": "No audio provided"}))
                return

            try:
                audio_bytes = base64.b64decode(b64)
            except Exception:
                await self.send(json.dumps({"error": "Invalid base64 audio"}))
                return

            # 🔥 Transcribe
            user_input = await sync_to_async(transcribe_bytes)(audio_bytes)

            await self.send(json.dumps({
                "type": "transcript",
                "text": user_input
            }))

            if not user_input:
                await self.send(json.dumps({"error": "Empty transcription"}))
                return

        else:
            await self.send(json.dumps({"error": "Unknown message type"}))
            return

        # 🔹 2) Fetch session
        try:
            session = await sync_to_async(Session.objects.get)(id=self.session_id)
        except Session.DoesNotExist:
            await self.send(json.dumps({"error": "Invalid session"}))
            return

        # 🔹 3) Build profile + hybrid
        user_profile = await sync_to_async(build_user_profile)(session)
        hybrid = await sync_to_async(hybrid_recommendation)(session)

        # 🔥 4) STREAM LLM (FIXED)
        try:
            # ✅ Correct way (NO lambda misuse, NO double call)
            def generate_tokens():
                return list(stream_explanation(user_profile, hybrid["recommendations"]))

            tokens = await sync_to_async(generate_tokens)()

            for token in tokens:
                await self.send(json.dumps({
                    "type": "stream",
                    "chunk": token
                }))

        except Exception as e:
            await self.send(json.dumps({
                "error": f"Streaming failed: {str(e)}"
            }))
            return

        await self.send(json.dumps({"type": "done"}))