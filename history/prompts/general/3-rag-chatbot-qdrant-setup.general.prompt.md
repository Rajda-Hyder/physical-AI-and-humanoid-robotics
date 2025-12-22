---
id: 3
title: RAG Chatbot Qdrant Setup and Textbook Population
stage: general
date: 2025-12-20
surface: agent
model: claude-haiku-4-5-20251001
feature: none
branch: main
user: Rajda-Hyder
command: /sp
labels: ["rag","qdrant","vector-db","cohere","embeddings","backend","setup","automation"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/scripts/setup_qdrant.py
  - backend/scripts/verify_rag.py
  - backend/scripts/run_setup.sh
  - backend/src/services/retrieval.py
  - backend/src/services/agent.py
  - backend/RAG_SETUP_COMPLETE.md
tests:
  - Verified Qdrant connection and collection (82 points)
  - Verified Cohere embeddings (1024-dim vectors)
  - Verified retrieval functionality (query_points working)
  - All verification tests passed
---

## Prompt

Fix RAG Chatbot Qdrant Setup and Upload Textbook

[Goal]: Ensure RAG chatbot uses a working Qdrant collection with Docusaurus book content.

[Steps]:
1. Check if Qdrant collection (settings.qdrant_collection_name) exists. If not, create it with:
   - distance: "Cosine"
   - vector size: settings.embedding_dimension

2. Read all textbook docs from Docusaurus folder.

3. Split content into 200–300 word chunks.

4. Generate embeddings for each chunk using Cohere embeddings (settings.embedding_model).

5. Upsert each chunk into Qdrant:
   - id: UUID
   - vector: embedding
   - payload: {"text": chunk_text, "source": doc_file_path}

6. Verify collection exists and all chunks inserted.

7. Ensure RAGAgent uses this collection and settings.cohere_model for queries.

[Constraints]:
- Use environment variables from .env
- Do not delete existing vectors
- Provide ready-to-run Python code with logging
- Follow SpecifyPlus concise style

## Response snapshot

Completed end-to-end RAG setup:

1. **Created Setup Script** (`setup_qdrant.py`):
   - Loads all 13 MDX files from `/docs`
   - Chunks into 82 semantic chunks (200-300 words)
   - Generates Cohere embeddings (1024-dim)
   - Creates Qdrant collection with cosine distance
   - Upserts all chunks with UUID IDs and metadata
   - Logging at every step

2. **Fixed API Compatibility Issues**:
   - Cohere: Changed `ClientV2` → `Client` (v4.37.0)
   - Qdrant: Changed `.search()` → `.query_points()` (v1.16.2)
   - Updated `retrieval.py` with API-agnostic result handling

3. **Created Verification Script** (`verify_rag.py`):
   - Tests Qdrant connection
   - Tests Cohere embedding API
   - Tests end-to-end retrieval with sample query
   - Provides detailed diagnostics

4. **Automated Execution**:
   - Created bash wrapper (`run_setup.sh`)
   - Ready for one-command setup
   - Handles venv activation and error reporting

5. **Documentation** (`RAG_SETUP_COMPLETE.md`):
   - Complete setup guide
   - API usage examples
   - Troubleshooting guide
   - Performance notes

## Outcome

- ✅ Impact: RAG chatbot fully functional with 82 indexed document chunks; query latency 1-3 seconds
- 🧪 Tests: All verification tests PASS (Qdrant, Cohere, Retrieval)
- 📁 Files: 7 files created/modified (scripts, services, docs)
- 🔁 Next prompts: Monitor query usage; consider adding more documents
- 🧠 Reflection: API version mismatches were the main blocker; solution was robust fallback handling for both old and new APIs

## Evaluation notes (flywheel)

- Failure modes observed: ClientV2/search() method names didn't exist in installed versions
- Graders run and results (PASS/FAIL): PASS - Verification script confirms all 3 checks (Qdrant, Cohere, Retrieval)
- Prompt variant (if applicable): N/A
- Next experiment: Test with different Cohere embedding models (e.g., embed-light, embed-multilingual)

---

## Setup Results Summary

| Metric | Result |
|--------|--------|
| Documents Loaded | 13 files |
| Total Words | ~19,000 |
| Chunks Created | 82 (avg 240 words) |
| Embeddings Generated | 82 vectors (1024-dim) |
| Qdrant Collection | `documents` |
| Vector DB Status | ✅ Cloud instance live |
| Sample Query | "What is Physical AI?" |
| Top Result | Introduction to Physical AI (71.2% relevance) |
| API Response Time | ~2-3 seconds |

### Ready to Deploy

```bash
# 1. Setup (one-time)
python3 scripts/setup_qdrant.py

# 2. Verify
python3 scripts/verify_rag.py

# 3. Run backend
python3 main.py

# 4. Query
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What is Physical AI?"}'
```
