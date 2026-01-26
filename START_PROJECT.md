# Project Startup Instructions

## Prerequisites
- Python 3.11+ (backend)
- Node.js 18+ (frontend)
- pnpm (frontend package manager)

## Environment Setup

### Backend Environment Variables
Create `.env` file in project root with:
```bash
QDRANT_API_KEY="your-qdrant-api-key"
QDRANT_URL="your-qdrant-url"
COHERE_API_KEY="your-cohere-api-key"
QDRANT_COLLECTION_NAME="documents"
```

### Frontend Environment Variables
Create `.env.local` file in project root with:
```bash
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
VITE_DEBUG=true

VITE_FIREBASE_API_KEY="your-firebase-api-key"
VITE_FIREBASE_AUTH_DOMAIN="your-project.firebaseapp.com"
VITE_FIREBASE_PROJECT_ID="your-project-id"
VITE_FIREBASE_STORAGE_BUCKET="your-project.firebasestorage.app"
VITE_FIREBASE_MESSAGING_SENDER_ID="your-sender-id"
VITE_FIREBASE_APP_ID="your-app-id"
```

## Start Backend (Terminal 1)

```bash
# Navigate to backend
cd backend

# Activate virtual environment
source .venv/bin/activate

# Install dependencies (if needed)
pip install -r requirements.txt

# Start FastAPI server
python -m backend.app
# OR
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

Backend will run on: http://localhost:8000
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

## Start Frontend (Terminal 2)

```bash
# Install dependencies (if needed)
pnpm install

# Start Docusaurus development server
pnpm start
```

Frontend will run on: http://localhost:3000

## Testing the Connection

### Test Backend Only
```bash
node test-backend-connection.js
```

### Test Full Stack
1. Start backend in Terminal 1
2. Start frontend in Terminal 2
3. Open http://localhost:3000 in browser
4. Navigate to chat interface
5. Send a test message: "What is Physical AI?"

## Common Issues

### Backend Issues
- **Port 8000 in use**: Kill process on port 8000 or change port in `.env.local`
- **Missing dependencies**: Run `pip install -r requirements.txt`
- **Environment variables**: Ensure `.env` file exists with correct values

### Frontend Issues
- **TypeScript errors**: Run `npx tsc --noEmit` to check
- **Port 3000 in use**: Docusaurus will prompt to use another port
- **Missing dependencies**: Run `pnpm install`
- **Environment variables**: Ensure `.env.local` exists

## API Request/Response Format

### Request to `/api/query` (POST)
```json
{
  "question": "What is Physical AI?",
  "top_k": 5,
  "include_context": true
}
```

### Response from `/api/query`
```json
{
  "question": "What is Physical AI?",
  "context": "Physical AI refers to...",
  "sources": [
    {
      "url": "https://example.com/doc",
      "section": "Introduction",
      "score": 0.95
    }
  ],
  "metadata": {
    "timestamp": 1234567890,
    "model": "embed-english-v3.0",
    "context_chunks": 5
  }
}
```

## Production Deployment

### Backend
- Deploy to Railway, Render, or similar
- Set environment variables in deployment platform
- Update `VITE_API_URL` in frontend `.env.local`

### Frontend
- Build: `pnpm build`
- Deploy: `pnpm deploy` or upload `build/` to static hosting
- Update `docusaurus.config.js` with production URL

## Files Modified

### Backend
- No changes required - backend was already correct

### Frontend
1. **src/services/api-client.ts**
   - Removed `conversation_id` and `context` from QueryRequest interface
   - Removed these fields from payload sent to backend
   - Fixed health endpoint path from `/api/v1/health` to `/api/health`

2. **src/hooks/useChat.ts**
   - Removed `context` parameter from request payload

3. **src/config/env.ts**
   - Fixed default baseUrl from `https://localhost:8000` to `http://localhost:8000`

4. **.env.local**
   - Changed API URL from Railway production URL to local: `http://localhost:8000`

5. **Cleaned up**
   - Removed `tsconfig.json.save` (backup file)
   - Removed `src/env.d.ts` (duplicate of `src/vite-env.d.ts`)
   - Removed `docusaurus.config.js.save` (backup file)

## Architecture

```
┌─────────────────┐         ┌─────────────────┐
│   Frontend      │  HTTP   │    Backend      │
│  (Docusaurus)   ├────────▶│   (FastAPI)     │
│  localhost:3000 │         │  localhost:8000 │
└─────────────────┘         └────────┬────────┘
                                     │
                            ┌────────┴────────┐
                            │                 │
                      ┌─────▼─────┐    ┌─────▼─────┐
                      │  Qdrant   │    │  Cohere   │
                      │  Vector   │    │    API    │
                      │    DB     │    │           │
                      └───────────┘    └───────────┘
```
