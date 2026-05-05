from django_filters import Filter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
import os
from dotenv import load_dotenv
import json
from django.conf import settings

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CAREERS_FILE = os.path.join(settings.BASE_DIR, "matching", "data", "careers.json")

with open(CAREERS_FILE, "r", encoding="utf-8") as f:
    ALL_CAREERS = json.load(f)

embedding = OpenAIEmbeddings(
    openai_api_key=os.getenv("OPENAI_API_KEY")
)
vector_db = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embedding
)

def get_top_careers(user_text):
    user_text = user_text.lower()

    scored = []

    for career in ALL_CAREERS:
        score = 0

        # Signal match
        for signal in career.get("signals", []):
            if signal in user_text:
                score += 2

        # Skill match
        for skill in career.get("skills", []):
            if skill in user_text:
                score += 1
        if score == 0:
            continue  

        scored.append((career, score))

    # Sort
    scored = sorted(scored, key=lambda x: x[1], reverse=True)

    return [c[0] for c in scored[:3]]