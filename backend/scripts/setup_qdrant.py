#!/usr/bin/env python3
"""
RAG Chatbot Qdrant Setup Script
Loads Docusaurus textbook content, chunks it, generates embeddings, and populates Qdrant
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict
import re
from uuid import uuid4
import time

# Add backend to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import cohere

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TextChunker:
    """Splits markdown content into semantic chunks of 200-300 words"""

    @staticmethod
    def split_into_chunks(text: str, min_words: int = 200, max_words: int = 300) -> List[str]:
        """
        Split text into semantic chunks based on word count and paragraph boundaries

        Args:
            text: The text to chunk
            min_words: Minimum words per chunk
            max_words: Maximum words per chunk

        Returns:
            List of text chunks
        """
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        chunks = []
        current_chunk = []
        current_word_count = 0

        for paragraph in paragraphs:
            word_count = len(paragraph.split())

            # If adding this paragraph exceeds max, save current chunk
            if current_word_count + word_count > max_words and current_chunk:
                chunk_text = '\n\n'.join(current_chunk)
                chunks.append(chunk_text)
                current_chunk = [paragraph]
                current_word_count = word_count
            else:
                current_chunk.append(paragraph)
                current_word_count += word_count

        # Add final chunk
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            chunks.append(chunk_text)

        return chunks


class DocLoader:
    """Loads Docusaurus MDX files and extracts content"""

    def __init__(self, docs_path: str):
        """
        Initialize document loader

        Args:
            docs_path: Path to docs folder
        """
        self.docs_path = Path(docs_path)
        if not self.docs_path.exists():
            raise FileNotFoundError(f"Docs folder not found: {docs_path}")

    def load_documents(self) -> List[Dict[str, str]]:
        """
        Load all MDX/MD files from docs folder

        Returns:
            List of documents with 'text', 'source_url', 'title', 'chapter' fields
        """
        documents = []

        for mdx_file in self.docs_path.rglob('*.mdx'):
            try:
                content = mdx_file.read_text(encoding='utf-8')

                # Extract markdown content (remove YAML frontmatter)
                text = self._extract_markdown(content)

                if not text.strip():
                    logger.warning(f"Empty content in {mdx_file.name}")
                    continue

                # Extract title from content
                title = self._extract_title(content)

                # Get relative path for source_url
                rel_path = mdx_file.relative_to(self.docs_path)
                source_url = f"/docs/{rel_path.parent}/{mdx_file.stem}"

                # Extract chapter from path
                chapter = str(rel_path.parent).replace('-', ' ').title()

                documents.append({
                    'text': text,
                    'source_url': source_url,
                    'title': title,
                    'chapter': chapter
                })

                logger.info(f"✅ Loaded: {mdx_file.name} ({len(text.split())} words)")

            except Exception as e:
                logger.error(f"❌ Failed to load {mdx_file.name}: {e}")
                continue

        logger.info(f"\n📚 Total documents loaded: {len(documents)}")
        return documents

    @staticmethod
    def _extract_markdown(content: str) -> str:
        """Remove YAML frontmatter and return markdown content"""
        # Remove YAML frontmatter (between --- markers)
        if content.startswith('---'):
            try:
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    return parts[2].strip()
            except:
                pass
        return content.strip()

    @staticmethod
    def _extract_title(content: str) -> str:
        """Extract title from markdown content (first H1 heading)"""
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line.replace('# ', '').strip()
        return "Untitled"


class QdrantSetup:
    """Manages Qdrant collection setup and data insertion"""

    def __init__(self, qdrant_url: str, api_key: str, collection_name: str, embedding_dim: int):
        """
        Initialize Qdrant client

        Args:
            qdrant_url: Qdrant instance URL
            api_key: Qdrant API key
            collection_name: Name of collection to create/use
            embedding_dim: Embedding dimension (must match embeddings generated)
        """
        self.client = QdrantClient(url=qdrant_url, api_key=api_key, timeout=30)
        self.collection_name = collection_name
        self.embedding_dim = embedding_dim

    def setup_collection(self) -> bool:
        """
        Create collection if it doesn't exist

        Returns:
            True if collection exists or was created, False otherwise
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]

            if self.collection_name in collection_names:
                logger.info(f"✅ Collection '{self.collection_name}' already exists")
                return True

            # Create new collection
            logger.info(f"📦 Creating collection '{self.collection_name}'...")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"✅ Collection '{self.collection_name}' created successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to setup collection: {e}", exc_info=True)
            return False

    def upsert_documents(self, chunks_with_embeddings: List[Dict]) -> int:
        """
        Upsert document chunks into Qdrant

        Args:
            chunks_with_embeddings: List of dicts with 'text', 'embedding', and metadata

        Returns:
            Number of documents inserted
        """
        if not chunks_with_embeddings:
            logger.warning("No chunks to upsert")
            return 0

        try:
            points = []
            for item in chunks_with_embeddings:
                point_id = int(uuid4().int % 2**63)

                point = PointStruct(
                    id=point_id,
                    vector=item['embedding'],
                    payload={
                        'text': item['text'],
                        'source_url': item['source_url'],
                        'title': item['title'],
                        'chapter': item['chapter']
                    }
                )
                points.append(point)

            # Upsert to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

            logger.info(f"✅ Upserted {len(points)} chunks into '{self.collection_name}'")
            return len(points)

        except Exception as e:
            logger.error(f"❌ Failed to upsert documents: {e}", exc_info=True)
            return 0

    def get_collection_stats(self) -> Dict:
        """Get collection statistics"""
        try:
            stats = self.client.get_collection(self.collection_name)
            return {
                'points_count': stats.points_count if hasattr(stats, 'points_count') else 'N/A',
                'dimension': stats.config.params.vectors.size if hasattr(stats, 'config') and hasattr(stats.config, 'params') else 'N/A'
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {'points_count': 'N/A', 'dimension': 'N/A'}


def main():
    """Main execution"""
    logger.info("🚀 Starting RAG Chatbot Qdrant Setup...\n")

    # Load environment variables
    qdrant_url = os.getenv('QDRANT_URL')
    qdrant_api_key = os.getenv('QDRANT_API_KEY')
    qdrant_collection = os.getenv('QDRANT_COLLECTION_NAME', 'documents')
    cohere_api_key = os.getenv('COHERE_API_KEY')
    embedding_model = os.getenv('EMBEDDING_MODEL', 'embed-english-v3.0')
    embedding_dim = int(os.getenv('EMBEDDING_DIMENSION', '1024'))

    # Validate environment
    errors = []
    if not qdrant_url:
        errors.append("QDRANT_URL not set")
    if not qdrant_api_key:
        errors.append("QDRANT_API_KEY not set")
    if not cohere_api_key:
        errors.append("COHERE_API_KEY not set")

    if errors:
        logger.error(f"❌ Configuration errors:\n  - " + "\n  - ".join(errors))
        return 1

    logger.info(f"✅ Configuration loaded:")
    logger.info(f"   - Qdrant: {qdrant_url}")
    logger.info(f"   - Collection: {qdrant_collection}")
    logger.info(f"   - Embedding model: {embedding_model}\n")

    # Step 1: Load documents
    logger.info("📖 Step 1: Loading textbook documents...")
    docs_path = Path(__file__).parent.parent.parent / 'docs'
    try:
        loader = DocLoader(str(docs_path))
        documents = loader.load_documents()

        if not documents:
            logger.error("❌ No documents loaded")
            return 1

    except Exception as e:
        logger.error(f"❌ Failed to load documents: {e}", exc_info=True)
        return 1

    # Step 2: Chunk documents
    logger.info("\n✂️  Step 2: Chunking documents (200-300 words per chunk)...")
    chunker = TextChunker()
    chunks = []

    for doc in documents:
        doc_chunks = chunker.split_into_chunks(doc['text'])
        for chunk_text in doc_chunks:
            chunks.append({
                'text': chunk_text,
                'source_url': doc['source_url'],
                'title': doc['title'],
                'chapter': doc['chapter']
            })

    logger.info(f"✅ Created {len(chunks)} chunks from {len(documents)} documents")

    # Step 3: Generate embeddings
    logger.info("\n🔢 Step 3: Generating embeddings with Cohere...")
    try:
        cohere_client = cohere.Client(api_key=cohere_api_key)

        # Batch embed texts (Cohere has limits, typically 100 at a time)
        batch_size = 50
        chunks_with_embeddings = []

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            texts = [chunk['text'] for chunk in batch]

            logger.info(f"   Embedding batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}...")

            try:
                response = cohere_client.embed(
                    texts=texts,
                    model=embedding_model,
                    input_type='search_document'
                )

                embeddings = response.embeddings
                for chunk, embedding in zip(batch, embeddings):
                    chunk['embedding'] = embedding
                    chunks_with_embeddings.append(chunk)

            except Exception as e:
                logger.error(f"❌ Embedding batch failed: {e}", exc_info=True)
                # Continue with next batch
                continue

            # Rate limiting
            time.sleep(0.5)

        logger.info(f"✅ Generated {len(chunks_with_embeddings)} embeddings")

    except Exception as e:
        logger.error(f"❌ Failed to generate embeddings: {e}", exc_info=True)
        return 1

    # Step 4: Setup Qdrant and upsert
    logger.info("\n📦 Step 4: Setting up Qdrant collection...")
    try:
        qdrant = QdrantSetup(qdrant_url, qdrant_api_key, qdrant_collection, embedding_dim)

        # Setup collection
        if not qdrant.setup_collection():
            return 1

        # Upsert documents
        logger.info("\n📤 Step 5: Uploading chunks to Qdrant...")
        inserted = qdrant.upsert_documents(chunks_with_embeddings)

        if inserted == 0:
            logger.error("❌ No documents were inserted")
            return 1

        # Verify
        logger.info("\n✅ Step 6: Verifying collection...")
        stats = qdrant.get_collection_stats()
        logger.info(f"   - Total points: {stats.get('points_count', 'N/A')}")
        logger.info(f"   - Vector dimension: {stats.get('dimension', 'N/A')}")

    except Exception as e:
        logger.error(f"❌ Qdrant operation failed: {e}", exc_info=True)
        return 1

    logger.info("\n" + "="*60)
    logger.info("🎉 RAG Chatbot Qdrant setup completed successfully!")
    logger.info("="*60)
    logger.info(f"\n📊 Summary:")
    logger.info(f"   - Documents processed: {len(documents)}")
    logger.info(f"   - Chunks created: {len(chunks_with_embeddings)}")
    logger.info(f"   - Collection: {qdrant_collection}")
    logger.info(f"   - Ready for RAG queries!\n")

    return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
