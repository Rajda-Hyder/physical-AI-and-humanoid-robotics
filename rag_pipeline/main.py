"""Main entry point for RAG pipeline."""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from .config import Config
from .crawler import DocumentationCrawler
from .embeddings import CohereEmbeddingsGenerator, generate_and_store_embeddings
from .logging_utils import get_logger
from .preprocessor import TextPreprocessor
from .storage import QdrantVectorStore
from .verification import RAGVerifier


def save_crawl_results(results: list, output_dir: str = "output") -> str:
    """Save crawl results to JSON file."""
    Path(output_dir).mkdir(exist_ok=True)
    output_file = Path(output_dir) / f"crawl_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    data = [
        {
            "url": r.url,
            "title": r.title,
            "module": r.module,
            "section": r.section,
            "crawled_at": r.crawled_at.isoformat(),
        }
        for r in results
    ]

    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

    return str(output_file)


def save_chunks_to_file(chunks: list, output_dir: str = "output", format: str = "json") -> str:
    """Save chunks to file."""
    Path(output_dir).mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if format == "json":
        output_file = Path(output_dir) / f"chunks_{timestamp}.json"
        data = [
            {
                "chunk_id": c.chunk_id,
                "source_url": c.source_url,
                "module": c.module,
                "section": c.section,
                "text": c.text[:100] + "...",
                "token_count": c.token_count,
                "created_at": c.created_at.isoformat(),
            }
            for c in chunks
        ]
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)
    else:
        output_file = Path(output_dir) / f"chunks_{timestamp}.csv"
        import csv

        with open(output_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["chunk_id", "source_url", "module", "section", "token_count"])
            for c in chunks:
                writer.writerow([c.chunk_id, c.source_url, c.module, c.section, c.token_count])

    return str(output_file)


def run_pipeline(
    config: Optional[Config] = None,
    env_file: Optional[str] = None,
    config_file: Optional[str] = None,
    verify_only: bool = False,
) -> dict:
    """Run complete RAG pipeline."""
    logger = get_logger()

    # Load configuration
    if config is None:
        config = Config(env_file=env_file, config_file=config_file)

    logger.log_info("Starting RAG pipeline")
    start_time = datetime.utcnow()

    try:
        # Phase 1: Website Crawling
        logger.log_info("Phase 1: Crawling website")
        crawler_config = config.get_crawler_config()
        crawler = DocumentationCrawler(crawler_config)
        crawl_results = crawler.crawl_website()

        logger.log_info(f"Crawled {len(crawl_results)} pages")

        # Save crawl results
        crawl_file = save_crawl_results(crawl_results)
        logger.log_info(f"Crawl results saved to {crawl_file}")

        # Phase 2: Text Preprocessing
        logger.log_info("Phase 2: Preprocessing content")
        chunking_config = config.get_chunking_config()
        preprocessor = TextPreprocessor(chunking_config)
        chunks = preprocessor.preprocess_crawled_content(crawl_results)

        logger.log_info(f"Created {len(chunks)} chunks")

        # Save chunks
        chunks_file = save_chunks_to_file(chunks)
        logger.log_info(f"Chunks saved to {chunks_file}")

        # Phase 3: Vector Storage Setup
        logger.log_info("Phase 3: Setting up vector database")
        vector_store = QdrantVectorStore(
            url=config.qdrant_url,
            api_key=config.qdrant_api_key,
            collection_name=config.qdrant_collection,
        )

        vector_store.create_collection(vector_size=1024)

        # Phase 4: Embedding Generation and Storage
        if not verify_only:
            logger.log_info("Phase 4: Generating and storing embeddings")
            embedding_config = config.get_embedding_config()

            generator = CohereEmbeddingsGenerator(
                api_key=config.cohere_api_key,
                model=config.cohere_model,
            )

            result = generate_and_store_embeddings(chunks, embedding_config, vector_store)

            logger.log_info(f"Stored {result['embeddings_stored']} embeddings")

        # Phase 5: Verification
        logger.log_info("Phase 5: Running verification")
        generator = CohereEmbeddingsGenerator(
            api_key=config.cohere_api_key,
            model=config.cohere_model,
        )
        verifier = RAGVerifier(vector_store, generator)

        coverage = verifier.report_vector_coverage()
        logger.log_info(f"Vector coverage: {coverage}")

        # Generate report
        end_time = datetime.utcnow()
        report = verifier.generate_ingestion_report(
            start_time,
            end_time,
            {
                "urls_discovered": len(crawl_results),
                "urls_crawled": len(crawl_results),
            },
            {
                "chunks_created": len(chunks),
                "chunks_deduplicated": 0,
                "chunks_final": len(chunks),
                "min_tokens": min((c.token_count for c in chunks), default=0),
                "avg_tokens": sum(c.token_count for c in chunks) // len(chunks)
                if chunks
                else 0,
                "max_tokens": max((c.token_count for c in chunks), default=0),
            },
        )

        # Save report
        Path("reports").mkdir(exist_ok=True)
        report_file = Path("reports") / f"ingestion_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, "w") as f:
            f.write(report)

        logger.log_info(f"Report saved to {report_file}")
        logger.log_info("Pipeline execution completed successfully")

        return {
            "success": True,
            "crawled_pages": len(crawl_results),
            "created_chunks": len(chunks),
            "vector_count": coverage.get("total_vectors", 0),
            "report_file": str(report_file),
        }

    except Exception as e:
        logger.log_error(f"Pipeline execution failed: {e}")
        raise


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="RAG Pipeline for Docusaurus ingestion")
    parser.add_argument("--env-file", default=".env", help="Path to .env file")
    parser.add_argument("--config-file", default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--verify-only", action="store_true", help="Run verification only")

    args = parser.parse_args()

    try:
        result = run_pipeline(
            env_file=args.env_file,
            config_file=args.config_file,
            verify_only=args.verify_only,
        )
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
