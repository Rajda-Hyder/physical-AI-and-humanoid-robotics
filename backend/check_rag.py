import os
from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient

# Load .env
load_dotenv()

# ENV variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "documents"

# Initialize clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)

qdrant = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    prefer_grpc=False
)

def embed_query(text: str):
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def search_qdrant(query_vector, limit=5):
    result = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=limit,
        with_payload=True
    )
    return result.points

def main():
    query = input("\nAsk something from your book: ")

    print("\nGenerating embedding...")
    embedding = embed_query(query)

    print("Searching Qdrant...")
    results = search_qdrant(embedding)

    if not results:
        print("\nNo results found.")
        return

    print("\n--- Retrieved Chunks ---\n")

    for i, point in enumerate(results, 1):
        payload = point.payload or {}
        text = payload.get("text", "")
        source = payload.get("source_url", "N/A")

        print(f"Result {i}")
        print("-" * 50)
        print(text[:1000])  # limit display
        print("\nSource:", source)
        print("\n")

if __name__ == "__main__":
    main()
