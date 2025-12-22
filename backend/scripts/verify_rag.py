#!/usr/bin/env python3
"""
RAG Chatbot Verification Script
Tests the complete RAG setup: Qdrant collection, embeddings, and retrieval
"""

import os
import sys
import logging
from pathlib import Path

# Add backend to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from qdrant_client import QdrantClient
import cohere

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def verify_qdrant():
    """Verify Qdrant connection and collection"""
    logger.info("\n🔍 Verifying Qdrant Connection...")

    qdrant_url = os.getenv('QDRANT_URL')
    qdrant_api_key = os.getenv('QDRANT_API_KEY')
    qdrant_collection = os.getenv('QDRANT_COLLECTION_NAME', 'documents')

    try:
        client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key, timeout=10)

        # Test connection
        client.get_collections()
        logger.info("✅ Qdrant connection: OK")

        # Check collection exists
        try:
            stats = client.get_collection(qdrant_collection)
            logger.info(f"✅ Collection '{qdrant_collection}' exists")
            logger.info(f"   - Points count: {stats.points_count}")

            if stats.points_count == 0:
                logger.warning(f"⚠️  Collection is empty! Run setup_qdrant.py first")
                return False

            return True
        except Exception as e:
            logger.error(f"❌ Collection '{qdrant_collection}' not found: {e}")
            logger.info("   Run 'python3 scripts/setup_qdrant.py' to create it")
            return False

    except Exception as e:
        logger.error(f"❌ Qdrant connection failed: {e}", exc_info=True)
        return False


def verify_cohere():
    """Verify Cohere API connection"""
    logger.info("\n🔍 Verifying Cohere API...")

    cohere_api_key = os.getenv('COHERE_API_KEY')
    embedding_model = os.getenv('EMBEDDING_MODEL', 'embed-english-v3.0')

    if not cohere_api_key:
        logger.error("❌ COHERE_API_KEY not set in .env")
        return False

    try:
        client = cohere.Client(api_key=cohere_api_key)

        # Test embedding
        test_text = "Physical AI is the intersection of machine learning and robotics"
        response = client.embed(
            texts=[test_text],
            model=embedding_model,
            input_type='search_document'
        )

        if response.embeddings and len(response.embeddings[0]) > 0:
            logger.info(f"✅ Cohere API: OK")
            logger.info(f"   - Model: {embedding_model}")
            logger.info(f"   - Embedding dimension: {len(response.embeddings[0])}")
            return True
        else:
            logger.error("❌ No embeddings returned from Cohere")
            return False

    except Exception as e:
        logger.error(f"❌ Cohere API failed: {e}", exc_info=True)
        return False


def verify_retrieval():
    """Verify retrieval functionality"""
    logger.info("\n🔍 Verifying Retrieval (RAG Query)...")

    qdrant_url = os.getenv('QDRANT_URL')
    qdrant_api_key = os.getenv('QDRANT_API_KEY')
    qdrant_collection = os.getenv('QDRANT_COLLECTION_NAME', 'documents')
    cohere_api_key = os.getenv('COHERE_API_KEY')
    embedding_model = os.getenv('EMBEDDING_MODEL', 'embed-english-v3.0')

    try:
        # Initialize clients
        qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key, timeout=10)
        cohere_client = cohere.Client(api_key=cohere_api_key)

        # Test query
        test_query = "What is Physical AI?"

        # Embed query
        query_embedding = cohere_client.embed(
            texts=[test_query],
            model=embedding_model,
            input_type='search_query'
        ).embeddings[0]

        # Search in Qdrant using query_points
        results = qdrant_client.query_points(
            collection_name=qdrant_collection,
            query=query_embedding,
            limit=3,
            score_threshold=0.3,
            with_payload=True
        )

        if results:
            logger.info(f"✅ Retrieval: OK")
            logger.info(f"   - Test query: '{test_query}'")

            # Handle both old and new API structures
            result_points = results.points if hasattr(results, 'points') else results
            logger.info(f"   - Results found: {len(result_points)}")

            for i, result in enumerate(result_points[:3], 1):
                payload = result.payload if hasattr(result, 'payload') else result.get('payload', {})
                score = result.score if hasattr(result, 'score') else result.get('score', 0)
                title = payload.get('title', 'N/A') if isinstance(payload, dict) else 'N/A'
                logger.info(f"   - Result {i}: {title} (score: {score:.3f})")
            return True
        else:
            logger.warning(f"⚠️  No results found for query: '{test_query}'")
            return False

    except Exception as e:
        logger.error(f"❌ Retrieval test failed: {e}", exc_info=True)
        return False


def main():
    """Run all verification tests"""
    logger.info("=" * 60)
    logger.info("🧪 RAG Chatbot Setup Verification")
    logger.info("=" * 60)

    results = {
        'Qdrant': verify_qdrant(),
        'Cohere': verify_cohere(),
        'Retrieval': verify_retrieval()
    }

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 Verification Summary:")
    logger.info("=" * 60)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {test_name}")

    # Overall result
    all_passed = all(results.values())
    logger.info("=" * 60)

    if all_passed:
        logger.info("🎉 All checks passed! RAG chatbot is ready.")
        logger.info("\nYou can now:")
        logger.info("  1. Start the backend: python3 main.py")
        logger.info("  2. Test the API: POST http://localhost:8000/api/v1/query")
        logger.info("  3. Ask questions about the textbook!")
        return 0
    else:
        logger.error("\n❌ Some checks failed. Please review the errors above.")
        logger.error("\nCommon issues:")
        logger.error("  - Run 'python3 scripts/setup_qdrant.py' to populate the database")
        logger.error("  - Check your .env file for correct API keys")
        logger.error("  - Ensure Qdrant cloud instance is running")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
