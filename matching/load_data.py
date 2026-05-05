import json
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
import os

from dotenv import load_dotenv
load_dotenv()

def load_career_data():
    with open("matching/data/careers.json") as f:
        careers = json.load(f)

    texts = [c["description"] for c in careers]
    metadatas = careers

    embedding = OpenAIEmbeddings(
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    db = Chroma.from_texts(
        texts=texts,
        embedding=embedding,
        metadatas=metadatas,
        persist_directory="./chroma_db"
    )

    db.persist()

    print("Career data loaded into vector DB")


if __name__ == "__main__":
    load_career_data()