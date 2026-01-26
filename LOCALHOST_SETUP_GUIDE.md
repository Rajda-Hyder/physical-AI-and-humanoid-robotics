# Quick Start: Localhost Frontend → Localhost Backend

## Prerequisites

- FastAPI backend running on `http://localhost:8000`
- Node.js/pnpm installed
- `.env.local` configured (already done)

---

## 1. Start Backend

```bash
# Terminal 1
cd backend
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

✅ Backend should print:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

## 2. Start Frontend Dev Server

```bash
# Terminal 2
npm start
# Or: pnpm start
```

✅ Frontend should print:
```
[INFO] ▸ Docusaurus server started on http://localhost:3000
```

---

## 3. Open Browser

Go to: **`http://localhost:3000`**

---

## 4. Verify Environment Configuration

### Check Console Log

Press `F12` → Console tab → Look for:

```
[ENV] Runtime environment initialized: {
  hostname: "localhost",
  env: {
    VITE_API_URL: "http://localhost:8000",
    VITE_DEBUG: "true"
  }
}
```

**If you see this → ✅ Environment correctly loaded**

---

## 5. Test ChatWidget

1. Scroll to bottom-right corner
2. Click ChatWidget (or it auto-opens if minimized=true is changed)
3. Type a test question: `"What is physical AI?"`
4. Submit

### Monitor Network Requests

Press `F12` → Network tab → Filter by `XHR` → Look for:

| Column | Expected Value |
|--------|-----------------|
| URL | `http://localhost:8000/api/v1/query/stream` |
| Status | `200` (success) or `202` (streaming) |
| Headers > Origin | `http://localhost:3000` |

✅ If status is 200/202 → Backend received the request
❌ If "Failed to fetch" → CORS issue

---

## 6. Troubleshooting

### Issue: "API BASE URL = http://127.0.0.1:8000" (not localhost)

Check what browser console shows in Network tab:
- If request still goes to **localhost** → OK, just the string repr differs
- If request fails → Need to fix

### Issue: CORS Error in Console

```
Access to XMLHttpRequest at 'http://localhost:8000/...'
from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Fix:** Add to `backend/app.py` CORS middleware:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: `window.__ENV__ is undefined`

1. Reload page (Ctrl+Shift+R to hard refresh)
2. Check that `/env.js` loads:
   - F12 → Network tab
   - Look for request to `/env.js`
   - Should return 200 with JavaScript code
3. If `/env.js` returns 404:
   - Verify `static/env.js` exists
   - Run: `npm run clear && npm start`

---

## Files in This Setup

| File | Purpose | Status |
|------|---------|--------|
| `.env.local` | Dev environment vars | ✅ Fixed |
| `static/env.js` | Runtime env loader | ✅ Created |
| `docusaurus.config.js` | Loads env.js in HTML head | ✅ Updated |
| `src/config/env.ts` | Type-safe env wrapper | ✅ Already correct |
| `src/services/api-client.ts` | Uses API_CONFIG | ✅ Updated |
| `src/theme/Root.tsx` | Passes API_CONFIG to ChatWidget | ✅ Updated |

---

## Expected Behavior

**Before (Broken):**
- Frontend at `localhost:3000`
- Always sent requests to Railway production URL
- No matter what `.env.local` said

**After (Fixed):**
- Frontend at `localhost:3000`
- Detects `localhost` hostname
- Automatically switches to `http://localhost:8000`
- ChatWidget sends request to local backend
- Everything works dev-locally without manual config

---

## Production Behavior (No Changes Needed)

When deployed to Railway:
1. Browser loads from Railway domain
2. `static/env.js` detects non-localhost hostname
3. Sets API URL to Railway backend automatically
4. Zero config needed for prod

---

## Test Checklist

- [ ] Backend running on `localhost:8000` (shows Uvicorn startup message)
- [ ] Frontend running on `localhost:3000` (shows Docusaurus startup message)
- [ ] Browser console shows `[ENV]` message with `localhost:8000`
- [ ] ChatWidget appears (bottom-right)
- [ ] Submit a test question
- [ ] Network tab shows request to `localhost:8000`
- [ ] Response received (no 404/500 errors)
- [ ] ChatWidget displays answer

If all checkmarks pass → ✅ **Everything is working!**
