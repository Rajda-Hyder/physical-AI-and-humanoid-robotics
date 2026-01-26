# Environment Configuration Guide

## Overview

This guide explains how environment variables work in your Docusaurus + FastAPI RAG chatbot system.

**Key principle:** Docusaurus can't read environment variables at runtime from `.env` files. Instead, we use a **static JavaScript file** that injects environment configuration into the browser.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│ File: static/env.js (PRODUCTION CODE)                   │
│ - Auto-detects dev vs production                         │
│ - Sets window.__ENV__ globally                           │
│ - Loaded FIRST in docusaurus.config.js                   │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ File: src/config/env.ts (TYPE-SAFE WRAPPER)              │
│ - Reads from window.__ENV__                              │
│ - Exports API_CONFIG and FIREBASE_CONFIG                │
│ - Used by all components                                │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Usage in Components:                                    │
│ - src/services/api-client.ts                            │
│ - src/theme/Root.tsx                                    │
│ - Any component importing API_CONFIG                    │
└─────────────────────────────────────────────────────────┘
```

---

## Files Modified

### 1. `.env.local` (Development Only)
**Path:** `/home/rajda/task_1/.env.local`

```env
# Dev Environment - Local Backend
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
VITE_DEBUG=true

# Firebase configs (loaded by Docusaurus at build time)
VITE_FIREBASE_API_KEY=AIzaSyBi4E3LKz2gvVpHRUSnLHbvdueysrwKZLY
VITE_FIREBASE_AUTH_DOMAIN=rag-chatbot-bf4d8.firebaseapp.com
# ... more Firebase vars
```

**When used:** Only during `docusaurus start` (dev server). Used by build process to seed initial values.

### 2. `static/env.js` (Runtime Configuration)
**Path:** `/home/rajda/task_1/static/env.js`

This is the **core of the solution**. It:
- ✅ Detects if running on `localhost` or `127.0.0.1` → dev mode
- ✅ Sets `window.__ENV__.VITE_API_URL` to local backend
- ✅ Sets production URL for Railway deployments
- ✅ Runs BEFORE any React code loads
- ✅ Works in both dev AND production

**Key logic:**
```javascript
const isDev = window.location.hostname === 'localhost' ||
              window.location.hostname === '127.0.0.1';

window.__ENV__.VITE_API_URL = isDev ? 'http://localhost:8000' :
                               'https://physical-ai-and-humanoid-robotics-production-e85e.up.railway.app';
```

### 3. `docusaurus.config.js` (Plugin Configuration)
**Path:** `/home/rajda/task_1/docusaurus.config.js`

Loads `static/env.js` as a script tag in the HTML head:

```javascript
plugins: [
  function envPlugin() {
    return {
      name: 'env-plugin',
      injectHtmlTags() {
        return {
          headTags: [
            {
              tagName: 'script',
              attributes: { src: '/env.js', async: false },
            },
          ],
        };
      },
    };
  },
],
```

**Why `async: false`?** Ensures `window.__ENV__` is set BEFORE React loads.

### 4. `src/config/env.ts` (Type-Safe Wrapper)
**Path:** `/home/rajda/task_1/src/config/env.ts`

Provides typed access to runtime environment:

```typescript
const env = typeof window !== 'undefined' ? window.__ENV__ || {} : {};

export const API_CONFIG = {
  baseUrl: env.VITE_API_URL || 'http://localhost:8000',
  timeout: Number.isFinite(Number(env.VITE_API_TIMEOUT))
    ? Number(env.VITE_API_TIMEOUT)
    : 30000,
  debug: env.VITE_DEBUG === 'true',
};
```

### 5. `src/services/api-client.ts` (API Client)
**Path:** `/home/rajda/task_1/src/services/api-client.ts`

Uses `API_CONFIG` instead of `import.meta.env`:

```typescript
export function getAPIClient(baseUrl?: string, timeout?: number) {
  if (!clientInstance) {
    clientInstance = new RAGChatAPIClient(
      baseUrl || API_CONFIG.baseUrl,        // ← Uses runtime config
      timeout || API_CONFIG.timeout
    )
  }
  return clientInstance;
}
```

### 6. `src/theme/Root.tsx` (Root Component)
**Path:** `/home/rajda/task_1/src/theme/Root.tsx`

Passes dynamic API URL to ChatWidget:

```typescript
import { API_CONFIG } from '../config/env';

const Root: React.FC<RootProps> = ({ children }) => {
  return (
    <BrowserOnly fallback={<div>{children}</div>}>
      {() => (
        <AuthProvider>
          {children}
          <ChatWidget
            apiUrl={API_CONFIG.baseUrl}    // ← Dynamic from config
            position="bottom-right"
            minimized={true}
          />
        </AuthProvider>
      )}
    </BrowserOnly>
  );
};
```

---

## Development Workflow

### Starting Local Development

```bash
# Terminal 1: Start FastAPI backend
cd backend
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000

# Terminal 2: Start Docusaurus dev server
npm start
# Or: pnpm start
```

**What happens:**
1. `.env.local` is loaded by Docusaurus build
2. Browser loads at `http://localhost:3000`
3. `static/env.js` runs in HTML head
4. Detects `localhost` → sets `window.__ENV__.VITE_API_URL = 'http://localhost:8000'`
5. React components read from `API_CONFIG.baseUrl`
6. ChatWidget calls `http://localhost:8000/api/v1/query/stream` ✅

### Expected Console Output

When dev server starts, you should see in browser console:

```
[ENV] Runtime environment initialized: {
  hostname: "localhost",
  env: {
    VITE_API_URL: "http://localhost:8000",
    VITE_DEBUG: "true"
  }
}
```

And when submitting a query:

```
API BASE URL = http://localhost:8000
[RAGChat] Submitting query: What is...
```

---

## Production Workflow

### Building for Production

```bash
npm run build
# Or: pnpm build
```

**What happens:**
1. Docusaurus generates static HTML in `build/`
2. `build/env.js` contains production defaults
3. Deployed to Railway
4. Browser loads at Railway URL (not localhost)
5. `static/env.js` detects production hostname
6. Sets `window.__ENV__.VITE_API_URL = 'https://physical-ai-and-humanoid-robotics-production-e85e.up.railway.app'`
7. ChatWidget calls Railway backend ✅

### Updating Production API URL

If Railway backend URL changes:

1. **Option A:** Update `static/env.js` production URL
   ```javascript
   const defaultProdUrl = 'https://new-railway-url.com';
   ```

2. **Option B:** Use Railway environment variables at build time (advanced)
   ```bash
   VITE_API_URL=https://new-url pnpm build
   ```

---

## Troubleshooting

### Issue: "Failed to fetch from `https://physical-ai-and-humanoid-robotics-production-e85e.up.railway.app`"

**Cause:** Frontend still using hardcoded Railway URL despite `.env.local`

**Fix:**
- ✅ Verify `src/theme/Root.tsx` uses `API_CONFIG.baseUrl` (not hardcoded string)
- ✅ Verify `docusaurus.config.js` loads `static/env.js`
- ✅ Check browser console for `[ENV]` initialization message

### Issue: "API BASE URL = http://127.0.0.1:8000" instead of `localhost:8000`

**Cause:** Build-time vs runtime URL mismatch

**Fix:**
- Update `.env.local` to use exact hostname:
  ```env
  VITE_API_URL=http://localhost:8000
  ```

### Issue: CORS error from localhost frontend

**Cause:** Backend not allowing `http://localhost:3000`

**Fix:** Verify `backend/app.py` has CORS middleware:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        # ... other origins
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: `window.__ENV__` is undefined in browser console

**Cause:** `static/env.js` didn't load

**Fix:**
1. Check if `/env.js` returns 200 in Network tab
2. Verify `static/env.js` file exists
3. Clear Docusaurus cache:
   ```bash
   npm run clear
   npm start
   ```

---

## Environment Variable Reference

| Variable | Dev Value | Prod Value | Used In |
|----------|-----------|-----------|---------|
| `VITE_API_URL` | `http://localhost:8000` | Railway URL | API calls |
| `VITE_API_TIMEOUT` | `30000` | `30000` | Request timeouts |
| `VITE_DEBUG` | `true` | `false` | Console logging |
| `VITE_FIREBASE_*` | Local Firebase creds | Same (shared) | Firebase auth |

---

## Next Steps

✅ **Done:**
- Runtime environment injection working
- Dev server connects to `localhost:8000`
- Production uses Railway backend

**Verify it works:**

1. Start backend: `python -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000`
2. Start frontend: `npm start`
3. Open `http://localhost:3000`
4. Check browser console for `[ENV]` message
5. Send a query to ChatWidget
6. Verify request goes to `http://localhost:8000/api/v1/query/stream`

---

## Code References

- `src/config/env.ts:24` - API_CONFIG.baseUrl default
- `src/services/api-client.ts:137` - getAPIClient uses API_CONFIG
- `src/theme/Root.tsx:18` - ChatWidget receives API_CONFIG.baseUrl
- `docusaurus.config.js:88` - env.js script tag injection
- `static/env.js:20-21` - Runtime URL detection logic
