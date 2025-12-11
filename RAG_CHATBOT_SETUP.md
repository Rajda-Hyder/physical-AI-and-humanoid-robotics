# RAG Chatbot Integration - Complete Setup Guide

**Date**: 2025-12-11
**Status**: ✅ Implementation Complete
**Tested**: FastAPI Backend + Docusaurus Frontend Integration

---

## 📋 Overview

This document provides complete setup instructions for the fully-functional RAG (Retrieval-Augmented Generation) Chatbot system integrating:

- **Backend**: FastAPI + Cohere Embeddings + Qdrant Vector DB
- **Frontend**: Docusaurus React Chat Widget
- **Integration**: CORS-enabled HTTP API with local and production support

---

## 🏗️ Architecture

```
┌─────────────────────────────┐
│  Docusaurus Frontend        │
│  - React Chat Widget        │
│  - useChat Hook             │
│  - API Client               │
└──────────────┬──────────────┘
               │ HTTP POST to /api/v1/query
               ▼
┌─────────────────────────────┐
│  FastAPI Backend            │
│  - Query Endpoint           │
│  - RAG Agent                │
│  - Context Injection        │
└──────────────┬──────────────┘
               │ Retrieves context
               ▼
┌─────────────────────────────┐
│  Qdrant Vector Database     │
│  - Document embeddings      │
│  - Semantic search          │
│  - Context chunks           │
└─────────────────────────────┘
```

---

## ⚙️ Prerequisites

### System Requirements
- **Python**: 3.9+
- **Node.js**: 18+
- **pnpm**: 8+ (or npm/yarn)

### API Keys Required
- **QDRANT_API_KEY**: From Qdrant Cloud dashboard
- **QDRANT_URL**: Your Qdrant instance URL
- **COHERE_API_KEY**: From Cohere dashboard

---

## 🚀 Quick Start (5 minutes)

### Step 1: Set Up Environment Variables

Copy the backend environment file:
```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` with your API keys:
```env
QDRANT_API_KEY="your-qdrant-api-key"
QDRANT_URL="https://your-instance.cloud.qdrant.io:6333"
COHERE_API_KEY="your-cohere-api-key"
```

### Step 2: Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 3: Start Backend Server

```bash
# From backend directory
cd backend
python -m uvicorn main:app --reload --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
✅ RAG Chatbot API is running!
```

### Step 4: Set Up Frontend Environment

```bash
# From project root
cat > .env.local << EOF
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=30000
REACT_APP_DEBUG=true
EOF
```

### Step 5: Start Frontend

```bash
# From project root (where package.json is)
pnpm install
pnpm start
```

The site will open at `http://localhost:3000`.

### Step 6: Test the Chat Widget

1. **Open** http://localhost:3000 in your browser
2. **Find** the chat widget (bottom-right corner, minimized purple button)
3. **Click** the button to expand the chat
4. **Type** a question: "What is physical AI?"
5. **Send** and wait for response

**Expected behavior**:
- ✅ Chat opens without errors
- ✅ Message appears in chat
- ✅ Loading spinner shows
- ✅ Response displays within 5 seconds
- ✅ Sources appear below answer
- ✅ Source links are clickable

---

## 📁 Project Structure

```
project-root/
├── backend/                              # FastAPI Backend
│   ├── main.py                          # Entry point
│   ├── requirements.txt                  # Dependencies
│   ├── .env.example                      # Config template
│   └── src/
│       ├── api/
│       │   └── routes.py                # API endpoints
│       ├── services/
│       │   ├── retrieval.py             # Qdrant retrieval
│       │   └── agent.py                 # RAG agent
│       ├── models/
│       │   ├── requests.py              # Request schemas
│       │   └── responses.py             # Response schemas
│       └── config/
│           └── settings.py              # Environment config
│
├── src/                                  # Frontend (Docusaurus)
│   ├── components/
│   │   └── ChatWidget/
│   │       ├── ChatWidget.tsx           # Main widget
│   │       └── ChatWidget.css           # Styles
│   ├── hooks/
│   │   └── useChat.ts                   # Chat state hook
│   ├── services/
│   │   └── api-client.ts                # API client
│   └── theme/
│       └── Root.tsx                     # App root (chat injected here)
│
├── docs/                                 # Documentation content
├── .env                                  # Frontend env (local)
└── .env.example                          # Frontend env template
```

---

## 🔧 Configuration

### Backend Configuration (`backend/.env`)

| Variable | Description | Example |
|----------|-------------|---------|
| `QDRANT_API_KEY` | Qdrant authentication key | `eyJhbGc...` |
| `QDRANT_URL` | Qdrant instance URL | `https://instance.cloud.qdrant.io:6333` |
| `COHERE_API_KEY` | Cohere API key for embeddings | `cOJJwavk...` |
| `QDRANT_COLLECTION_NAME` | Document collection name | `documents` |
| `EMBEDDING_MODEL` | Cohere embedding model | `embed-english-v3.0` |
| `EMBEDDING_DIMENSION` | Embedding vector dimension | `1024` |
| `API_HOST` | API bind address | `0.0.0.0` |
| `API_PORT` | API port | `8000` |
| `API_TIMEOUT` | Request timeout (seconds) | `30` |
| `DEBUG` | Enable debug logging | `true` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Frontend Configuration (`.env.local`)

| Variable | Description | Example |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend API URL | `http://localhost:8000` |
| `REACT_APP_API_TIMEOUT` | Request timeout (ms) | `30000` |
| `REACT_APP_DEBUG` | Enable debug logging | `true` |

---

## 🧪 Testing the System

### Health Check

```bash
# Test backend is running
curl http://localhost:8000/api/v1/health

# Expected response:
# {
#   "status": "healthy",
#   "version": "1.0.0",
#   "service": "RAG Chatbot API"
# }
```

### API Information

```bash
curl http://localhost:8000/api/v1/info

# Shows available endpoints and integrations
```

### Test Query (curl)

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is physical AI?",
    "context": null,
    "stream": false
  }'

# Expected response:
# {
#   "response_id": "uuid...",
#   "answer": "Physical AI refers to...",
#   "context_chunks": [...],
#   "metadata": {...}
# }
```

### Test from Browser Console

```javascript
// In browser console (F12 → Console) on localhost:3000
const response = await fetch('http://localhost:8000/api/v1/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: 'What is physical AI?' })
})
const data = await response.json()
console.log(data)
```

---

## 🐛 Troubleshooting

### Backend Issues

**Error**: `QDRANT_API_KEY environment variable is required`
- **Solution**: Add keys to `backend/.env` file
- **Verify**: `cat backend/.env` shows all three API keys

**Error**: `Failed to connect to Qdrant`
- **Solution**: Check `QDRANT_URL` is correct and accessible
- **Verify**: `curl -H "Authorization: Bearer $QDRANT_API_KEY" "$QDRANT_URL/health"`

**Error**: `ImportError: No module named 'qdrant_client'`
- **Solution**: Install dependencies: `pip install -r backend/requirements.txt`

**Backend won't start on port 8000**
- **Solution**: Check port is free: `lsof -i :8000` and kill if needed
- **Alternative**: Change `API_PORT` in `.env` to different port (e.g., 8001)

### Frontend Issues

**Chat widget not appearing**
- **Solution**: Check browser console (F12 → Console) for errors
- **Verify**: Docusaurus started without errors (`pnpm start`)
- **Check**: `.env.local` exists with `REACT_APP_API_URL`

**"Cannot reach backend" error in chat**
- **Verify**: Backend is running: `curl http://localhost:8000/api/v1/health`
- **Check**: `REACT_APP_API_URL` in `.env.local` is correct
- **Solution**: CORS might be blocked - check browser console for CORS error

**"Request timeout" in chat**
- **Cause**: Backend taking >30 seconds to respond
- **Solution**: Increase `REACT_APP_API_TIMEOUT` in `.env.local` (milliseconds)
- **Debug**: Check backend logs for slowness

**Module not found error in TypeScript**
- **Solution**: Clear build cache: `rm -rf .docusaurus build node_modules`
- **Reinstall**: `pnpm install && pnpm start`

---

## 📝 API Endpoints

### POST `/api/v1/query`

**Submit a query to the RAG chatbot**

**Request**:
```json
{
  "query": "What is physical AI?",
  "context": null,
  "conversation_id": null,
  "stream": false
}
```

**Response (200)**:
```json
{
  "response_id": "550e8400-e29b-41d4-a716-446655440000",
  "answer": "Physical AI refers to...",
  "context_chunks": [
    {
      "source_url": "/docs/chapter-1/intro#physical-ai",
      "relevance_score": 0.95,
      "text": "Physical AI (or embodied AI) refers to...",
      "metadata": {
        "title": "Introduction to Physical AI",
        "chapter": "Chapter 1"
      }
    }
  ],
  "metadata": {
    "model": "cohere-command-r-plus",
    "tokens_used": 156,
    "response_time_ms": 2341,
    "timestamp": 1702329603000,
    "version": "1.0.0"
  }
}
```

**Error Responses**:
- **400**: Bad request (invalid query)
- **422**: Unprocessable entity (query too long)
- **500**: Server error (processing failed)
- **503**: Service unavailable (Qdrant down)

---

## 🌐 Deployment

### Production Setup

1. **Update Backend URL**:
   ```bash
   # In .env or deploy environment
   REACT_APP_API_URL=https://api.yourdomain.com
   ```

2. **Update CORS Origins** in `backend/main.py`:
   ```python
   cors_origins = [
       "https://yourdomain.com",
       "https://www.yourdomain.com",
   ]
   ```

3. **Enable HTTPS** for frontend and backend

4. **Build Frontend**:
   ```bash
   pnpm build
   # Output in build/ directory, ready for deployment
   ```

5. **Deploy Backend**:
   ```bash
   # Using Docker, Heroku, AWS Lambda, or your platform
   # Ensure environment variables are set
   ```

---

## 📊 Monitoring

### View Backend Logs

```bash
# If running locally
# Logs appear in terminal where backend is running

# For production, check service logs:
# Docker: docker logs container-id
# Heroku: heroku logs --tail
# AWS CloudWatch: Review log streams
```

### Debug Mode

Enable debug logging in both frontend and backend:

**Frontend**:
```bash
# .env.local
REACT_APP_DEBUG=true
```

**Backend**:
```bash
# backend/.env
DEBUG=true
LOG_LEVEL=DEBUG
```

Then check browser console and backend logs for detailed information.

---

## 🧠 How It Works

### Query Flow

1. **User Types Question** → Chat Widget captures input
2. **Send to Backend** → API Client POSTs to `/api/v1/query`
3. **Retrieve Context** → Qdrant searches for relevant documents
4. **Generate Response** → Cohere API creates grounded answer
5. **Display Response** → Chat Widget shows answer + sources
6. **Show Sources** → User can click links to view original content

### Selected Text Feature

1. User selects text from documentation
2. Clicks "📌 Selected Text" button
3. Selected text is added as context
4. Query sent with context to backend
5. RAG agent generates more focused response

---

## ✅ Verification Checklist

- [ ] Backend `.env` has all three API keys
- [ ] Backend starts without errors: `python -m uvicorn main:app --reload`
- [ ] Backend health check passes: `curl http://localhost:8000/api/v1/health`
- [ ] Frontend starts: `pnpm start` opens http://localhost:3000
- [ ] Chat widget visible on page (bottom-right, purple button)
- [ ] Chat widget opens when clicked
- [ ] Can type in chat input
- [ ] Query sends and shows loading indicator
- [ ] Response displays within 5 seconds
- [ ] Sources appear and are clickable
- [ ] Selected text button works
- [ ] No errors in browser console (F12)
- [ ] No errors in backend terminal

---

## 🚨 Common Issues Summary

| Issue | Cause | Solution |
|-------|-------|----------|
| Backend won't start | Missing API keys | Add to `backend/.env` |
| "Cannot reach backend" | CORS blocked | Check API URL in `.env.local` |
| Chat not responding | API timeout | Increase `REACT_APP_API_TIMEOUT` |
| Empty responses | No context in Qdrant | Need to load documents first |
| Widget not showing | Module import error | Check `src/theme/Root.tsx` |
| TypeScript errors | Build cache corrupt | Delete `node_modules`, rebuild |

---

## 📞 Support

For issues:
1. Check the **Troubleshooting** section above
2. Enable **Debug Mode** and review logs
3. Verify all **Prerequisites** are met
4. Run the **Verification Checklist**
5. Check backend and frontend logs for specific errors

---

## 📚 Documentation References

- **API Contracts**: `specs/4-frontend-integration/contracts/openapi.yaml`
- **Data Model**: `specs/4-frontend-integration/data-model.md`
- **Architecture Plan**: `specs/4-frontend-integration/plan.md`
- **Docusaurus Docs**: https://docusaurus.io/
- **FastAPI Docs**: http://localhost:8000/docs (when running)
- **Qdrant Docs**: https://qdrant.tech/documentation/
- **Cohere Docs**: https://docs.cohere.com/

---

**Status**: ✅ **READY FOR USE**
**Last Updated**: 2025-12-11
**Version**: 1.0.0
