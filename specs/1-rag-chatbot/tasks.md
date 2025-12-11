# Task Breakdown: RAG Chatbot - Website Ingestion & Vector Database

**Feature Branch**: `1-rag-chatbot`
**Total Tasks**: 28
**Estimated Effort**: 5-7 work days
**Priority**: P1 (core functionality) + P2 (verification)

---

## Task Organization

Tasks are grouped by implementation phase and ordered by dependencies. Each task includes:
- Unique identifier (TASK-XXX)
- Clear acceptance criteria
- Test cases
- Dependencies

---

## Phase 1: Project Setup & Infrastructure

### TASK-001: Initialize Python Project Structure
**Priority**: P0 (blocker)
**Dependency**: None
**Estimated Time**: 2 hours

**Acceptance Criteria**:
- [ ] Create `rag_pipeline/` directory at project root
- [ ] Create Python package structure:
  ```
  rag_pipeline/
  ├── __init__.py
  ├── main.py (entry point)
  ├── config.py (configuration loading)
  ├── crawler.py (website crawler)
  ├── preprocessor.py (text chunking)
  ├── embeddings.py (embedding generation)
  ├── storage.py (Qdrant integration)
  ├── verification.py (QA checks)
  ├── logging_utils.py (audit trail)
  └── utils/
      ├── __init__.py
      ├── retry.py (exponential backoff)
      └── text_processing.py (tokenization, etc.)
  ```
- [ ] Create `tests/` directory with matching structure
- [ ] Create `config.yaml` template with all settings
- [ ] Create `.env.example` with required variables

**Test Cases**:
- Directory structure exists
- All Python files are importable
- Config template is valid YAML

---

### TASK-002: Set Up Python Dependencies & Virtual Environment
**Priority**: P0 (blocker)
**Dependency**: TASK-001
**Estimated Time**: 1 hour

**Acceptance Criteria**:
- [ ] Create `requirements.txt` with all dependencies (see plan.md)
- [ ] Create `pyproject.toml` if using modern packaging
- [ ] Document Python version requirement (3.8+)
- [ ] Create setup instructions in README
- [ ] Verify all imports work

**Dependencies**: requests, beautifulsoup4, cohere, qdrant-client, tiktoken, nltk, python-dotenv, pytest

**Test Cases**:
- All packages can be imported
- NLTK punkt tokenizer downloads successfully
- No version conflicts

---

### TASK-003: Set Up Environment Variables & Configuration Loading
**Priority**: P0 (blocker)
**Dependency**: TASK-002
**Estimated Time**: 1 hour

**Acceptance Criteria**:
- [ ] Create `.env.example` with:
  ```
  COHERE_API_KEY=
  QDRANT_URL=
  QDRANT_API_KEY=
  TARGET_WEBSITE_URL=
  LOG_LEVEL=INFO
  ```
- [ ] Implement `config.py` that:
  - Loads from `.env` via `python-dotenv`
  - Validates required keys are present
  - Raises clear error if missing
  - Supports both file and environment variable sources
- [ ] Create `config.yaml` template with all crawler/chunking/embedding settings
- [ ] Document how to configure each component

**Test Cases**:
- Missing required env vars raises ValueError
- Config loads from .env file
- Config loads from environment variables
- Config.yaml parses correctly

---

### TASK-004: Set Up Logging Infrastructure
**Priority**: P0 (blocker)
**Dependency**: TASK-001
**Estimated Time**: 1.5 hours

**Acceptance Criteria**:
- [ ] Create `logging_utils.py` with:
  - Logger initialization with timestamp, level, message format
  - File handler (logs/ingestion_YYYYMMDD.log)
  - Console handler for real-time feedback
  - Structured logging for operations (JSON lines format)
- [ ] Create `logs/` directory (add to .gitignore)
- [ ] Log format: `[TIMESTAMP] [LEVEL] [COMPONENT] Message`
- [ ] Implement operation logging:
  ```python
  log_operation("crawl_start", {"base_url": "...", "config": {...}})
  log_operation("crawl_complete", {"urls_discovered": 15, "duration_seconds": 45})
  log_operation("chunk_created", {"chunk_id": "...", "token_count": 287})
  log_operation("embedding_stored", {"vector_id": "...", "success": True})
  ```

**Test Cases**:
- Log files created in `logs/` directory
- Correct timestamp format
- All log levels work (DEBUG, INFO, WARNING, ERROR)

---

## Phase 2: Website Crawler Implementation

### TASK-005: Implement URL Discovery with BFS Traversal
**Priority**: P1
**Dependency**: TASK-003, TASK-004
**Estimated Time**: 4 hours

**Acceptance Criteria**:
- [ ] Create `crawler.py::discover_urls(base_url)` function that:
  - Uses BFS to discover all reachable documentation pages
  - Filters out non-documentation URLs (e.g., login, admin pages)
  - Respects `robots.txt` if enabled
  - Returns list of discovered URLs with hierarchy info
- [ ] Implement `_should_crawl_url(url)` helper to filter:
  - Include: `/docs/`, documentation paths
  - Exclude: `/admin`, `/api`, external links, anchors
- [ ] Add request delay (configurable, default 0.5s) to be respectful
- [ ] Handle timeouts and connection errors gracefully
- [ ] Limit to reasonable max pages (configurable)
- [ ] Preserve URL structure metadata (path depth, module inference)

**Configuration**:
```python
CRAWLER_CONFIG = {
    "base_url": "https://example.com/docs",
    "request_delay": 0.5,
    "timeout": 10,
    "max_pages": None,  # unlimited
    "respect_robots_txt": True,
    "user_agent": "RAGCrawler/1.0"
}
```

**Test Cases**:
- Discovers all documentation pages from test website
- Excludes non-documentation URLs
- Preserves parent-child relationships
- Handles redirects correctly
- Respects robots.txt when enabled
- Waits between requests

---

### TASK-006: Implement HTML Content Extraction & Filtering
**Priority**: P1
**Dependency**: TASK-005
**Estimated Time**: 3 hours

**Acceptance Criteria**:
- [ ] Create `crawler.py::extract_documentation_content(html, url)` function that:
  - Uses BeautifulSoup to parse HTML
  - Identifies main content area (typically `<main>`, `<article>`, `.docusaurus_container`)
  - Filters out common non-content elements:
    - Navigation sidebars
    - Breadcrumbs
    - Footer elements
    - Ad/tracking scripts
  - Converts HTML to plain text preserving structure
  - Preserves markdown-like formatting (e.g., **bold**, list markers)
  - Returns cleaned text content

- [ ] Create `_extract_main_content(soup)` helper to identify main text area
- [ ] Create `_clean_html(html_text)` to remove scripts, styles, comments
- [ ] Handle edge cases:
  - Pages with multiple content sections
  - Code blocks and pre-formatted text
  - Tables (convert to plain text representation)
  - Lists and nested structures

**Test Cases**:
- Navigation and sidebars removed
- Main content preserved
- Markdown structure visible in output
- Code blocks remain readable
- Tables converted to text format

---

### TASK-007: Extract & Preserve Hierarchical Metadata
**Priority**: P1
**Dependency**: TASK-005, TASK-006
**Estimated Time**: 2 hours

**Acceptance Criteria**:
- [ ] Create `crawler.py::extract_hierarchy_metadata(url, html)` that:
  - Infers module name from URL path (e.g., `/docs/module-1-foundations` → "Module 1: Foundations")
  - Extracts page title from `<h1>`, `<title>`, or first heading
  - Extracts section/lesson structure from heading hierarchy
  - Returns metadata object:
    ```python
    {
        "url": "...",
        "title": "Lesson 1: Introduction to Physical AI",
        "module": "Module 1: Foundations",
        "section": "Introduction",
        "hierarchy_level": 3,
        "breadcrumbs": ["Module 1", "Foundations", "Introduction"]
    }
    ```
- [ ] Handle Docusaurus-specific patterns:
  - Module folders typically: `module-N-name`
  - Lesson folders typically: `lesson-N-N-name`
- [ ] Create title fallback chain:
  1. Page's `<h1>` tag
  2. Document `<title>` tag
  3. First heading found
  4. URL slug as last resort

**Test Cases**:
- Module extracted from URL correctly
- Lesson title extracted from page
- Breadcrumb hierarchy matches nesting
- Fallback title extraction works

---

### TASK-008: Implement Crawler with Integration Testing
**Priority**: P1
**Dependency**: TASK-005, TASK-006, TASK-007
**Estimated Time**: 3 hours

**Acceptance Criteria**:
- [ ] Create `crawler.py::CrawlResult` dataclass:
  ```python
  @dataclass
  class CrawlResult:
      url: str
      title: str
      module: str
      section: str
      html_content: str
      text_content: str
      crawled_at: datetime
      page_type: str
      hierarchy_level: int
  ```
- [ ] Create `crawler.py::crawl_website(base_url, config)` orchestrator that:
  - Discovers all URLs
  - Extracts content from each
  - Preserves metadata
  - Logs each page crawled
  - Returns list of CrawlResult objects
- [ ] Add error handling and logging for each page
- [ ] Implement `save_crawl_results(results, output_dir)` to save JSON

**Test Cases**:
- Full crawl completes without errors
- All pages extracted
- Metadata complete for each page
- Results saved to JSON
- Crawler can resume from saved state

**Acceptance Scenarios** (from spec.md):
- ✅ All public documentation pages discovered (User Story 1.1)
- ✅ Documentation pages filtered from non-docs URLs (User Story 1.2)
- ✅ Hierarchy metadata preserved (User Story 1.3)
- ✅ Navigation elements filtered from content (User Story 1.4)

---

## Phase 3: Text Preprocessing & Chunking

### TASK-009: Implement Text Tokenization using TikToken
**Priority**: P1
**Dependency**: TASK-001, TASK-002
**Estimated Time**: 1.5 hours

**Acceptance Criteria**:
- [ ] Create `preprocessor.py::count_tokens(text)` using tiktoken:
  - Use `encoding_for_model("gpt-2")` (standard encoding)
  - Return accurate token count
  - Handle special characters, multi-byte chars
- [ ] Create `preprocessor.py::estimate_tokens_for_embedding_batch(texts)`:
  - Validate batch won't exceed Cohere limits
  - Return total token count for logging

**Test Cases**:
- Token count matches expected (use known examples)
- Special characters counted correctly
- Multi-language text handled (English focus)

---

### TASK-010: Implement Text Normalization & Cleaning
**Priority**: P1
**Dependency**: TASK-009
**Estimated Time**: 2 hours

**Acceptance Criteria**:
- [ ] Create `preprocessor.py::normalize_text(text)` that:
  - Remove extra whitespace (multiple spaces → single)
  - Standardize line breaks
  - Handle Unicode normalization
  - Preserve markdown-style markers (*, -, #)
  - Convert tabs to spaces
- [ ] Create `preprocessor.py::remove_boilerplate(text)` to remove:
  - "Edit this page" links
  - "Previous/Next" navigation
  - Docusaurus-specific metadata

**Test Cases**:
- Extra whitespace removed
- Markdown structure preserved
- Unicode handled correctly

---

### TASK-011: Implement Semantic Boundary Detection for Chunking
**Priority**: P1
**Dependency**: TASK-009, TASK-010
**Estimated Time**: 3 hours

**Acceptance Criteria**:
- [ ] Create `preprocessor.py::find_semantic_boundaries(text)` that:
  - Detects paragraph breaks (double newlines)
  - Detects section breaks (heading markers: `###`, `---`, etc.)
  - Preserves code block boundaries
  - Returns list of boundary positions
- [ ] Create `preprocessor.py::split_at_boundaries(text, boundaries)`:
  - Splits text at detected boundaries
  - Respects token limits (don't split short sections)
  - Returns list of semantic units
- [ ] Handle edge cases:
  - Consecutive boundaries (collapse them)
  - Sections shorter than min_tokens (merge with neighbors)
  - Code blocks (don't split inside)

**Test Cases**:
- Paragraphs detected correctly
- Sections separated properly
- Code blocks kept intact
- No mid-sentence splits in output

---

### TASK-012: Implement Intelligent Text Chunking
**Priority**: P1
**Dependency**: TASK-011
**Estimated Time**: 4 hours

**Acceptance Criteria**:
- [ ] Create `preprocessor.py::chunk_text(text, min_tokens, target_tokens, max_tokens, overlap_tokens)` that:
  - Respects semantic boundaries (prefer paragraph/section breaks)
  - Creates chunks of target_tokens when possible
  - Enforces min/max token limits
  - Implements overlap (e.g., last 50 tokens of previous chunk start next)
  - Returns list of chunk strings with metadata
- [ ] Create `preprocessor.py::ChunkMetadata` dataclass:
  ```python
  @dataclass
  class ChunkMetadata:
      text: str
      token_count: int
      chunk_index: int
      total_chunks: int
      boundary_type: str  # "paragraph", "section", etc.
  ```
- [ ] Configuration:
  ```python
  CHUNKING_CONFIG = {
      "min_tokens": 100,
      "target_tokens": 350,
      "max_tokens": 512,
      "overlap_tokens": 50
  }
  ```

**Test Cases**:
- All chunks between min/max tokens
- Semantic boundaries respected (no mid-sentence splits)
- Overlap implemented correctly
- Distribution matches expected (200-500 total for full website)
- Long pages chunk properly (100+ chunks per page)

---

### TASK-013: Implement Context Preservation (Header Prepending)
**Priority**: P1
**Dependency**: TASK-012
**Estimated Time**: 2 hours

**Acceptance Criteria**:
- [ ] Create `preprocessor.py::prepend_context(chunk_text, source_metadata)` that:
  - Adds section header at beginning of chunk
  - Format: `## Section Title\n\nchunk content...`
  - Preserves full context hierarchy (module > section > subsection)
  - Token count includes prepended headers
- [ ] Examples:
  ```
  Input: chunk = "robots learn through reinforcement..."
  Output: "## Learning Methods\n\nRobots learn through reinforcement..."
  ```

**Test Cases**:
- Headers added to chunks
- Token count includes headers
- Format is readable
- No duplicate headers

---

### TASK-014: Implement Chunk ID Generation & Metadata Assignment
**Priority**: P1
**Dependency**: TASK-012, TASK-013
**Estimated Time**: 2 hours

**Acceptance Criteria**:
- [ ] Create `preprocessor.py::generate_chunk_id(source_url, page_index, chunk_index)`:
  - Format: `chunk_{hash}_{module}_{lesson}_{section}_{index}`
  - Globally unique, deterministic (same input → same ID)
  - Human-readable when possible
  - Example: `chunk_a1b2_module1_lesson1_intro_001`
- [ ] Create `preprocessor.py::TextChunk` dataclass:
  ```python
  @dataclass
  class TextChunk:
      chunk_id: str
      source_url: str
      module: str
      section: str
      text: str
      token_count: int
      chunk_index: int
      total_chunks: int
      created_at: datetime
  ```
- [ ] Assign metadata from crawl results to each chunk

**Test Cases**:
- Chunk IDs are unique
- IDs are reproducible
- Metadata complete for each chunk
- Timestamps accurate

---

### TASK-015: Implement Deduplication Logic
**Priority**: P1
**Dependency**: TASK-014
**Estimated Time**: 3 hours

**Acceptance Criteria**:
- [ ] Create `preprocessor.py::deduplicate_chunks(chunks, similarity_threshold=0.95)`:
  - Calculate text hash for exact duplicates (fast path)
  - Use difflib SequenceMatcher for near-duplicates
  - Merge duplicate metadata (preserve references to both sources)
  - Return deduplicated list with metadata about merges
- [ ] Configuration:
  ```python
  DEDUPLICATION_CONFIG = {
      "threshold": 0.95,  # 95% similarity = duplicate
      "preserve_all_sources": True  # keep metadata for both
  }
  ```
- [ ] Handle edge cases:
  - Identical chunks with different section headers (may keep both)
  - Chunks that differ only by whitespace (deduplicate)
  - Chunks from different pages (preserve source info)

**Test Cases**:
- Identical chunks deduplicated
- 95%+ similar chunks detected
- Metadata preserved for both sources
- Whitespace-only differences handled

---

### TASK-016: Implement Preprocessing Pipeline Integration
**Priority**: P1
**Dependency**: TASK-008, TASK-015
**Estimated Time**: 3 hours

**Acceptance Criteria**:
- [ ] Create `preprocessor.py::preprocess_crawled_content(crawl_results, config)` orchestrator:
  - Takes list of CrawlResult from crawler
  - Normalizes text
  - Chunks intelligently
  - Prepends context headers
  - Assigns IDs and metadata
  - Deduplicates
  - Returns list of TextChunk objects
- [ ] Implement `save_chunks_to_file(chunks, output_format="json")`:
  - Save to JSON or CSV for inspection/debugging
  - Include full metadata for each chunk
- [ ] Logging:
  - Log total chunks created
  - Log token distribution statistics
  - Log deduplication results (X duplicates removed)

**Test Cases**:
- Full preprocessing pipeline runs without errors
- Output matches acceptance criteria from spec:
  - ✅ 256-512 token chunks with semantic boundaries (Story 2.1)
  - ✅ Section headers preserved (Story 2.2)
  - ✅ Metadata complete (Story 2.3)
  - ✅ Tables/code formatted correctly (Story 2.4)
  - ✅ Logical split boundaries (Story 2.5)
- Chunk statistics logged correctly

---

## Phase 4: Embedding Generation & Storage

### TASK-017: Implement Exponential Backoff Retry Logic
**Priority**: P1
**Dependency**: TASK-001, TASK-002
**Estimated Time**: 2 hours

**Acceptance Criteria**:
- [ ] Create `utils/retry.py::ExponentialBackoff` class:
  ```python
  class ExponentialBackoff:
      def __init__(self, initial_delay=1, max_attempts=5, base=2):
          # delay = initial_delay * (base ** attempt_number)
      def should_retry(self, exception) -> bool
      def get_next_delay(self) -> float
      def wait(self)  # sleep for next_delay
  ```
- [ ] Handle special cases:
  - Extract `Retry-After` header from HTTP responses (override backoff)
  - Detect rate limit errors (429) specifically
  - Idempotent operations only (safe to retry)
- [ ] Configuration:
  ```python
  RETRY_CONFIG = {
      "max_attempts": 5,
      "initial_delay": 1,
      "exponential_base": 2,  # 1s → 2s → 4s → 8s → 16s
      "max_delay": 60  # cap at 1 minute
  }
  ```

**Test Cases**:
- Backoff delays increase exponentially
- Max attempts respected
- Retry-After header respected
- Non-retryable errors not retried

---

### TASK-018: Implement Cohere API Integration
**Priority**: P1
**Dependency**: TASK-003, TASK-002, TASK-017
**Estimated Time**: 3 hours

**Acceptance Criteria**:
- [ ] Create `embeddings.py::CoherEmbeddingsGenerator` class:
  ```python
  class CoherEmbeddingsGenerator:
      def __init__(self, api_key: str, model: str = "embed-english-v3.0"):
          # Initialize Cohere client
      def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
          # Call Cohere API with retry logic
      def get_embedding_dimension(self) -> int:
          # Return 1024 for embed-english-v3.0
  ```
- [ ] Implement batch processing:
  - Default batch size: 100 texts per request
  - Validate total tokens don't exceed API limits
  - Handle partial batch failures (retry failed texts)
  - Log API calls for audit trail
- [ ] Error handling:
  - Catch and retry on 429 (rate limit)
  - Catch and retry on 5xx (server errors)
  - Fail on 401 (auth), 404 (model not found)
  - Log detailed error context

**Configuration**:
```python
COHERE_CONFIG = {
    "api_key": "${COHERE_API_KEY}",
    "model": "embed-english-v3.0",
    "embedding_dimension": 1024,
    "batch_size": 100,
    "retry_max_attempts": 5,
    "retry_initial_delay": 1
}
```

**Test Cases**:
- Embeddings generated for valid texts
- Correct dimension (1024)
- Batch processing works
- Rate limits respected (retry on 429)
- Partial failures retried

---

### TASK-019: Set Up Qdrant Cloud Integration
**Priority**: P1
**Dependency**: TASK-003, TASK-002
**Estimated Time**: 2 hours

**Acceptance Criteria**:
- [ ] Create `storage.py::QdrantVectorStore` class:
  ```python
  class QdrantVectorStore:
      def __init__(self, url: str, api_key: str, collection_name: str):
          # Connect to Qdrant Cloud
      def create_collection(self, vector_size: int) -> bool:
          # Create collection if not exists
      def insert_vectors(self, vectors: List[Vector]) -> List[str]:
          # Store vectors with metadata
      def search(self, query_vector: List[float], top_k: int) -> List[SearchResult]:
          # Semantic search
  ```
- [ ] Collection schema:
  ```python
  {
      "name": "robotics_documentation",
      "vectors": {"size": 1024, "distance": "cosine"},
      "payload_schema": {
          "chunk_id": "string",
          "source_url": "string",
          "module": "string",
          "section": "string",
          "text": "string",
          "token_count": "integer",
          "created_at": "string"
      }
  }
  ```
- [ ] Collection initialization logic:
  - Check if collection exists
  - Create if missing (or skip if exists and dimensions match)
  - Validate schema compatibility

**Configuration**:
```python
QDRANT_CONFIG = {
    "url": "${QDRANT_URL}",
    "api_key": "${QDRANT_API_KEY}",
    "collection_name": "robotics_documentation",
    "timeout": 30
}
```

**Test Cases**:
- Qdrant connection successful
- Collection created/verified
- Connection can be authenticated
- Schema matches expected dimensions

---

### TASK-020: Implement Vector Storage with Metadata
**Priority**: P1
**Dependency**: TASK-018, TASK-019
**Estimated Time**: 3 hours

**Acceptance Criteria**:
- [ ] Create `storage.py::store_embeddings_in_qdrant(embeddings, chunks, vector_store)`:
  - Takes list of embeddings (from Cohere)
  - Takes list of TextChunk metadata
  - Uploads to Qdrant as points with payload
  - Returns confirmation of stored vector IDs
  - Logs operation with counts
- [ ] Implement batch uploads:
  - Process in batches of 100
  - Each point includes full metadata
  - Retry failed batches with backoff
- [ ] Data validation:
  - Embedding dimension matches schema (1024)
  - Metadata complete (no missing fields)
  - Chunk IDs unique

**Test Cases**:
- Vectors stored in Qdrant
- Metadata queryable
- Correct count stored
- No data loss
- Batch uploads work

---

### TASK-021: Implement Deduplication at Storage Level
**Priority**: P1
**Dependency**: TASK-020
**Estimated Time**: 2 hours

**Acceptance Criteria**:
- [ ] Create `storage.py::check_duplicate_vectors(chunk_id, vector_store)`:
  - Query existing collection for chunk_id
  - Check if chunk already stored
  - Return existing vector ID if present
- [ ] Implement pre-upload validation:
  - Check each chunk_id against Qdrant before storing
  - Skip duplicate uploads
  - Log skipped vectors for audit
  - Merge metadata for duplicate sources

**Test Cases**:
- Duplicate chunk IDs detected
- Existing vectors not re-uploaded
- Metadata updated with new sources

---

### TASK-022: Implement End-to-End Embedding Pipeline
**Priority**: P1
**Dependency**: TASK-016, TASK-018, TASK-021
**Estimated Time**: 3 hours

**Acceptance Criteria**:
- [ ] Create `embeddings.py::generate_and_store_embeddings(chunks, config)` orchestrator:
  - Takes preprocessed TextChunk objects
  - Batches chunks for Cohere API
  - Generates embeddings
  - Stores in Qdrant with metadata
  - Returns summary (count, time, errors)
- [ ] Error handling and recovery:
  - Handle partial batch failures
  - Retry failed chunks
  - Log all operations
- [ ] Progress tracking:
  - Log progress every N chunks
  - Estimate time remaining
  - Final summary report

**Logging**:
- `embedding_batch_start`: batch size, total chunks
- `embedding_batch_complete`: vectors stored, duration
- `embedding_error`: chunk_id, error details, retry attempt
- `embedding_pipeline_complete`: total vectors, total time, failures

**Test Cases**:
- Full pipeline runs without errors
- Correct number of embeddings generated
- All vectors stored in Qdrant
- Metadata complete
- Progress logged throughout
- Meets spec requirement: ✅ Story 3 (embedding generation & storage)

---

## Phase 5: Verification & Quality Assurance

### TASK-023: Implement Vector Count & Coverage Reporting
**Priority**: P2
**Dependency**: TASK-022
**Estimated Time**: 2 hours

**Acceptance Criteria**:
- [ ] Create `verification.py::report_vector_coverage(vector_store)` that:
  - Count total vectors in collection
  - Group by module (parse from chunk_id or metadata)
  - Return report:
    ```
    Total Vectors: 287
    Module 1: Foundations: 65 chunks
    Module 2: Embodied Robotics: 72 chunks
    Module 3: Humanoid AI Agents: 75 chunks
    Module 4: Applied AI-Native: 75 chunks
    ```
- [ ] Verify against success criteria:
  - ✅ SC-001: 100% coverage (all pages crawled)
  - ✅ SC-002: 200-500 chunks total (verify distribution)

**Test Cases**:
- Coverage report generated
- Module counts sum to total
- Distribution within expected range

---

### TASK-024: Implement Semantic Query Verification
**Priority**: P2
**Dependency**: TASK-022
**Estimated Time**: 2 hours

**Acceptance Criteria**:
- [ ] Create `verification.py::verify_semantic_search(vector_store, sample_queries)` that:
  - Takes list of test queries
  - Generates embeddings for queries (using Cohere)
  - Searches vector DB for top-5 results per query
  - Returns results with relevance scores
  - User manually spot-checks relevance (10+ queries per spec)
- [ ] Example queries (from spec):
  - "How do robots perceive their environment?"
  - "What is embodied intelligence?"
  - "Explain humanoid robot design"
  - etc.
- [ ] Verify spec requirement:
  - ✅ SC-005: Top-5 results semantically relevant (manual verification)

**Test Cases**:
- Queries return results (non-empty)
- Results include source metadata
- Relevance scores present
- Results are semantically related

---

### TASK-025: Implement Metadata Validation & Completeness Check
**Priority**: P2
**Dependency**: TASK-022
**Estimated Time**: 1.5 hours

**Acceptance Criteria**:
- [ ] Create `verification.py::validate_metadata_completeness(vector_store)` that:
  - Sample 100+ vectors from collection
  - Check each has required fields:
    - chunk_id (not empty, unique format)
    - source_url (valid URL format)
    - module (not empty)
    - section (not empty)
    - text (preview available)
    - token_count (valid integer)
    - created_at (valid timestamp)
  - Report any missing/invalid fields
- [ ] Verify spec requirement:
  - ✅ SC-004: All metadata intact and queryable
  - ✅ SC-009: No dimension mismatches

**Test Cases**:
- All required fields present
- URLs are valid format
- Token counts are positive integers
- Timestamps are parseable

---

### TASK-026: Create Comprehensive Ingestion Report
**Priority**: P2
**Dependency**: TASK-023, TASK-024, TASK-025
**Estimated Time**: 2 hours

**Acceptance Criteria**:
- [ ] Create `verification.py::generate_ingestion_report()` that produces:
  ```markdown
  # RAG Chatbot Ingestion Report
  ## Summary
  - Start Time: 2025-12-11T10:00:00Z
  - End Time: 2025-12-11T10:08:30Z
  - Total Duration: 8 minutes 30 seconds

  ## Crawling Phase
  - URLs Discovered: 15
  - URLs Crawled: 15
  - Pages Extracted: 15

  ## Preprocessing Phase
  - Total Chunks Created: 287
  - Chunks Deduplicated: 3
  - Final Chunk Count: 284
  - Token Distribution:
    - Minimum: 102 tokens
    - Average: 342 tokens
    - Maximum: 509 tokens

  ## Embedding Generation
  - Embeddings Generated: 284
  - Cohere API Calls: 3 batches of 100
  - Embedding Dimension: 1024
  - Processing Time: 45 seconds

  ## Storage & Verification
  - Vectors Stored: 284
  - Metadata Complete: ✅ (100%)
  - Semantic Search: ✅ (10 queries verified)
  - Coverage by Module:
    - Module 1: 65 chunks
    - Module 2: 72 chunks
    - Module 3: 75 chunks
    - Module 4: 75 chunks

  ## Status
  Overall Status: ✅ SUCCESS
  All acceptance criteria met.
  ```
- [ ] Save report to `reports/ingestion_YYYY-MM-DD_HHmmss.md`

**Test Cases**:
- Report generated
- All statistics present
- Format is readable
- Saved to correct location

---

### TASK-027: Implement Incremental Update Support
**Priority**: P2
**Dependency**: TASK-016, TASK-022, TASK-024
**Estimated Time**: 3 hours

**Acceptance Criteria**:
- [ ] Create `rag_pipeline/incremental.py::update_with_new_content(since_timestamp, config)`:
  - Crawl website for changes since timestamp
  - Preprocess new/updated content
  - Generate embeddings
  - Store in Qdrant without duplicating existing vectors
  - Verify no data loss
- [ ] Track processed state:
  - Save last_processed_timestamp after successful update
  - Use as default for next incremental run
  - Support manual timestamp override
- [ ] Deduplication at update time:
  - Check if chunk_id already exists in Qdrant
  - Skip upload if present
  - Log skipped vectors
  - Merge metadata if needed
- [ ] Verify spec requirement:
  - ✅ SC-010: At least 10 incremental updates without data loss

**Test Cases**:
- Incremental update discovers changes
- New content processed
- No duplicates created
- Existing vectors not modified
- Metadata updated correctly

---

### TASK-028: Create End-to-End Integration Test Suite
**Priority**: P2
**Dependency**: All other tasks
**Estimated Time**: 3 hours

**Acceptance Criteria**:
- [ ] Create `tests/test_integration.py` with:
  - Full pipeline test (crawl → chunk → embed → store)
  - Uses test website (can be local or fixture data)
  - Verifies all success criteria met
  - Checks final report generated
- [ ] Test incremental update flow
- [ ] Test error recovery (connection loss, rate limits)
- [ ] Performance test (completes in <10 minutes for full website)

**Test Scenarios**:
1. Full pipeline from start to finish
2. Crawl phase produces expected URLs
3. Preprocessing produces 200-500 chunks
4. Embeddings stored with metadata
5. Queries return semantically relevant results
6. Report generated with all stats
7. Incremental update adds new content
8. No data loss or duplicates

**Acceptance Criteria**:
- ✅ SC-001: 100% URL coverage
- ✅ SC-002: Correct chunk distribution (200-500)
- ✅ SC-003: 100% embedding generation success
- ✅ SC-004: All metadata intact and queryable
- ✅ SC-005: Semantic search returns relevant results
- ✅ SC-006: Full pipeline under 10 minutes
- ✅ SC-007: All operations logged
- ✅ SC-008: Automated verification shows no issues
- ✅ SC-009: No dimension mismatches
- ✅ SC-010: Incremental updates without loss

---

## Quality Gates & Sign-Off

### Code Quality
- [ ] All code passes linting (flake8, black formatting)
- [ ] All code has type hints (mypy passes)
- [ ] Unit test coverage >80%
- [ ] Integration tests pass
- [ ] No hardcoded secrets or credentials

### Documentation
- [ ] README.md updated with usage instructions
- [ ] All functions have docstrings
- [ ] Configuration documented
- [ ] Example `.env` provided
- [ ] Troubleshooting guide included

### Operational Readiness
- [ ] Logging functional and auditable
- [ ] Error messages helpful
- [ ] Recovery procedures documented
- [ ] Performance benchmarks met
- [ ] No resource leaks

### Deployment
- [ ] Can run with single command: `python -m rag_pipeline.main`
- [ ] Configuration from environment variables
- [ ] Supports both one-time and incremental runs
- [ ] Verification scripts work standalone

---

## Success Criteria Summary

**Must Have (All P1 tasks)**:
- ✅ Website crawler discovers all 15+ documentation pages
- ✅ Text preprocessing creates 200-500 semantic chunks
- ✅ Embeddings generated for 100% of chunks
- ✅ Vectors stored in Qdrant with metadata
- ✅ Semantic search working

**Should Have (P2 verification)**:
- ✅ Automated verification of all success criteria
- ✅ Comprehensive ingestion reports
- ✅ Audit trail of all operations
- ✅ Incremental update support

**Acceptance**: All 28 tasks completed, all test cases passing, all success criteria met.
