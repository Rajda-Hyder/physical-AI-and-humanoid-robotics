# Visual Solution Diagram

## Problem → Solution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    THE PROBLEM (Before)                         │
└─────────────────────────────────────────────────────────────────┘

Frontend (localhost:3000)
    │
    ├─ Tried import.meta.env ❌ (doesn't work in Docusaurus)
    ├─ Tried .env.local ❌ (ignored at runtime)
    └─ Had hardcoded Railway URL ❌ (always used production)

Result: Always sent requests to Railway, not localhost:8000 ❌


┌─────────────────────────────────────────────────────────────────┐
│                  THE SOLUTION (After)                           │
└─────────────────────────────────────────────────────────────────┘

HTML HEAD (runs first)
    │
    ├─ <script src="/env.js" async="false"></script>
    │
    └─→ static/env.js executes
         │
         ├─ Detects: window.location.hostname
         │
         ├─ If localhost:3000
         │  └─→ window.__ENV__.VITE_API_URL = 'http://localhost:8000'
         │
         └─ If Railway domain
            └─→ window.__ENV__.VITE_API_URL = 'https://railway-url.com'

REACT LOADS
    │
    ├─ Import src/config/env.ts
    │  └─→ Reads from window.__ENV__
    │  └─→ Exports API_CONFIG
    │
    ├─ Import src/services/api-client.ts
    │  └─→ Uses API_CONFIG.baseUrl
    │
    └─ Import src/theme/Root.tsx
       └─→ Passes API_CONFIG.baseUrl to ChatWidget

Result: ChatWidget uses correct backend automatically ✅
```

---

## Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                     Browser & HTML                                 │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  <html>                                                            │
│    <head>                                                          │
│      <script src="/env.js" async="false"></script> ← LOADS FIRST   │
│      <script src="/app.js"></script>              ← LOADS SECOND   │
│    </head>                                                         │
│    <body>                                                          │
│      <div id="root"></div>                                         │
│    </body>                                                         │
│  </html>                                                           │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────────┐
│                    static/env.js (44 lines)                        │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  (function() {                                                     │
│    const isDev = hostname === 'localhost' || === '127.0.0.1'      │
│                                                                    │
│    window.__ENV__ = {                                              │
│      VITE_API_URL: isDev ? 'localhost:8000' : 'railway-url',      │
│      VITE_DEBUG: isDev ? 'true' : 'false',                        │
│      // ... Firebase vars                                          │
│    }                                                              │
│  })()                                                              │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────────┐
│               React Component Tree Loads                           │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  App.tsx                                                           │
│    ├─ Root.tsx                                                    │
│    │   ├─ ChatWidget                                              │
│    │   │   └─ import { API_CONFIG }                               │
│    │   │       from '../config/env'                               │
│    │   └─ uses: apiUrl={API_CONFIG.baseUrl}                       │
│    │                                                              │
│    ├─ useChat() hook                                              │
│    │   └─ getAPIClient()                                          │
│    │       └─ uses: API_CONFIG.baseUrl                            │
│    │                                                              │
│    └─ components use: API_CONFIG.baseUrl                          │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────────┐
│              API Calls with Correct Backend URL                    │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  If localhost:3000                                                 │
│    └─→ POST http://localhost:8000/api/v1/query/stream             │
│                                                                    │
│  If Railway production                                             │
│    └─→ POST https://railway-url.com/api/v1/query/stream           │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagram

```
                    User opens browser
                            │
                            ↓
                  http://localhost:3000
                            │
                            ↓
              HTML loads with <script src="/env.js">
                            │
                            ├─ static/env.js runs FIRST
                            │   │
                            │   ├─ Check: window.location.hostname
                            │   │
                            │   ├─ If == 'localhost' or '127.0.0.1'
                            │   │   └─→ Set window.__ENV__.VITE_API_URL
                            │   │       = 'http://localhost:8000'
                            │   │
                            │   └─→ console.log('[ENV]...')
                            │
                            ↓
              React app loads (second script)
                            │
                            ├─ src/config/env.ts
                            │   │
                            │   └─→ API_CONFIG = {
                            │       baseUrl: window.__ENV__.VITE_API_URL,
                            │       ...
                            │   }
                            │
                            ├─ src/theme/Root.tsx
                            │   │
                            │   └─→ ChatWidget apiUrl={API_CONFIG.baseUrl}
                            │
                            ├─ src/services/api-client.ts
                            │   │
                            │   └─→ getAPIClient(API_CONFIG.baseUrl)
                            │
                            ↓
                    User types question
                            │
                            ↓
                  ChatWidget calls submitQuery()
                            │
                            ↓
          fetch(API_CONFIG.baseUrl + '/api/v1/query/stream')
                            │
                            ├─ Uses: http://localhost:8000
                            │
                            ↓
              Backend processes request on localhost:8000
                            │
                            ↓
                  Returns response (200 OK)
                            │
                            ↓
             ChatWidget displays answer to user ✅
```

---

## File Dependency Graph

```
docusaurus.config.js
    │
    ├─ Loads plugin: injectHtmlTags()
    │   └─ Injects: <script src="/env.js" async="false">
    │
    └─ Builds static/
        └─ Copies: static/env.js → build/env.js

build/env.js (runtime)
    │
    └─ Sets: window.__ENV__ (global)

src/config/env.ts
    │
    ├─ Reads: window.__ENV__
    │
    ├─ Exports: API_CONFIG
    │   └─ Used by many components
    │
    └─ Exports: FIREBASE_CONFIG
        └─ Used by auth components

src/services/api-client.ts
    │
    ├─ Imports: { API_CONFIG }
    │   from '../config/env'
    │
    ├─ Function: getAPIClient()
    │   └─ Uses: API_CONFIG.baseUrl
    │
    └─ Exported to: useChat hook

src/theme/Root.tsx
    │
    ├─ Imports: { API_CONFIG }
    │   from '../config/env'
    │
    ├─ Component: ChatWidget
    │   └─ Prop: apiUrl={API_CONFIG.baseUrl}
    │
    └─ Rendered: In every page

src/components/ChatWidget/ChatWidget.tsx
    │
    ├─ Receives: apiUrl prop
    │
    ├─ Imports: useChat hook
    │
    ├─ Calls: getAPIClient(apiUrl)
    │
    └─ Makes requests to: apiUrl + endpoints
```

---

## Environment Detection Flow

```
Browser loads page at: http://localhost:3000
                            │
                            ↓
        window.location.hostname = "localhost"
                            │
                            ↓
         static/env.js checks:
         const isDev = hostname === 'localhost' ||
                       hostname === '127.0.0.1'
                            │
        ┌───────────────────┴──────────────────┐
        │ isDev = true                         │
        ↓                                       ↓
   ✅ Development Mode                   ❌ Production Mode
        │                                     │
        ├─ VITE_API_URL =                      ├─ VITE_API_URL =
        │  'http://localhost:8000'             │  'https://railway-url'
        │                                     │
        ├─ VITE_DEBUG = 'true'                ├─ VITE_DEBUG = 'false'
        │                                     │
        └─ console.log('[ENV]...')            └─ (no debug logging)


        Browser console:                     Browser console:
        [ENV] Runtime initialized: {         (no [ENV] message)
          hostname: "localhost",
          env: {
            VITE_API_URL: "http://...",
            VITE_DEBUG: "true"
          }
        }
```

---

## Request Flow Comparison

### Before (Broken)

```
Browser (localhost:3000)
    │
    └─→ Hardcoded URL in Root.tsx
        └─→ "https://railway-url.com"
            │
            └─→ ChatWidget always uses Railway
                └─→ POST to https://railway-url.com/api/v1/query/stream
                    │
                    └─→ Response received ✅ (but it's production!)
```

### After (Fixed)

```
Browser (localhost:3000)
    │
    ├─→ static/env.js detects "localhost"
    │   └─→ Sets window.__ENV__.VITE_API_URL = "http://localhost:8000"
    │
    ├─→ src/config/env.ts reads window.__ENV__
    │   └─→ API_CONFIG.baseUrl = "http://localhost:8000"
    │
    └─→ ChatWidget uses API_CONFIG.baseUrl
        └─→ POST to http://localhost:8000/api/v1/query/stream
            │
            ├─→ Connects to local backend ✅
            ├─→ No CORS issues ✅
            └─→ Development works! ✅
```

---

## Environment Variable Inheritance

```
.env.local (file on disk)
│
├─ Only used during: npm start (dev build)
│
├─ Loads into: process.env (Node.js)
│
├─ But Docusaurus doesn't inject
│  these into the browser directly
│
└─ Instead uses: static/env.js

static/env.js (hardcoded values)
│
├─ Always loaded by: docusaurus.config.js plugin
│
├─ Runs in: Browser (window scope)
│
├─ Sets: window.__ENV__ (global object)
│
└─ Auto-detects: Dev vs Production

window.__ENV__ (runtime, in browser)
│
├─ Read by: src/config/env.ts
│
├─ Exported as: API_CONFIG
│
└─ Used by: All components and services
```

---

## Timeline: What Happens When

```
1. User types: npm start
   └─ Docusaurus dev server starts
   └─ Reads .env.local (build time)

2. Browser loads: http://localhost:3000
   └─ HTML arrives with <script src="/env.js">

3. Before React loads:
   └─ static/env.js runs (async: false)
   └─ Sets window.__ENV__
   └─ Console shows: [ENV] Runtime initialized

4. React loads:
   └─ Imports src/config/env.ts
   └─ API_CONFIG reads window.__ENV__
   └─ All components get correct baseUrl

5. User sends question:
   └─ ChatWidget calls getAPIClient()
   └─ Uses API_CONFIG.baseUrl
   └─ Requests go to localhost:8000 ✅

6. Backend responds:
   └─ Answer appears in ChatWidget
   └─ Everything works! ✅
```

---

## Success Criteria Visualized

```
✅ BEFORE YOU TEST
  ├─ [ ] .env.local is clean (no Python code)
  ├─ [ ] static/env.js exists (44 lines)
  ├─ [ ] docusaurus.config.js loads /env.js
  ├─ [ ] Root.tsx uses API_CONFIG.baseUrl
  └─ [ ] api-client.ts uses API_CONFIG

✅ DURING TESTING
  ├─ [ ] Backend runs: python -m uvicorn app:app --reload
  ├─ [ ] Frontend runs: npm start
  ├─ [ ] Browser: http://localhost:3000 opens
  ├─ [ ] Console: [ENV] message appears
  ├─ [ ] Console: API BASE URL = http://localhost:8000
  ├─ [ ] Network: Requests go to localhost:8000
  ├─ [ ] Response: Status 200 (not 404/500)
  └─ [ ] ChatWidget: Shows answer (not error)

✅ SUCCESS = All checked
```

---

## Summary Flowchart

```
                         START
                           │
                           ↓
                    Open localhost:3000
                           │
                           ↓
              ┌─────────────────────────┐
              │ static/env.js runs      │
              │ Detects: localhost      │
              │ Sets: API_URL localhost │
              └─────────────────────────┘
                           │
                           ↓
              ┌─────────────────────────┐
              │ React app loads         │
              │ Reads: window.__ENV__   │
              │ Exports: API_CONFIG     │
              └─────────────────────────┘
                           │
                           ↓
              ┌─────────────────────────┐
              │ ChatWidget mounted      │
              │ Receives: API_CONFIG    │
              │ Ready for queries       │
              └─────────────────────────┘
                           │
                           ↓
              ┌─────────────────────────┐
              │ User sends query        │
              │ Request to: localhost   │
              │ Backend processes       │
              │ Response received       │
              └─────────────────────────┘
                           │
                           ↓
                      ✅ SUCCESS
```

---

This visual guide shows:
1. The problem and solution
2. Architecture and dependencies
3. Data flow through the system
4. Environment detection logic
5. Request routing
6. Success criteria

Reference this when explaining the solution to others!
