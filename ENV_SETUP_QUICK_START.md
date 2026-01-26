# Quick Start: Environment Variables Setup

## 🚀 TL;DR - Get Running in 3 Steps

### Step 1: Create `.env.local`
```bash
cp .env.example .env.local
# Edit with your Firebase credentials
nano .env.local
```

### Step 2: Install & Start
```bash
pnpm install
pnpm start
```

### Step 3: Open Browser
Visit http://localhost:3000 - ChatWidget and Firebase auth should work!

---

## 📝 What to Put in `.env.local`

```bash
# Firebase Config (required)
VITE_FIREBASE_API_KEY=your_key_here
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_bucket.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id

# API Config (optional - defaults shown)
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
VITE_DEBUG=true
```

---

## ✅ Verify Setup

After `pnpm start`, check:

1. **No webpack.configure error** ✓
2. **Site loads at localhost:3000** ✓
3. **ChatWidget appears (bottom-right)** ✓
4. **Sign In button works** ✓ (if Firebase is configured)

---

## 🔗 Related Docs

- **DOCUSAURUS_V3_ENV_FIX.md** - Technical details of the fix
- **FIREBASE_BUILD_FIX.md** - Firebase import.meta error resolution
- **FRONTEND_CHATBOT_SETUP.md** - ChatWidget configuration
- **QUICK_START_CHATBOT.md** - 5-minute chatbot test guide

---

## ❓ Common Issues

| Issue | Solution |
|-------|----------|
| "env.ts not found" | Run `pnpm install` and `pnpm docusaurus clear` |
| Firebase shows "undefined" | Check `.env.local` has all Firebase values filled |
| ChatWidget won't connect | Verify `VITE_API_URL` points to running backend |
| `pnpm start` slow | First startup is slower; subsequent runs are faster |

---

## 🚢 Production Deploy

Set these environment variables in your hosting platform (Vercel, Netlify, etc.):
- `VITE_FIREBASE_API_KEY`
- `VITE_FIREBASE_AUTH_DOMAIN`
- `VITE_FIREBASE_PROJECT_ID`
- `VITE_FIREBASE_STORAGE_BUCKET`
- `VITE_FIREBASE_MESSAGING_SENDER_ID`
- `VITE_FIREBASE_APP_ID`
- `VITE_API_URL` (your backend URL)

Then run: `pnpm build`

The build will automatically load your platform's environment variables and embed them in the static files.

---

**Last Updated:** 2025-12-31
**Status:** ✅ Working - Build passes, dev server running
