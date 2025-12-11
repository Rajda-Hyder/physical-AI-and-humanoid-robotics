# Quick Start Guide: Frontend-Backend Integration

**Feature**: 4-frontend-integration
**Date**: 2025-12-11
**Status**: Phase 1 - Setup Instructions

---

## 5-Minute Setup

This guide gets you running the RAG chatbot frontend and backend locally.

### Prerequisites

- Node.js 16+ and npm 8+
- Python 3.11+
- Git
- A text editor (VS Code recommended)

### Step 1: Clone the Repository

```bash
git clone https://github.com/panaversity/rag-chatbot.git
cd rag-chatbot
```

### Step 2: Set Up Backend (FastAPI)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run migrations (if needed)
python -m alembic upgrade head

# Start backend server
uvicorn main:app --reload
# Backend runs at: http://localhost:8000
```

**Verify backend is working:**
```bash
curl http://localhost:8000/api/v1/health
# Expected: {"status": "healthy"}
```

### Step 3: Set Up Frontend (Docusaurus)

In a new terminal (keep backend running):

```bash
# Navigate to frontend directory
cd docusaurus-site

# Install dependencies
npm install

# Create .env.local file
cp .env.example .env.local

# Edit .env.local if needed
# REACT_APP_API_URL=http://localhost:8000

# Start development server
npm start
# Frontend runs at: http://localhost:3000
```

**Verify frontend is working:**
- Open http://localhost:3000 in your browser
- You should see the Docusaurus site
- Look for the chat widget (button or icon on the page)

### Step 4: Test the Chat Widget

1. Click the chat widget icon/button (usually bottom-right or persistent sidebar)
2. Type a question: "What is physical AI?"
3. Click "Send" or press Enter
4. You should see:
   - Loading spinner while processing
   - Response text from the RAG system
   - Source links below the response
5. Click a source link to navigate to that documentation section

**Success indicators:**
- ✅ Chat widget opens
- ✅ Query sends without errors
- ✅ Response displays in 2-5 seconds
- ✅ Source links work and navigate correctly
- ✅ Error messages display if backend is down

---

## Configuration

### Frontend Environment Variables

Create `docusaurus-site/.env.local`:

```bash
# Backend API URL
REACT_APP_API_URL=http://localhost:8000

# Request timeout (milliseconds)
REACT_APP_API_TIMEOUT=30000

# Enable streaming responses (SSE)
REACT_APP_STREAM_MODE=false

# Debug logging
REACT_APP_DEBUG=true
```

### Backend Environment Variables

Create `backend/.env`:

```bash
# Database URL (PostgreSQL or SQLite for dev)
DATABASE_URL=sqlite:///./chat.db

# OpenAI API key
OPENAI_API_KEY=sk-...

# Qdrant vector database
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=documents

# CORS settings
CORS_ORIGINS=http://localhost:3000

# API settings
API_TIMEOUT=30
MAX_QUERY_LENGTH=10000

# Logging
LOG_LEVEL=INFO
DEBUG=false
```

---

## Common Tasks

### Check Backend Health

```bash
# Health check endpoint
curl http://localhost:8000/api/v1/health

# List available endpoints
curl http://localhost:8000/docs
# Opens interactive API documentation at http://localhost:8000/docs
```

### View Frontend Debug Logs

1. Open browser Developer Tools (F12)
2. Go to Console tab
3. Type: `localStorage.REACT_APP_DEBUG = 'true'`
4. Reload page
5. Chat operations will log to console

### Debug Network Requests

1. Open browser Developer Tools (F12)
2. Go to Network tab
3. Type a query in the chat widget
4. Observe POST request to `/api/v1/query`
5. Click request to see headers, body, response

### Restart Backend

```bash
# Kill the running process
# Ctrl+C in the backend terminal

# Then restart
uvicorn main:app --reload
```

### Clear Chat History

```javascript
// In browser console
localStorage.removeItem('chatHistory')
location.reload()
```

---

## Troubleshooting

### Chat Widget Not Appearing

**Issue**: Chat widget not visible on page

**Solutions**:
1. Check browser console for errors (F12 → Console)
2. Verify Docusaurus started successfully (`npm start` output)
3. Check `.env.local` exists with correct values
4. Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)

### "Cannot reach backend" Error

**Issue**: Chat shows "Service unavailable" or network error

**Solutions**:
1. Verify backend is running: `curl http://localhost:8000/api/v1/health`
2. Check `REACT_APP_API_URL` in `.env.local` matches backend URL
3. Verify CORS is enabled in backend `.env` (should include localhost:3000)
4. Check firewall isn't blocking port 8000
5. Backend error log: `python -m uvicorn main:app --reload` (shows errors)

### Slow Responses (>5 seconds)

**Issue**: Backend takes too long to respond

**Solutions**:
1. Check backend logs for slowness
2. Verify Qdrant is running and responsive
3. Check system resources (CPU, memory)
4. Try a simpler query with fewer words
5. Check internet connection (if using cloud API)

### "Query exceeds maximum length" Error

**Issue**: Error when typing long questions

**Solutions**:
1. Shorten the query to <10,000 characters
2. Split into multiple questions
3. Check `MAX_QUERY_LENGTH` in backend `.env`

### TypeScript Errors in Editor

**Issue**: Editor shows red squiggles in `*.tsx` files

**Solutions**:
1. Run: `npm install --save-dev @types/react @types/react-dom`
2. Verify `tsconfig.json` exists in docusaurus-site
3. Restart editor/IDE
4. Run: `npm run type-check`

---

## File Structure

```
project-root/
├── backend/                          # FastAPI backend (Spec 3)
│   ├── main.py                      # Entry point
│   ├── src/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       └── query.py         # /api/v1/query endpoint
│   │   ├── models/
│   │   └── services/
│   ├── requirements.txt              # Python dependencies
│   ├── .env.example                  # Backend config template
│   └── tests/
│
├── docusaurus-site/                 # Frontend (Docusaurus + Chat Widget)
│   ├── src/
│   │   ├── components/
│   │   │   └── ChatWidget.tsx       # Main widget component
│   │   ├── pages/
│   │   └── theme/
│   │       └── Root.tsx             # Root wrapper (chat injection point)
│   ├── docs/                         # Documentation content
│   ├── package.json                  # Dependencies
│   ├── docusaurus.config.js          # Docusaurus config
│   ├── .env.example                  # Frontend config template
│   └── tests/
│
└── specs/4-frontend-integration/    # Planning artifacts (this feature)
    ├── spec.md                       # Requirements
    ├── plan.md                       # Architecture
    ├── research.md                   # Technology decisions
    ├── data-model.md                 # Type definitions
    ├── quickstart.md                 # This file
    ├── contracts/                    # API schemas
    │   ├── openapi.yaml             # OpenAPI/Swagger spec
    │   └── types.ts                 # TypeScript types
    └── tasks.md                      # Implementation tasks
```

---

## Development Workflow

### Making Changes to Chat Widget

1. Edit component files in `docusaurus-site/src/components/ChatWidget.tsx`
2. Changes hot-reload automatically (thanks to Docusaurus dev server)
3. Check browser console (F12 → Console) for errors
4. Test in browser at http://localhost:3000

### Making Changes to Backend

1. Edit files in `backend/src/`
2. Server auto-reloads (thanks to `--reload` flag)
3. Check terminal for errors
4. API docs update at http://localhost:8000/docs

### Testing Locally

```bash
# Frontend tests
cd docusaurus-site
npm test

# Backend tests
cd backend
pytest tests/ -v

# End-to-end tests (optional)
npm run test:e2e
```

---

## Performance Tips

### Faster Builds

```bash
# Frontend: Skip type checking during dev
npm start --skip-tsc

# Backend: Use uvicorn workers for faster requests
uvicorn main:app --workers 4
```

### Better Debugging

```bash
# Backend: Enable SQL query logging
# In .env
SQLALCHEMY_ECHO=true

# Frontend: Enable Redux DevTools
# In browser, install Redux DevTools extension
```

### Reduced Bundle Size

```bash
# Analyze bundle size
cd docusaurus-site
npm run build
npm install -D webpack-bundle-analyzer
npx webpack-bundle-analyzer build/path
```

---

## Deployment Checklist

Before deploying to production:

- [ ] `.env` file removed from version control (use `.env.example`)
- [ ] All environment variables documented in `.env.example`
- [ ] Backend CORS configured for production domain
- [ ] Frontend `REACT_APP_API_URL` points to production backend
- [ ] Tests passing: `npm test` and `pytest tests/`
- [ ] Build succeeds: `npm run build`
- [ ] No console errors in browser (F12 → Console)
- [ ] No warnings in backend logs
- [ ] Performance metrics met (SC-001 through SC-010)
- [ ] Accessibility audit passes (axe DevTools)
- [ ] Source URLs work correctly

---

## Next Steps

1. **Explore the API**: http://localhost:8000/docs (interactive Swagger UI)
2. **Review type definitions**: `specs/4-frontend-integration/contracts/types.ts`
3. **Read implementation plan**: `specs/4-frontend-integration/plan.md`
4. **Check data model**: `specs/4-frontend-integration/data-model.md`
5. **View tasks**: `specs/4-frontend-integration/tasks.md`

---

## Getting Help

- **Backend issues**: Check `backend/` README
- **Frontend issues**: Check `docusaurus-site/` README
- **Architecture questions**: See `specs/4-frontend-integration/plan.md`
- **Type definitions**: See `specs/4-frontend-integration/contracts/types.ts`
- **API contract**: See `specs/4-frontend-integration/contracts/openapi.yaml`

---

## Quick Reference Commands

```bash
# Terminal 1: Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload

# Terminal 2: Frontend
cd docusaurus-site
npm install
cp .env.example .env.local
npm start

# Test both
# In docusaurus-site
npm test

# In backend
pytest tests/ -v
```

---

**Status**: ✅ Setup guide complete - Ready for implementation
**Last Updated**: 2025-12-11
