from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

embedding = OpenAIEmbeddings(
    openai_api_key=os.getenv("OPENAI_API_KEY")
)
vector_db = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embedding
)


def get_top_careers(query):
    results = vector_db.similarity_search(query, k=3)

    return [r.metadata for r in results]