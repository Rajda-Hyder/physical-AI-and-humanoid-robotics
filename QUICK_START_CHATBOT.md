# Quick Start: Test the Chatbot (5 Minutes)

## 🎯 Goal
Get the chatbot running locally and test it with your Railway backend.

---

## ⚡ Step 1: Start Frontend Dev Server (1 minute)

```bash
cd /home/rajda/task_1

# Install dependencies (first time only)
pnpm install

# Start dev server
pnpm dev
```

**Expected output:**
```
VITE v... ready in ... ms

➜  Local:   http://localhost:3000/
```

---

## 🌐 Step 2: Open in Browser (1 minute)

1. Open http://localhost:3000 in your browser
2. Look at the **bottom-right corner**
3. You should see a **📚 Textbook Assistant** button

**If you don't see it:**
- Press F12 to open Developer Tools
- Check Console tab for errors
- Verify `src/theme/Root.tsx` has ChatWidget import

---

## 💬 Step 3: Ask Your First Question (2 minutes)

**Click the chatbot button to expand it**

```
┌────────────────────────────────┐
│ 📚 Textbook Assistant      [−]  │
├────────────────────────────────┤
│                                │
│ 👋 Hello! Ask me anything     │
│    about the textbook.        │
│                                │
│ ┌──────────────────────────┐  │
│ │ Ask about the textbook.. │  │
│ │                          │  │
│ │                          │  │
│ └──────────────────────────┘  │
│ [📌 Selected] [✉️ Send]        │
└────────────────────────────────┘
```

**Type in the input box:**
```
What is Physical AI?
```

**Press Ctrl+Enter or click Send button**

---

## ✅ Step 4: Check the Answer (2 minutes)

You should see:

```
┌────────────────────────────────┐
│ 👤 You         2:34 PM         │
│ What is Physical AI?           │
│                                │
│ 🤖 Assistant   2:36 PM         │
│ Physical AI combines...        │
│ [more text...]                 │
│                                │
│ 📖 Sources (3)                 │
│ ▼ Click to expand sources      │
└────────────────────────────────┘
```

**Click "📖 Sources (3)" to see where answer came from:**

```
• Lesson 1.1: Intro to Physical AI
  Relevance: 95%
  
• Module 1: Foundations
  Relevance: 87%
  
• Lesson 1.2: Core Concepts
  Relevance: 82%
```

---

## 🚨 Step 5: Test Error Handling (Optional, 1 minute)

**Ask a question NOT in the book:**
```
What is the weather today?
```

**Expected error message:**
```
❌ Sorry, I cannot find the answer in the book.
```

This proves the chatbot is enforcing **book-content-only** mode ✅

---

## 📋 What Just Happened?

1. ✅ Frontend loaded successfully
2. ✅ ChatWidget injected on page
3. ✅ Connected to Railway backend
4. ✅ Sent question to `/api/query` endpoint
5. ✅ Received answer with sources
6. ✅ Displayed answer with source citations

---

## 🔧 Troubleshooting

### Problem: ChatWidget doesn't appear

**Check:**
```bash
# 1. Is dev server running?
# Look for "Local: http://localhost:3000"

# 2. Open browser console (F12)
# Look for errors

# 3. Refresh page (Ctrl+R)
```

---

### Problem: "Sorry, I cannot find the answer in the book" for book questions

**Check:**
```bash
# 1. Is Railway backend running?
curl http://physical-ai-and-humanoid-robotics-production-e85e.up.railway.app/api/health

# 2. Check browser network tab (F12 → Network)
# Look for POST request to /api/query
# Check response status: should be 200
```

---

### Problem: "An error occurred while processing your query"

**Check:**
```bash
# 1. Browser console (F12 → Console)
# Look for the actual error message

# 2. Is Railway URL correct?
# Should be: http://physical-ai-and-humanoid-robotics-production-e85e.up.railway.app
# Not: localhost:8000

# 3. Is Railway backend accessible?
curl http://physical-ai-and-humanoid-robotics-production-e85e.up.railway.app/
# Should return JSON, not error
```

---

## ✨ Features to Try

After your first question, try these:

### 1. **Multiple Questions**
Ask several questions in a row. Chat history is saved.

### 2. **Selected Text Context**
- Highlight text on the page
- Click "📌 Selected Text" button
- Ask a follow-up question
- The selected text is added as context

### 3. **Retry on Error**
- Stop your Railway backend temporarily
- Ask a question
- Get error message
- See "Retry" button
- Restart Railway
- Click Retry - it works!

### 4. **Navigate Between Pages**
- Ask a question
- Click to a different page (e.g., docs)
- Chat history persists
- Widget still works

### 5. **Minimize Widget**
- Click the [−] button in header
- Widget collapses to button only
- Click again to expand

---

## 📊 Response Times

Expected response times:
- **First request:** 2-3 seconds (cold start)
- **Subsequent requests:** 1-2 seconds (warm cache)

The widget shows a loading indicator while waiting.

---

## 🎓 What's Happening Under the Hood

```
1. You type: "What is Physical AI?"
2. Click Send
   ↓
3. Frontend sends to Railway backend:
   POST /api/query
   {
     "question": "What is Physical AI?",
     "top_k": 5,
     "include_context": true
   }
   ↓
4. Railway backend:
   - Embeds question with Cohere
   - Searches Qdrant vector DB
   - Generates answer
   - Returns with sources
   ↓
5. Frontend receives:
   {
     "question": "What is Physical AI?",
     "context": "Physical AI combines...",
     "sources": [
       {"url": "...", "section": "...", "score": 0.95},
       ...
     ]
   }
   ↓
6. Frontend validates:
   ✓ Has sources? YES → Show answer
   ✗ No sources? → Show error
   ↓
7. Display answer + sources with links
```

---

## 🎯 Success!

If you can:
✅ Open the chatbot
✅ Ask a question
✅ Get an answer with sources
✅ Get an error for non-book questions

**Then you're ready to deploy!** 🚀

---

## 📚 Next Steps

1. **Test all features** - Try the features above
2. **Check console** - F12 → Console tab for any warnings
3. **Review logs** - Check Railway dashboard for backend activity
4. **Deploy** - Follow FRONTEND_CHATBOT_SETUP.md for deployment steps
5. **Share** - Send the deployed URL to users!

---

## 🚀 Deploy to Production

Once local testing works:

```bash
# Build for production
pnpm build

# Deploy 'build/' folder to:
# - Vercel (easiest for Docusaurus)
# - Netlify
# - AWS S3
# - Any static host

# See FRONTEND_CHATBOT_SETUP.md for detailed instructions
```

---

## 📞 Help

If something isn't working:

1. **Check FRONTEND_CHATBOT_SETUP.md** - Detailed troubleshooting
2. **Check browser console (F12)** - Look for error messages
3. **Test Railway backend** - Is it running? curl the health endpoint
4. **Review Railway logs** - Check deployment status in Railway dashboard

---

**You've got this! 🎉**

Built with React + TypeScript + Docusaurus v3 + Railway FastAPI
