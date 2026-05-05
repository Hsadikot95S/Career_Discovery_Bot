# Real-Time AI Career Assistant (Backend)

## What this is

This backend powers a real-time AI career assistant that supports both **text and voice interaction**, processes user responses incrementally, and generates **personalized career recommendations with explanations**.

The system combines:

* Rule-based feature extraction
* Hybrid scoring (features + retrieval)
* RAG (retrieval over career data)
* LLM-based reasoning
* WebSocket streaming

---

## How it works (high level)

1. User starts a session
2. User answers questions (text or voice)
3. Answers are stored as messages
4. Feature extraction runs per answer
5. Features are aggregated across session
6. RAG retrieves relevant careers
7. Hybrid scoring ranks careers
8. LLM generates explanation
9. Response is streamed via WebSocket

---

## Architecture Flow

```
User Input → Message Store → Feature Extraction → Feature Aggregation
→ RAG Retrieval → Hybrid Scoring → LLM Explanation → Streaming Output
```

---

## Stack

* Django (API + orchestration)
* Django Channels (WebSockets)
* OpenAI (LLM + embeddings)
* ChromaDB (vector retrieval)
* Whisper (speech-to-text)
* SQLite (development DB)

---

## Project layout

```
core/
users/
user_sessions/
conversations/   # session + Q/A handling
features/        # feature extraction + storage
matching/        # RAG + hybrid scoring + LLM
recommendations/
```

---

## Setup

### 1. Install dependencies

```
pip install -r requirements.txt
```

### 2. Environment variables

Create `.env`:

```
OPENAI_API_KEY=your_key
```

---

### 3. Run migrations

```
python manage.py migrate
```

---

### 4. Start servers

HTTP:

```
python manage.py runserver
```

WebSocket (required for streaming):

```
python -m daphne core.asgi:application
```

---

# REST API

---

## 1. Start session

```
POST /conversation/start/
```

### Response

```
{
  "session_id": "uuid"
}
```

---

## 2. Send user response

```
POST /conversation/respond/<session_id>/
```

### Body

```
{
  "answer": "I like Hindi and English and writing"
}
```

### What happens internally

* Message is saved
* Features are extracted
* FeatureVector is stored

---

## 3. Basic recommendations (RAG only)

```
GET /recommendations/basic/<session_id>/
```

### Response

```
{
  "query": {
    "raw_text": "user aggregated input"
  },
  "recommendations": [...]
}
```

---

## 4. Scored recommendations (Hybrid Engine)

```
GET /recommendations/scored/<session_id>/
```

### Response

```
{
  "features": {...},
  "domain_scores": {...},
  "recommendations": [...]
}
```

---

## 5. Final recommendation (LLM output)

```
GET /recommendations/final/<session_id>/
```

### Response

```
{
  "career": "...",
  "reason": "...",
  "skills_to_learn": [...],
  "roadmap": [...]
}
```

---

# WebSocket API (Real-Time)

---

## Connect

```
ws://127.0.0.1:8000/ws/chat/<session_id>/
```

---

## Send TEXT

```
{
  "type": "text",
  "message": "I enjoy writing and storytelling"
}
```

---

## Send AUDIO (base64)

```
{
  "type": "audio",
  "audio": "<base64_encoded_audio>"
}
```

---

## Responses

### Transcript (for audio)

```
{
  "type": "transcript",
  "text": "I enjoy writing"
}
```

---

### Streaming output

```
{ "type": "stream", "chunk": "You " }
{ "type": "stream", "chunk": "should " }
...
{ "type": "done" }
```

---

# Key Components

---

## Feature Extraction

Located in:

```
features/extractor.py
```

* Converts user text → structured features
* Handles positive + negative signals

---

## Feature Storage

```
FeatureVector (per user answer)
```

* Stored per message
* Aggregated later for scoring

---

## RAG Engine

```
matching/rag_engine.py
```

* Uses careers.json
* Filters irrelevant careers
* Uses signal + skill scoring
* Removes zero-score candidates

---

## Hybrid Engine

```
matching/hybrid_engine.py
```

Combines:

* RAG score
* Feature/domain score
* Signal score

---

## LLM Engine

```
matching/llm_engine.py
```

* Generates final explanation
* Outputs structured JSON

---

# Postman Collection (Updated)

```
{
  "info": {
    "name": "Career Assistant API"
  },
  "item": [
    {
      "name": "Start Session",
      "request": {
        "method": "POST",
        "url": "http://127.0.0.1:8000/conversation/start/"
      }
    },
    {
      "name": "Respond",
      "request": {
        "method": "POST",
        "header": [
          {"key": "Content-Type", "value": "application/json"}
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"answer\": \"I like Hindi and writing\"\n}"
        },
        "url": "http://127.0.0.1:8000/conversation/respond/{{session_id}}/"
      }
    },
    {
      "name": "Basic",
      "request": {
        "method": "GET",
        "url": "http://127.0.0.1:8000/recommendations/basic/{{session_id}}/"
      }
    },
    {
      "name": "Scored",
      "request": {
        "method": "GET",
        "url": "http://127.0.0.1:8000/recommendations/scored/{{session_id}}/"
      }
    },
    {
      "name": "Final",
      "request": {
        "method": "GET",
        "url": "http://127.0.0.1:8000/recommendations/final/{{session_id}}/"
      }
    }
  ]
}
```

---

# Important Notes

* RAG now uses **filtering + scoring (not raw similarity)**
* Feature extraction is **rule-based (currently)**
* WebSocket streaming is **chunked (not token-level yet)**
* SQLite is used only for development

---

# Known Limitations

* Feature extraction is keyword-based (can be improved)
* No caching layer yet
* No authentication
* No rate limiting

---

# Next Improvements

* Token-level streaming (true real-time LLM)
* Replace rule-based features with embeddings/classifier
* Add Redis (caching + channels layer)
* Move to PostgreSQL
* Add observability (logs + metrics)
* Frontend integration

---

# Status

Backend is fully functional:

* End-to-end pipeline working
* RAG + hybrid scoring stable
* WebSocket streaming working
* Voice + text supported

Ready for:

* Demo
* Frontend integration
* Production hardening

---
