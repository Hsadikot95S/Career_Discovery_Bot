import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_explanation(user_profile, careers):
    """
    user_profile: string (combined user answers)
    careers: list of dicts from RAG
    """

    prompt = f"""
You are an expert career advisor.

User Profile:
{user_profile}

Top Career Options:
{careers}

Task:
1. Pick the BEST matching career
2. Explain WHY it fits the user
3. Suggest skills to learn
4. Provide a simple roadmap

Return JSON ONLY in this format:

{{
  "career": "...",
  "reason": "...",
  "skills_to_learn": ["...", "..."],
  "roadmap": ["step1", "step2"]
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful career advisor."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content