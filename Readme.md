# Real-Time AI Career Assistant (Backend)

## What this is

This is a backend system for a career assistant that works in real time. It supports both text and voice input, processes user responses step-by-step, and returns career recommendations with explanations.

The system is designed around WebSockets instead of traditional request/response APIs so that responses can be streamed back progressively.

---

## How it works (high level)

1. User starts a session
2. System asks questions and collects answers
3. Answers are converted into features
4. A scoring system ranks possible career paths
5. Retrieved context (RAG) is added
6. LLM generates explanation
7. Response is streamed back via WebSocket

---

## Stack

* Django (core backend)
* Django Channels (WebSockets)
* OpenAI (LLM + embeddings)
* ChromaDB (vector search)
* Whisper (speech-to-text)
* SQLite (dev DB)

---

## Project layout

```
core/
users/
user_sessions/
conversations/
features/
matching/
recommendations/
```

---

## Setup

### 1. Install dependencies

```
pip install -r requirements.txt
```

### 2. Add environment variables

Create `.env`:

```
OPENAI_API_KEY=your_key
```

### 3. Run migrations

```
python manage.py migrate
```

### 4. Start server

HTTP endpoints:

```
python manage.py runserver
```

WebSocket server:

```
python -m daphne core.asgi:application
```

---

## API (REST)

### Start conversation

```
POST /conversation/start/
```

Response:

```
{
  "session_id": "uuid"
}
```

---

### Continue conversation

```
POST /conversation/next/<session_id>/
```

Body:

```
{
  "answer": "I like math"
}
```

---

### Final recommendation

```
GET /matching/final/<session_id>/
```

---

## WebSocket API

### Connect

```
ws://127.0.0.1:8000/ws/chat/<session_id>/
```

---

### Send text

```
{
  "type": "text",
  "message": "I like coding"
}
```


---

### Responses


Streaming response:

```
{ "type": "stream", "chunk": "You " }
{ "type": "stream", "chunk": "should " }
...
{ "type": "done" }
```

---

## Postman Collection

You can import this JSON into Postman:

```
{
  "info": {
    "name": "Career Assistant API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Start",
      "request": {
        "method": "POST",
        "url": "http://127.0.0.1:8000/conversation/start/"
      }
    },
    {
      "name": "Next",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {"mode": "raw", "raw": "{\n  \"answer\": \"I like math\"\n}"},
        "url": "http://127.0.0.1:8000/conversation/next/{{session_id}}/"
      }
    },
    {
      "name": "Final",
      "request": {
        "method": "GET",
        "url": "http://127.0.0.1:8000/matching/final/{{session_id}}/"
      }
    }
  ]
}
```

---

## Notes

* Whisper runs on CPU → expect a few seconds delay
* Streaming is currently buffered (not token-by-token)
* No rate limiting yet
* SQLite is only for development

---

## Next improvements

* True streaming (token-by-token)
* Move to Postgres
* Add Redis caching
* Add monitoring/logging
* Build frontend

---

## Status

Backend is complete and functional. Ready to be integrated with frontend or deployed with additional production hardening.
