import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def safe_json_parse(data):
    # ✅ Case 1: Already parsed (best case)
    if isinstance(data, dict):
        return data

    # ✅ Case 2: String → parse
    if isinstance(data, str):
        try:
            return json.loads(data)
        except:
            cleaned = data.replace("```json", "").replace("```", "").strip()
            try:
                return json.loads(cleaned)
            except:
                return {
                    "error": "Invalid JSON from LLM",
                    "raw_output": data
                }

    # fallback
    return {
        "error": "Unexpected LLM output type",
        "raw_output": str(data)
    }        
        
def generate_explanation(user_profile, careers):

    prompt = f"""
You are a strict JSON generator.

DO NOT output anything except valid JSON.

User Profile:
{user_profile}

Top Careers:
{careers}

Return EXACTLY this JSON format:

{{
  "career": "string",
  "reason": "string",
  "skills_to_learn": ["string"],
  "roadmap": ["string"]
}}

Rules:
- No markdown
- No explanation outside JSON
- No trailing text
- Keep response concise
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.3,  # 🔥 Lower = more deterministic
        messages=[
            {"role": "system", "content": "You output strict JSON only."},
            {"role": "user", "content": prompt}
        ]
    )

    content = response.choices[0].message.content

    return safe_json_parse(content)


def stream_explanation(user_profile, careers):
    prompt = f"""
You are a career advisor.

User:
{user_profile}

Careers:
{careers}

Respond with explanation, skills, and roadmap.
"""

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": prompt}
        ],
        stream=True  # 🔥 KEY
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content