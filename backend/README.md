# RAG Chatbot Backend API

Production-grade FastAPI backend for Retrieval-Augmented Generation using Cohere embeddings and Qdrant vector database.

## Features

- ✅ FastAPI with async support
- ✅ POST `/api/query` endpoint for RAG queries
- ✅ Cohere embeddings (embed-english-v3.0)
- ✅ Qdrant vector database integration
- ✅ Full error handling and logging
- ✅ Health checks and service monitoring
- ✅ CORS support
- ✅ Pydantic request/response validation
- ✅ Interactive API documentation

## Project Structure

```
backend/
├── app.py                      # FastAPI application
├── api/
│   ├── __init__.py
│   └── routes.py               # API endpoints
├── services/
│   ├── __init__.py
│   ├── rag_service.py          # RAG orchestration
│   └── qdrant_service.py       # Qdrant integration
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
└── README.md                  # This file
```

## Installation

### 1. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp backend/.env.example backend/.env

# Edit .env with your credentials
export QDRANT_URL=https://your-instance.qdrant.io
export QDRANT_API_KEY=your_api_key
export QDRANT_COLLECTION_NAME=documents
export COHERE_API_KEY=your_cohere_key
```

### 3. Run Server

**Development (with auto-reload):**
```bash
uvicorn backend.app:app --reload
```

**Production (with Gunicorn):**
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.app:app
```

## API Endpoints

### POST /api/query

Submit a question to the RAG system.

**Request:**
```json
{
  "question": "What is Physical AI?",
  "top_k": 5,
  "include_context": true
}
```

**Response:**
```json
{
  "question": "What is Physical AI?",
  "context": "## Context from Documentation\n...",
  "sources": [
    {
      "url": "https://example.com/docs/intro",
      "section": "Foundations",
      "score": 0.95
    }
  ],
  "metadata": {
    "model": "embed-english-v3.0",
    "context_chunks": 5,
    "query_succeeded": true
  }
}
```

### GET /api/health

Check service health.

**Response:**
```json
{
  "status": "healthy",
  "cohere": "connected",
  "qdrant": "connected",
  "model": "embed-english-v3.0"
}
```

### GET /api/info

Get service information.

**Response:**
```json
{
  "name": "RAG Chatbot API",
  "version": "1.0.0",
  "model": "embed-english-v3.0",
  "collection": {
    "name": "documents",
    "points_count": 287,
    "vectors_count": 287
  }
}
```

### GET /

Root endpoint with service links.

## Documentation

- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Usage Examples

### Python Client

```python
import requests

url = "http://localhost:8000/api/query"
payload = {
    "question": "What is Physical AI?",
    "top_k": 5
}

response = requests.post(url, json=payload)
print(response.json())
```

### cURL

```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is Physical AI?",
    "top_k": 5,
    "include_context": true
  }'
```

### JavaScript/Fetch

```javascript
const response = await fetch('http://localhost:8000/api/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: 'What is Physical AI?',
    top_k: 5,
    include_context: true
  })
});

const data = await response.json();
console.log(data);
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `QDRANT_URL` | Yes | - | Qdrant instance URL |
| `QDRANT_API_KEY` | Yes | - | Qdrant API key |
| `QDRANT_COLLECTION_NAME` | No | `documents` | Collection name |
| `COHERE_API_KEY` | Yes | - | Cohere API key |

## Architecture

### Request Flow

```
Request
   ↓
Query Validation (Pydantic)
   ↓
Embed Question (Cohere)
   ↓
Search Qdrant (Vector DB)
   ↓
Format Context
   ↓
Build Response
   ↓
Return JSON
```

### Components

1. **FastAPI App** (`app.py`)
   - Lifespan management (startup/shutdown)
   - CORS configuration
   - Error handling
   - Middleware setup

2. **Routes** (`api/routes.py`)
   - Request/response models
   - Endpoint definitions
   - Input validation
   - Error responses

3. **RAG Service** (`services/rag_service.py`)
   - Question embedding
   - Context retrieval
   - Context formatting
   - Query orchestration

4. **Qdrant Service** (`services/qdrant_service.py`)
   - Vector search
   - Collection management
   - Health checks
   - Error handling

## Error Handling

All endpoints return proper HTTP status codes:

| Status | Meaning | Example |
|--------|---------|---------|
| 200 | Success | Query processed |
| 400 | Bad Request | Invalid question |
| 500 | Server Error | Service unavailable |
| 503 | Service Unavailable | Qdrant down |

Error responses include descriptive messages:
```json
{
  "detail": "Question is too short (minimum 3 characters)"
}
```

## Logging

All operations are logged with timestamps and levels:

```
2024-01-15 10:30:45 - backend.app - INFO - Starting RAG Chatbot API...
2024-01-15 10:30:46 - backend.services.qdrant_service - INFO - Connected to Qdrant
2024-01-15 10:30:47 - backend.api.routes - INFO - Received query: What is Physical AI?
```

## Performance Considerations

1. **Batch Queries**: Use reasonable `top_k` values (5-20)
2. **Timeout**: Requests timeout after 30 seconds
3. **Concurrency**: Handles multiple concurrent requests
4. **Caching**: No built-in caching (consider adding Redis)

## Security

- ✅ Environment-based secrets (no hardcoding)
- ✅ Input validation with Pydantic
- ✅ CORS for cross-origin requests
- ✅ Error messages don't expose internals
- ✅ Logging excludes sensitive data

## Testing

Run basic health check:

```bash
# Start server
uvicorn backend.app:app --reload

# In another terminal
curl http://localhost:8000/api/health
```

## Troubleshooting

### Connection refused
```
Error: Failed to connect to Qdrant
→ Check QDRANT_URL and QDRANT_API_KEY
→ Verify Qdrant instance is running
```

### API key error
```
Error: Unauthorized
→ Check COHERE_API_KEY is valid
→ Verify Cohere account has credits
```

### No results
```
Result: context_chunks: 0
→ Check collection has data
→ Verify collection name matches
→ Run RAG pipeline ingestion first
```

## Production Deployment

### Using Gunicorn + Uvicorn

```bash
# Install
pip install gunicorn uvicorn

# Run with 4 workers
gunicorn -w 4 -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  backend.app:app
```

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ ./backend/
COPY rag_pipeline/ ./rag_pipeline/

CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0"]
```

### Environment Best Practices

- Store secrets in `.env` (not in git)
- Use managed secrets in production (AWS Secrets Manager, etc.)
- Rotate API keys regularly
- Monitor API usage

## Support

For issues or questions:
1. Check logs in console output
2. Review API documentation at `/docs`
3. Verify environment variables are set
4. Test Qdrant and Cohere connectivity separately

## License

See main project LICENSE file.
