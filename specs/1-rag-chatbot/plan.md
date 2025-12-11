# Implementation Plan: RAG Chatbot - Website Ingestion & Vector Database

**Feature Branch**: `1-rag-chatbot`
**Status**: Ready for Implementation
**Target Audience**: AI engineers and backend developers

---

## Executive Summary

This plan outlines the technical architecture for building a RAG (Retrieval-Augmented Generation) chatbot system that ingests a Docusaurus website, chunks content, generates embeddings via Cohere, and stores them in Qdrant Cloud. The implementation focuses on modularity, reliability, and production readiness across four core components.

---

## 1. Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    RAG Chatbot Ingestion Pipeline               │
└─────────────────────────────────────────────────────────────────┘
         │
         ├─► [Website Crawler] ─────────────────────┐
         │   (requests, beautifulsoup4)             │
         │   • Discover URLs                        │
         │   • Parse HTML content                   │
         │   • Extract documentation                │
         │   • Preserve hierarchy metadata          │
         │                                           │
         ├─────────────────────────────────────────►│
         │                                           ▼
         │                                    [Raw Pages Store]
         │                                    (JSON files)
         │
         ├─► [Text Preprocessor] ─────────────────┐
         │   (nltk, tiktoken)                      │
         │   • Normalize text                      │
         │   • Split into paragraphs               │
         │   • Calculate token counts              │
         │   • Preserve source references          │
         │                                          │
         ├──────────────────────────────────────►│
         │                                         ▼
         │                                  [Chunks Store]
         │                                  (JSON/CSV)
         │
         ├─► [Embeddings Generator] ──────────────┐
         │   (cohere, qdrant-client)              │
         │   • Batch process chunks               │
         │   • Call Cohere API                    │
         │   • Handle rate limits & retries       │
         │   • Deduplicate identical chunks       │
         │                                         │
         ├─────────────────────────────────────►│
         │                                        ▼
         │                                 [Qdrant Cloud]
         │                                 Vector Database
         │
         └─► [Verification & Logging]
             • Vector count audit
             • Sample semantic queries
             • Metadata validation
             • Execution reports
```

### Data Flow

1. **Crawling Phase**: Discover and extract website content
2. **Preprocessing Phase**: Normalize and chunk text
3. **Embedding Phase**: Generate embeddings and store vectors
4. **Verification Phase**: Validate and report results

---

## 2. Key Architectural Decisions

### Decision 1: Python-Based Pipeline vs. JavaScript Integration
**Choice**: Separate Python application for ingestion pipeline
**Rationale**:
- RAG ingestion is a batch process, not real-time client-side operation
- Python ecosystem has mature libraries (requests, beautifulsoup4, cohere SDK, qdrant-client)
- Decouples ingestion from web frontend - can run on schedule or manually
- Allows reuse across multiple projects
- No dependency on Node.js runtime constraints
**Trade-off**: Two technology stacks (Node/TypeScript for web, Python for RAG), but clear separation of concerns

### Decision 2: Batch Embedding Generation vs. Streaming
**Choice**: Batch processing with configurable batch size
**Rationale**:
- One-time ingestion use case (not real-time)
- Batch reduces API calls and costs
- Allows retry logic at batch level
- Easier to parallelize if needed in future
- Deterministic and auditable
**Trade-off**: Slightly longer processing time, but more efficient and reliable

### Decision 3: Qdrant Cloud Free Tier vs. Self-Hosted
**Choice**: Qdrant Cloud Free Tier
**Rationale**:
- No infrastructure management required
- Sufficient for 200-500 vectors with metadata (~1GB limit)
- Includes built-in backup and reliability
- Easy to scale up if needed
- Reduces operational burden
**Trade-off**: API dependency (not self-hosted), potential rate limits

### Decision 4: Metadata Storage Strategy
**Choice**: Store full metadata in Qdrant alongside vectors
**Rationale**:
- Enables rich search results (return source URL, section, etc.)
- Supports incremental updates and deduplication
- No separate database needed for metadata
- Qdrant supports payload with arbitrary JSON
**Trade-off**: Slightly larger vector storage, but simpler architecture

### Decision 5: Text Chunking Strategy
**Choice**: Semantic-aware chunking with overlap
**Rationale**:
- Respects paragraph/section boundaries (not arbitrary splits)
- Target 256-512 tokens maintains semantic coherence
- Section headers prepended to chunks provide context
- Configurable overlap for edge cases
**Trade-off**: More complex implementation than simple token-count splitting

### Decision 6: Error Handling & Retry Strategy
**Choice**: Exponential backoff with configurable retry limits
**Rationale**:
- Handles transient API failures gracefully
- Respects rate limits (especially Cohere free tier)
- Prevents API throttling through progressive delays
- Logs failures for debugging
**Trade-off**: Slightly longer total execution time on failures

---

## 3. Technical Specifications

### 3.1 Website Crawler Component

**Purpose**: Discover and extract content from Docusaurus website

**Inputs**:
- Base website URL (e.g., `https://example.com/docs`)
- Optional: robots.txt compliance (default: true)
- Optional: max pages to crawl (default: unlimited)

**Outputs**:
```json
{
  "url": "https://example.com/docs/module-1/lesson-1",
  "title": "Lesson 1: Introduction",
  "module": "Module 1: Foundations",
  "section": "Introduction",
  "html_content": "...",
  "text_content": "...",
  "metadata": {
    "crawled_at": "2025-12-11T10:30:00Z",
    "page_type": "lesson",
    "hierarchy_level": 3
  }
}
```

**Key Functions**:
- `discover_urls(base_url)` - BFS/DFS traversal of documentation links
- `extract_documentation(html)` - Parse and filter main content (remove navigation)
- `preserve_hierarchy(url, html)` - Extract module/section/lesson structure
- `normalize_content(html_content)` - Convert HTML to clean text

**Dependencies**:
- `requests` - HTTP client
- `beautifulsoup4` - HTML parsing
- `urllib` - URL manipulation
- `robots.txt` handling

**Configuration**:
```python
CRAWLER_CONFIG = {
    "base_url": "https://example.com/docs",
    "request_delay": 0.5,  # seconds between requests
    "timeout": 10,  # seconds per request
    "max_retries": 3,
    "respect_robots_txt": True,
    "user_agent": "RAGCrawler/1.0"
}
```

### 3.2 Text Preprocessing Component

**Purpose**: Chunk extracted content into semantic units

**Inputs**:
- Raw page content (text + metadata)
- Chunking parameters (token limits, overlap)

**Outputs**:
```json
{
  "chunk_id": "chunk_001_module1_lesson1_section1",
  "source_url": "https://example.com/docs/module-1/lesson-1",
  "module": "Module 1: Foundations",
  "section": "What is Physical AI?",
  "text": "Section: What is Physical AI?\n\nPhysical AI combines...",
  "token_count": 287,
  "metadata": {
    "chunk_index": 0,
    "total_chunks": 5,
    "created_at": "2025-12-11T10:35:00Z"
  }
}
```

**Key Functions**:
- `tokenize_text(text)` - Count tokens using tiktoken (GPT-2 encoding)
- `chunk_by_semantic_boundaries(text, min_tokens, max_tokens)` - Split at paragraph/section breaks
- `prepend_context(chunk, section_header)` - Add section info for semantic clarity
- `assign_chunk_ids(chunks, source_url)` - Generate unique identifiers
- `deduplicate_chunks(chunks)` - Detect 95%+ similarity (using hash or embedding)

**Dependencies**:
- `tiktoken` - Token counting (GPT-2 encoding)
- `nltk` - NLP utilities (sentence tokenization)
- `difflib` - Text similarity for deduplication

**Configuration**:
```python
CHUNKING_CONFIG = {
    "min_tokens": 100,
    "target_tokens": 350,  # center of 256-512 range
    "max_tokens": 512,
    "overlap_tokens": 50,  # context from previous chunk
    "split_on": ["paragraph", "sentence"],  # preferred boundaries
    "prepend_headers": True,
    "deduplication_threshold": 0.95
}
```

### 3.3 Embeddings Generator Component

**Purpose**: Generate semantic embeddings and store in Qdrant

**Inputs**:
- Text chunks with metadata
- Cohere API credentials

**Outputs**:
- Vectors stored in Qdrant Cloud with metadata

**Key Functions**:
- `initialize_cohere_client(api_key)` - Create authenticated client
- `initialize_qdrant_client(url, api_key)` - Connect to Qdrant Cloud
- `batch_chunks(chunks, batch_size)` - Group chunks for API efficiency
- `generate_embeddings(text_batch)` - Call Cohere API
- `store_vectors_in_qdrant(embeddings, metadata)` - Upload to vector DB
- `handle_rate_limits(response)` - Extract retry-after headers
- `verify_storage(vector_ids)` - Confirm successful storage

**Dependencies**:
- `cohere` - Cohere API client
- `qdrant-client` - Qdrant Python client
- Retry logic (exponential backoff)

**Configuration**:
```python
EMBEDDING_CONFIG = {
    "cohere_api_key": "${COHERE_API_KEY}",
    "cohere_model": "embed-english-v3.0",
    "embedding_dimension": 1024,
    "batch_size": 100,  # chunks per API call
    "retry_max_attempts": 5,
    "retry_initial_delay": 1,  # seconds
    "retry_exponential_base": 2,
    "qdrant_url": "${QDRANT_URL}",
    "qdrant_api_key": "${QDRANT_API_KEY}",
    "collection_name": "robotics_documentation"
}
```

**Qdrant Collection Schema**:
```python
from qdrant_client.models import VectorParams, Distance

COLLECTION_SCHEMA = {
    "name": "robotics_documentation",
    "vectors": VectorParams(
        size=1024,  # Cohere embed-english-v3.0 dimension
        distance=Distance.COSINE  # semantic similarity metric
    ),
    "payload": {
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

### 3.4 Verification & Logging Component

**Purpose**: Validate ingestion completeness and provide audit trail

**Key Functions**:
- `count_vectors_by_module()` - Distribution across modules
- `sample_semantic_query(query_text, top_k)` - Retrieve relevant chunks
- `validate_metadata_completeness()` - Check all chunks have required fields
- `generate_ingestion_report()` - Summary statistics and timing
- `log_operation(operation_type, details)` - Audit trail

**Verification Checks**:
1. Vector count matches chunk count (no storage failures)
2. All metadata fields present (no missing data)
3. Sample semantic queries return relevant results
4. No dimension mismatches in embeddings
5. Deduplication worked correctly
6. Incremental update doesn't create duplicates

**Logging Format**:
```json
{
  "timestamp": "2025-12-11T10:40:00Z",
  "operation": "crawl_complete",
  "details": {
    "urls_discovered": 15,
    "urls_crawled": 15,
    "pages_extracted": 15,
    "duration_seconds": 45
  }
}
```

---

## 4. Implementation Phases

### Phase 1: Core Crawler (User Story 1)
**Duration**: Estimated 1-2 work days
**Deliverable**: Fully functional website crawler

**Tasks**:
1. Set up project structure and dependencies
2. Implement URL discovery with BFS traversal
3. Implement HTML content extraction
4. Implement metadata preservation (module/section/lesson)
5. Add request delay and robots.txt compliance
6. Write unit tests for crawler functions
7. Test against live Docusaurus website

**Success Metrics**:
- All 15+ documentation pages discovered
- 100% URL coverage
- Hierarchy metadata preserved correctly
- No request timeouts or 403 errors

### Phase 2: Text Preprocessing (User Story 2)
**Duration**: Estimated 1-2 work days
**Deliverable**: Intelligent text chunking system

**Tasks**:
1. Implement tokenization using tiktoken
2. Implement semantic boundary detection (paragraphs, sections)
3. Implement chunk assembly with context preservation
4. Implement chunk ID generation
5. Implement deduplication logic
6. Write tests for edge cases (long pages, tables, code blocks)
7. Measure chunk distribution (200-500 total, 256-512 per chunk)

**Success Metrics**:
- 200-500 chunks total
- 100% chunks in 256-512 token range
- 0% mid-sentence splits
- Section headers preserved in output

### Phase 3: Embeddings & Storage (User Story 3)
**Duration**: Estimated 1-2 work days
**Deliverable**: End-to-end embedding pipeline

**Tasks**:
1. Set up Qdrant Cloud account and collection
2. Implement Cohere API integration
3. Implement batch processing logic
4. Implement retry logic with exponential backoff
5. Implement storage to Qdrant
6. Implement deduplication at storage level
7. Write tests for API failures and retries

**Success Metrics**:
- 100% of chunks have embeddings
- All embeddings stored in Qdrant
- Metadata queryable via Qdrant payload
- 0% storage failures
- Full pipeline completes in <10 minutes

### Phase 4: Verification & Audit (User Story 4)
**Duration**: Estimated 1 work day
**Deliverable**: Comprehensive verification toolkit

**Tasks**:
1. Implement vector count reporting by module
2. Implement sample semantic query functionality
3. Implement metadata validation checks
4. Implement logging system with timestamps
5. Write verification reports
6. Create incremental update handling
7. Write tests for verification logic

**Success Metrics**:
- Verification script runs without errors
- Sample queries return semantically relevant results
- All metadata validates successfully
- Incremental updates work without duplicates
- Full audit trail logged

---

## 5. Technology Stack & Dependencies

### Python Dependencies
```toml
[project.dependencies]
requests = "^2.31.0"           # HTTP client
beautifulsoup4 = "^4.12.0"     # HTML parsing
urllib3 = "^2.0.0"             # URL manipulation
cohere = "^5.0.0"              # Cohere embeddings API
qdrant-client = "^2.7.0"        # Qdrant vector DB client
tiktoken = "^0.5.0"            # Token counting
nltk = "^3.8.0"                # NLP utilities
python-dotenv = "^1.0.0"       # Environment variables
```

### External Services
- **Cohere API**: Embeddings generation (free tier: ~100 req/min)
- **Qdrant Cloud Free Tier**: Vector storage (~1GB, suitable for 200-500 vectors)
- **Target Website**: Publicly accessible Docusaurus deployment

### Development Tools
- **Python 3.8+**: Runtime environment
- **pytest**: Unit testing
- **black/flake8**: Code formatting and linting
- **mypy**: Type checking

---

## 6. Data Models & Schemas

### Page Model
```python
@dataclass
class WebPage:
    url: str
    title: str
    module: str
    section: str
    html_content: str
    text_content: str
    crawled_at: datetime
    page_type: str  # "lesson", "module_overview", etc.
    hierarchy_level: int
```

### Chunk Model
```python
@dataclass
class TextChunk:
    chunk_id: str
    source_url: str
    module: str
    section: str
    text: str
    token_count: int
    chunk_index: int  # position within page
    total_chunks: int  # total chunks for page
    created_at: datetime
```

### Embedding Model (Qdrant Payload)
```python
@dataclass
class EmbeddingMetadata:
    chunk_id: str
    source_url: str
    module: str
    section: str
    text: str  # preview/full text for search results
    token_count: int
    created_at: str  # ISO 8601
```

---

## 7. Error Handling Strategy

### Retry Logic
- **Transient Errors** (429, 500-599): Exponential backoff (1s → 2s → 4s → 8s → 16s)
- **Rate Limit** (429): Extract `Retry-After` header, respect it
- **Connection Errors**: Retry with backoff
- **Permanent Errors** (401, 403, 404): Log and skip/fail appropriately

### Error Categories
1. **Crawling Errors**: Website unavailable, 404s, timeout
   - Strategy: Log warning, skip page, continue with others
2. **Processing Errors**: Malformed content, encoding issues
   - Strategy: Log error, skip chunk, continue
3. **API Errors**: Cohere rate limit, authentication failure
   - Strategy: Retry with backoff, or graceful failure with message
4. **Storage Errors**: Qdrant connection lost
   - Strategy: Retry, ensure no partial uploads

---

## 8. Testing Strategy

### Unit Tests
- Crawler URL discovery and filtering
- HTML content extraction and cleanup
- Token counting and chunking logic
- Chunk ID generation
- Deduplication algorithm
- Retry logic and backoff
- Qdrant storage and retrieval

### Integration Tests
- End-to-end crawl → chunk → embed → store pipeline
- API rate limit handling
- Connection loss and recovery
- Incremental updates without duplication

### Manual Tests
- Sample semantic queries against live vector DB (10+ queries)
- Spot-check chunk quality and metadata
- Verify module coverage statistics
- Performance measurement (total time, API calls)

---

## 9. Operational Runbooks

### Running the Full Pipeline
```bash
python -m rag_pipeline.main \
  --website-url https://example.com/docs \
  --output-dir ./ingestion_output \
  --verify
```

### Running Incremental Updates
```bash
python -m rag_pipeline.incremental_update \
  --since "2025-12-01T00:00:00Z" \
  --verify
```

### Verification & Reporting
```bash
python -m rag_pipeline.verify \
  --sample-queries 10 \
  --generate-report
```

### Debugging & Logs
```bash
# View ingestion logs
tail -f logs/ingestion_$(date +%Y%m%d).log

# Inspect chunk quality
python -m rag_pipeline.inspect_chunks --module "Module 1" --sample-size 5

# Query vector DB manually
python -m rag_pipeline.query --query "How do robots learn?"
```

---

## 10. Deployment & Configuration

### Environment Variables
```env
# Cohere
COHERE_API_KEY=xxxx

# Qdrant Cloud
QDRANT_URL=https://xxxx.qdrant.io
QDRANT_API_KEY=xxxx

# Website
TARGET_WEBSITE_URL=https://example.com/docs

# Logging
LOG_LEVEL=INFO
LOG_DIR=./logs
```

### Configuration File (config.yaml)
```yaml
crawler:
  base_url: ${TARGET_WEBSITE_URL}
  request_delay: 0.5
  max_retries: 3
  respect_robots_txt: true

chunking:
  min_tokens: 100
  target_tokens: 350
  max_tokens: 512
  overlap_tokens: 50
  deduplication_threshold: 0.95

embeddings:
  cohere_model: embed-english-v3.0
  batch_size: 100
  retry_max_attempts: 5
  retry_initial_delay: 1

qdrant:
  collection_name: robotics_documentation
  timeout: 30

pipeline:
  verify_after_ingestion: true
  max_runtime_minutes: 10
```

---

## 11. Risk Analysis & Mitigation

### Risk 1: Cohere API Rate Limiting
**Severity**: Medium
**Impact**: Pipeline slowdown or partial failure
**Mitigation**:
- Implement batch size optimization (start with 50, increase if no rate limits)
- Use exponential backoff with Retry-After header respect
- Monitor API error rates during execution
- Plan execution during off-peak hours

### Risk 2: Qdrant Connection Loss Mid-Upload
**Severity**: Medium
**Impact**: Partial vector storage, potential duplicates
**Mitigation**:
- Implement transaction-like semantics (store all-or-nothing per batch)
- Add pre-upload validation of vector count vs. database count
- Implement incremental commit tracking
- Enable Qdrant backups/snapshots

### Risk 3: Website Content Changes
**Severity**: Low
**Impact**: Duplicate vectors for updated content
**Mitigation**:
- Track last crawl timestamp, skip unchanged pages on refresh
- Implement content hash deduplication
- Maintain changelog of ingested content versions

### Risk 4: Long Execution Time
**Severity**: Low
**Impact**: Longer feedback loop, resource usage
**Mitigation**:
- Optimize batch sizes for API efficiency
- Consider parallel processing for future scaling
- Cache intermediate results (pages, chunks)
- Profile and optimize slowest components

---

## 12. Success Metrics & Acceptance Criteria

### Crawler Phase
- ✅ 100% of public documentation pages discovered
- ✅ Zero 404 errors or timeouts
- ✅ Hierarchy metadata matches expected structure
- ✅ Processing time < 60 seconds

### Preprocessing Phase
- ✅ 200-500 chunks total (or documented reasoning if different)
- ✅ 100% chunks between 100-600 tokens
- ✅ 0% mid-sentence splits
- ✅ All section headers preserved

### Embedding Phase
- ✅ 100% of chunks have embeddings (no failed generations)
- ✅ All embeddings stored in Qdrant with metadata
- ✅ No duplicate embeddings in database
- ✅ Processing time < 10 minutes total

### Verification Phase
- ✅ Automated script validates all requirements
- ✅ 10+ sample queries return semantically relevant results
- ✅ All metadata fields present and valid
- ✅ Coverage statistics by module

---

## Next Steps

1. **Review & Approve Plan**: Confirm architecture decisions with stakeholders
2. **Generate Tasks**: Run `/sp.tasks` to create detailed task breakdown
3. **Set Up Development Environment**: Clone repository, install dependencies
4. **Begin Phase 1 Implementation**: Start with website crawler component
5. **Establish Monitoring**: Set up logging and verification infrastructure

---

## Appendix: Configuration Templates

### Docusaurus Website Analysis
- Expected: 4 modules × 3 lessons = 12 pages minimum
- Estimated chunks: 250-400 total (20-35 chunks per lesson)
- Estimated processing time: 5-8 minutes
- Estimated vector storage: 50-100 MB with metadata

### API Budgets
- Cohere: ~300-500 embedding requests (50+ free tier daily)
- Qdrant: ~300-500 vectors (well within free tier 1GB limit)
- No cost for ingestion (testing with free tiers)
