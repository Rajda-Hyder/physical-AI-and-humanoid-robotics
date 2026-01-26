import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

from backend.src.services.qdrant_service import QdrantService
from backend.src.services.rag_service import RAGService
import os

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

print("Cohere key:", COHERE_API_KEY is not None)
print("Qdrant key:", QDRANT_API_KEY is not None)

qdrant_service = QdrantService(url=QDRANT_URL, api_key=QDRANT_API_KEY)
rag_service = RAGService(cohere_api_key=COHERE_API_KEY, qdrant_service=qdrant_service)

question = "What is Physical AI?"

response = rag_service.query(question)

print("\n--- Answer ---")
print(response.get("answer", "No answer returned"))
print("\n--- Sources ---")
for src in response.get("sources", []):
    print(src.get("url"), "-", src.get("score"))

