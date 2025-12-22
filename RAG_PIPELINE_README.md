# RAG Pipeline: Docusaurus Website Ingestion

A complete Python-based pipeline for ingesting Docusaurus documentation websites into Qdrant vector database using Cohere embeddings.

## Features

- **Website Crawler**: Discovers and extracts documentation pages using BFS traversal
- **Smart Chunking**: Intelligently chunks text with semantic boundaries (256-512 tokens)
- **Embedding Generation**: Creates embeddings using Cohere API with batch processing
- **Vector Storage**: Stores embeddings in Qdrant Cloud with rich metadata
- **Verification**: Validates data quality and provides comprehensive reports
- **Logging & Audit Trail**: Complete structured logging for debugging and compliance

## Architecture

```
┌─────────────────────────────────────────┐
│    Website Crawler (BFS Traversal)      │
│  Discover → Extract → Parse → Store     │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   Text Preprocessor (Chunking)          │
│  Normalize → Chunk → Prepend → Dedupe   │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   Embedding Generation (Cohere)         │
│  Batch → Embed → Store in Qdrant        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   Verification & Reporting              │
│  Validate → Verify → Report             │
└─────────────────────────────────────────┘
```

## Installation

1. **Clone and setup**:
   ```bash
   # Install dependencies
   pip install -r requirements.txt

   # Download NLTK data
   python -m nltk.downloader punkt
   ```

2. **Configure environment**:
   ```bash
   # Copy and fill in credentials
   cp .env.rag.example .env.rag
   # Edit .env.rag with your API keys
   ```

3. **Optional: Copy config template**:
   ```bash
   cp config.yaml.example config.yaml
   ```

## Configuration

### Environment Variables (.env.rag)

Required:
- `COHERE_API_KEY`: Your Cohere API key
- `QDRANT_URL`: Your Qdrant Cloud instance URL
- `QDRANT_API_KEY`: Your Qdrant API key

Optional:
- `TARGET_WEBSITE_URL`: Website to crawl (default: from config)
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)

### Configuration File (config.yaml)

```yaml
crawler:
  base_url: https://example.com/docs
  request_delay: 0.5          # Seconds between requests
  timeout: 10                 # Request timeout
  max_pages: null             # Limit crawling (null = unlimited)
  respect_robots_txt: true

chunking:
  min_tokens: 100
  target_tokens: 350
  max_tokens: 512
  overlap_tokens: 50

embedding:
  model: "embed-english-v3.0"
  embedding_dimension: 1024
  batch_size: 100
  retry_max_attempts: 5
  retry_initial_delay: 1

retry:
  max_attempts: 5
  initial_delay: 1
  exponential_base: 2
  max_delay: 60
```

## Usage

### Run Full Pipeline

```bash
python -m rag_pipeline.main
```

Options:
- `--env-file`: Path to .env file (default: .env)
- `--config-file`: Path to config.yaml (default: config.yaml)
- `--verify-only`: Run verification without embedding generation

### Example: Custom Config Files

```bash
python -m rag_pipeline.main \
  --env-file .env.rag \
  --config-file config.yaml
```

### Programmatic Usage

```python
from rag_pipeline.main import run_pipeline
from rag_pipeline.config import Config

# Run pipeline
result = run_pipeline(
    env_file=".env.rag",
    config_file="config.yaml"
)

print(f"Crawled: {result['crawled_pages']} pages")
print(f"Created: {result['created_chunks']} chunks")
print(f"Stored: {result['vector_count']} vectors")
print(f"Report: {result['report_file']}")
```

## Output

The pipeline produces:
- **Logs**: `logs/ingestion_YYYYMMDD_HHMMSS.log` - Complete execution log
- **Operations Log**: `logs/operations_YYYYMMDD_HHMMSS.jsonl` - Structured operation data
- **Crawl Results**: `output/crawl_results_*.json` - Discovered pages metadata
- **Chunks**: `output/chunks_*.json` - Text chunks with metadata
- **Report**: `reports/ingestion_report_*.md` - Comprehensive quality report

## Success Criteria

✅ **Phase 1: Website Discovery**
- Crawls all public documentation pages (100% coverage)
- Filters navigation/UI elements
- Preserves hierarchy metadata

✅ **Phase 2: Text Preprocessing**
- Creates 256-512 token chunks with semantic boundaries
- Preserves source references and section headers
- Deduplicates near-identical chunks

✅ **Phase 3: Embedding Generation**
- Generates embeddings for 100% of chunks
- Handles rate limits with exponential backoff
- Stores with complete metadata

✅ **Phase 4: Verification**
- Reports vector coverage by module
- Validates semantic search functionality
- Checks metadata completeness

## Testing

Run tests:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=rag_pipeline tests/
```

Key test files:
- `tests/test_imports.py` - Module importability
- `tests/test_crawler.py` - Crawler functionality
- `tests/test_preprocessor.py` - Text processing
- `tests/test_integration.py` - Full pipeline (optional)

## Troubleshooting

### Import Errors
```bash
# Ensure Python path is set
export PYTHONPATH=/home/rajda/task_1:$PYTHONPATH
python -m rag_pipeline.main
```

### API Rate Limits
The pipeline includes exponential backoff retry logic. Adjust in config.yaml:
```yaml
retry:
  max_attempts: 10
  initial_delay: 2
  exponential_base: 2
  max_delay: 120
```

### Large Websites
Limit crawling in config.yaml:
```yaml
crawler:
  max_pages: 50  # Limit to 50 pages for testing
```

### Memory Issues
Process in batches by manually chunking the work or reducing batch_size:
```yaml
embedding:
  batch_size: 50  # Reduce from 100
```

## Performance

Typical performance (varies by website):
- Crawling: ~0.5-2 sec per page
- Preprocessing: ~100-500 ms per page
- Embedding: ~10-50 ms per chunk
- Full pipeline: ~5-15 minutes for 15-20 page site

## Architecture Decisions

1. **Python-based pipeline**: Separates ingestion from web frontend, enables batch processing
2. **BFS crawling**: Discovers all pages systematically, respects robots.txt
3. **Semantic chunking**: Respects paragraph/section boundaries for better embeddings
4. **Batch embedding**: More efficient than streaming, allows retry at batch level
5. **Qdrant Cloud**: Managed vector database eliminates infrastructure burden

## Security

- API keys stored in environment variables (never committed)
- No sensitive data logged to files
- Uses HTTPS for all API calls
- Respects website robots.txt by default

## Limitations

- Requires JavaScript-rendered content to be served as static HTML
- Text extraction depends on HTML structure (Docusaurus-optimized)
- Rate limits depend on API quotas
- No incremental updates (re-crawls full website each run)

## Future Enhancements

- [ ] Incremental updates (detect new/changed pages)
- [ ] Parallel crawling
- [ ] Support for multiple embedding models
- [ ] Database connection pooling
- [ ] Webhook notifications on completion
- [ ] Web UI for pipeline monitoring

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review config in `config.yaml`
3. Verify credentials in `.env.rag`
4. Run tests: `pytest -v tests/`

## License

See main project LICENSE file.
