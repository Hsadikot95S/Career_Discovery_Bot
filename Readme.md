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

### Send audio

```
{
  "type": "audio",
  "audio": "<base64>"
}
```

---

### Responses

Transcript (for audio):

```
{
  "type": "transcript",
  "text": "I like physics"
}
```

Streaming response:

```
{ "type": "stream", "chunk": "You " }
{ "type": "stream", "chunk": "should " }
...
{ "type": "done" }
```

---

## WebSocket Testing

### Option 1: Postman (WebSocket)

1. Open Postman → New → WebSocket Request
2. Enter:

```
ws://127.0.0.1:8000/ws/chat/{{session_id}}/
```

3. Connect and send:

```
{
  "type": "text",
  "message": "I enjoy problem solving"
}
```

---

### Option 2: Browser Console

```
const ws = new WebSocket("ws://127.0.0.1:8000/ws/chat/<session_id>/");

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: "text",
    message: "I like math"
  }));
};

ws.onmessage = (e) => console.log(e.data);
```

---

### Option 3: Python Script (Audio Test)

```
import websocket, json, base64

ws = websocket.create_connection("ws://127.0.0.1:8000/ws/chat/<session_id>/")

with open("test.wav", "rb") as f:
    audio = base64.b64encode(f.read()).decode()

ws.send(json.dumps({
    "type": "audio",
    "audio": audio
}))

while True:
    print(ws.recv())
```

---

### Expected Behavior

* Connection succeeds
* Transcript returned for audio
* Multiple `stream` messages received
* Final `done` message

---

### Send text

```
{
  "type": "text",
  "message": "I like coding"
}
```

---

### Send audio

```
{
  "type": "audio",
  "audio": "<base64>"
}
```

---

### Responses

Transcript (for audio):

```
{
  "type": "transcript",
  "text": "I like physics"
}
```

Streaming response:

```
{ "type": "stream", "chunk": "You " }
{ "type": "stream", "chunk": "should " }
...
{ "type": "done" }
```

---

## Postman Collection

You can import this JSON into Postman (includes success + error examples):

```
{
  "info": {
    "name": "Career Assistant API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    { "key": "base_url", "value": "http://127.0.0.1:8000" },
    { "key": "session_id", "value": "" }
  ],
  "item": [
    {
      "name": "Start Conversation",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/conversation/start/"
      },
      "response": [
        {
          "name": "200 OK",
          "status": "OK",
          "code": 200,
          "_postman_previewlanguage": "json",
          "body": "{
  \"session_id\": \"cf9fb5c0-57c8-4622-b30b-c8e06c9c36cd\"
}"
        },
        {
          "name": "500 Error",
          "status": "Internal Server Error",
          "code": 500,
          "_postman_previewlanguage": "json",
          "body": "{
  \"error\": \"Failed to create session\"
}"
        }
      ]
    },
    {
      "name": "Next Question",
      "request": {
        "method": "POST",
        "header": [
          {"key": "Content-Type", "value": "application/json"}
        ],
        "body": {
          "mode": "raw",
          "raw": "{
  \"answer\": \"I like math and coding\"
}"
        },
        "url": "{{base_url}}/conversation/next/{{session_id}}/"
      },
      "response": [
        {
          "name": "200 OK",
          "status": "OK",
          "code": 200,
          "_postman_previewlanguage": "json",
          "body": "{
  \"question\": \"What type of problems do you enjoy solving?\",
  \"step\": 2
}"
        },
        {
          "name": "400 Missing Answer",
          "status": "Bad Request",
          "code": 400,
          "_postman_previewlanguage": "json",
          "body": "{
  \"error\": \"Answer is required\"
}"
        },
        {
          "name": "404 Invalid Session",
          "status": "Not Found",
          "code": 404,
          "_postman_previewlanguage": "json",
          "body": "{
  \"error\": \"Invalid session\"
}"
        }
      ]
    },
    {
      "name": "Final Recommendation",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/matching/final/{{session_id}}/"
      },
      "response": [
        {
          "name": "200 OK",
          "status": "OK",
          "code": 200,
          "_postman_previewlanguage": "json",
          "body": "{
  \"career\": \"Software Engineer\",
  \"reason\": \"Strong alignment with analytical and technical interests\",
  \"skills_to_learn\": [\"Data Structures\", \"System Design\"],
  \"roadmap\": [\"Learn fundamentals\", \"Build projects\", \"Apply for roles\"]
}"
        },
        {
          "name": "400 LLM Parse Error",
          "status": "Bad Request",
          "code": 400,
          "_postman_previewlanguage": "json",
          "body": "{
  \"error\": \"LLM output parsing failed\",
  \"raw\": {}
}"
        },
        {
          "name": "404 Invalid Session",
          "status": "Not Found",
          "code": 404,
          "_postman_previewlanguage": "json",
          "body": "{
  \"error\": \"Invalid session\"
}"
        }
      ]
    }
  ]
}
```

{
"info": {
"name": "Career Assistant API",
"schema": "[https://schema.getpostman.com/json/collection/v2.1.0/collection.json](https://schema.getpostman.com/json/collection/v2.1.0/collection.json)"
},
"item": [
{
"name": "Start Conversation",
"request": {
"method": "POST",
"url": "[http://127.0.0.1:8000/conversation/start/](http://127.0.0.1:8000/conversation/start/)"
},
"response": [
{
"name": "Success",
"originalRequest": {},
"status": "OK",
"code": 200,
"_postman_previewlanguage": "json",
"body": "{
"session_id": "cf9fb5c0-57c8-4622-b30b-c8e06c9c36cd"
}"
}
]
},
{
"name": "Next Question",
"request": {
"method": "POST",
"header": [
{"key": "Content-Type", "value": "application/json"}
],
"body": {
"mode": "raw",
"raw": "{
"answer": "I like math and coding"
}"
},
"url": "[http://127.0.0.1:8000/conversation/next/{{session_id}}/](http://127.0.0.1:8000/conversation/next/{{session_id}}/)"
},
"response": [
{
"name": "Next Question Response",
"status": "OK",
"code": 200,
"_postman_previewlanguage": "json",
"body": "{
"question": "What type of problems do you enjoy solving?",
"step": 2
}"
}
]
},
{
"name": "Final Recommendation",
"request": {
"method": "GET",
"url": "[http://127.0.0.1:8000/matching/final/{{session_id}}/](http://127.0.0.1:8000/matching/final/{{session_id}}/)"
},
"response": [
{
"name": "Final Output",
"status": "OK",
"code": 200,
"_postman_previewlanguage": "json",
"body": "{
"career": "Software Engineer",
"reason": "Strong alignment with analytical and technical interests",
"skills_to_learn": ["Data Structures", "System Design"],
"roadmap": ["Learn fundamentals", "Build projects", "Apply for roles"]
}"
}
]
}
]
}

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
