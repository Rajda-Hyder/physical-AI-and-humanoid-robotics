from src.config.settings import settings
from src.services.qdrant_service import QdrantService

print("QDRANT URL:", settings.qdrant_url)
print("QDRANT KEY:", settings.qdrant_api_key[:8], "...")

qdrant = QdrantService(
    url=settings.qdrant_url,
    api_key=settings.qdrant_api_key
)

result = qdrant.health_check()
print("QDRANT HEALTH RESULT =", result)
