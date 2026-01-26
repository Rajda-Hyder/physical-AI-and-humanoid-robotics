from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()  # ye ensure karega ke QDRANT_URL aur QDRANT_API_KEY read ho rahe hain

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

print("\n--- Collections ---")
collections = client.get_collections()
print(collections)

print("\n--- Documents Collection Info ---")
info = client.get_collection("documents")
print("Points count:", info.points_count)
