from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
import json

# Load careers
with open("matching/data/careers.json") as f:
    careers = json.load(f)

texts = [c["description"] for c in careers]
metadatas = careers

embedding = OpenAIEmbeddings()

vector_db = Chroma.from_texts(
    texts=texts,
    embedding=embedding,
    metadatas=metadatas,
    persist_directory="./chroma_db"
)