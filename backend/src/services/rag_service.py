"""RAG (Retrieval-Augmented Generation) service."""

import logging
from typing import Dict, List
import cohere
import re
from .qdrant_service import QdrantService

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class RAGService:
    """Service for retrieval-augmented generation using Cohere and Qdrant."""

    def __init__(
        self,
        cohere_api_key: str,
        qdrant_service: QdrantService,
        model: str = "embed-english-v3.0",
    ):
        """
        Initialize RAG service.

        Args:
            cohere_api_key: Cohere API key
            qdrant_service: Initialized Qdrant service
            model: Cohere embedding model to use
        """
        self.model = model  

        self.embedding_model = "embed-english-v3.0"
        self.chat_model = "command-r-plus-08-2024"

        self.qdrant_service = qdrant_service
        self.embedding_dimension = 1024

        try:
            self.cohere_client = cohere.Client(api_key=cohere_api_key)
            logger.info("Cohere client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Cohere client: {e}")
            raise

    def _clean_text(self, text: str) -> str:
        """
        Clean context text by removing headings, URLs, and extra whitespace.
        This ensures the answer is human-style and not section-heavy.
        """
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)  # remove markdown headers
        text = re.sub(r'https?://\S+', '', text)  # remove URLs
        text = re.sub(r'\n+', ' ', text)  # collapse newlines
        text = re.sub(r'\s+', ' ', text)  # collapse multiple spaces
        return text.strip()

    def summarize_text(self, text: str, prompt: str = None, max_sentences: int = 3) -> str:
        """
        Summarize text concisely in natural language.
    
        Changes made:
        - Output now avoids abrupt sentence breaks
        - Collapses excessive whitespace
        - Ensures the first letters of sentences are capitalized
        - Handles cases where text is very short
        """
        text = text.strip()
        if not text:
            return "No relevant content available."

        try:
            # Safe prompt for LLM
            safe_prompt = (prompt or text)[:2000]

            response = self.cohere_client.chat(
                model=self.chat_model,
                message=safe_prompt,
                max_tokens=150,  # slightly increased for smoother sentences
                temperature=0.3
            )

            output = response.text.strip()

            # Split into sentences safely
            sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', output) if s]
        
            # Capitalize first letter of each sentence (optional)
            sentences = [s[0].upper() + s[1:] if s else s for s in sentences]

            # Take first max_sentences
            output = " ".join(sentences[:max_sentences]).strip()

            # Ensure ending period
            if not output.endswith("."):
                output += "."

            return output

        except Exception as e:
            logger.warning(f"Cohere summarization failed: {e}")

        # Fallback local summarizer if API fails
        sentences = re.split(r'(?<=[.!?]) +', text.replace("\n", " "))
        sentences = [s.strip() for s in sentences if len(s) > 25]
        summary = sentences[:max_sentences]

        # Capitalize first letter
        summary = [s[0].upper() + s[1:] if s else s for s in summary]

        return " ".join(summary) + "."

    def _embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for text using Cohere.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        try:
            response = self.cohere_client.embed(
                texts=[text],
                model=self.embedding_model,
                input_type="search_query",
            )

            raw = response.embeddings[0]

            # Normalize embedding (fix for Railway bug)
            if isinstance(raw, list):
                embedding = [float(x) for x in raw]
            else:
                embedding = list(map(float, raw))

            logger.debug(f"Generated embedding size: {len(embedding)}")
            return embedding

        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise

    def _retrieve_context(self, query_vector: List[float], top_k: int = 5) -> List[Dict]:
        """
        Retrieve relevant context from vector database.

        Args:
            query_vector: Query embedding
            top_k: Number of results to retrieve

        Returns:
            List of relevant documents/chunks
        """
        try:
            results = self.qdrant_service.search(query_vector, top_k=top_k)
            logger.info(f"Retrieved {len(results)} context chunks")
            return results

        except Exception as e:
            logger.error(f"Failed to retrieve context: {e}")
            raise

    def _format_context(self, context: List[Dict]) -> str:
        """
        Format retrieved context into a readable string.

        Args:
            context: List of context chunks

        Returns:
            Formatted context string
        """
        if not context:
            return "No relevant context found."

        formatted = "## Context from Documentation\n\n"
        for i, chunk in enumerate(context, 1):
            source = chunk.get("source_url", "Unknown source")
            section = chunk.get("section", "No section")
            score = chunk.get("score", 0)
            text = chunk.get("text", "")

            # Limit text preview
            text_preview = text[:300] + "..." if len(text) > 300 else text

            formatted += f"**Source {i}** (Score: {score:.3f})\n"
            formatted += f"- URL: {source}\n"
            formatted += f"- Section: {section}\n"
            formatted += f"- Content: {text_preview}\n\n"

        return formatted

    def query(
        self,
        question: str,
        context: str | None = None,
        conversation_id: str | None = None,
        top_k: int = 5,
        include_context: bool = True,
        include_sources: bool = False
    ) -> Dict:

        try:
            logger.info(f"Processing question: {question}")

            original_question = question

            # Validation
            if not question or not isinstance(question, str):
                raise ValueError("Question must be a non-empty string")
            if len(question.strip()) < 2:
                raise ValueError("Question is too short")
                
            if context:
                question = f"{context}\n\nUser question: {question}"


            # Step 1: Embed the question
            query_vector = self._embed_text(question)

            # Step 2: Retrieve context
            context_chunks = self._retrieve_context(query_vector, top_k=top_k)

            # Deduplicate context
            unique_chunks = []
            seen_texts = set()
            for chunk in context_chunks:
                text = chunk.get("text", "").strip()
                text_hash = hash(text)
                if text and text_hash not in seen_texts:
                    seen_texts.add(text_hash)
                    unique_chunks.append(chunk)
            context_chunks = unique_chunks
            logger.info(f"Context chunks after deduplication: {len(context_chunks)}")

            # Build raw text safely
            raw_text = " ".join(c.get("text", "") for c in context_chunks)
            if not raw_text.strip():
                return {
                    "question": original_question,
                    "answer": "No relevant information found in the knowledge base.",
                    "context": "",
                    "sources": [] if include_sources else None,
                    "metadata": {
                        "model": self.model,
                        "context_chunks": 0,
                        "query_succeeded": True,
                    },
                }

            # Limit context length for LLM
            MAX_CONTEXT_LENGTH = 1200
            raw_text_for_summary = self._clean_text(raw_text[:MAX_CONTEXT_LENGTH])

            # Generate concise answer
            concise_answer = self.summarize_text(
                text=raw_text_for_summary,
                prompt=(
                    "Answer this question in a concise, natural way using the context below.\n\n"
                    f"Context:\n{raw_text_for_summary}\n\n"
                    f"Question: {question}"
                ),
                max_sentences=3
            )

            # Optional sources, clean without duplicates
            sources = []
            if include_sources:
                seen_urls = set()
                for c in context_chunks:
                    url = c.get("source_url") or c.get("url")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        sources.append({
                            "url": url,
                            "section": c.get("section"),
                            "score": round(c.get("score", 0), 3)
                        })

            # Build final response
            response = {
                "question": original_question,
                "answer": concise_answer,
                "context": raw_text if include_context else "",
                "sources": sources if include_sources else None,
                "metadata": {
                    "model": self.model,
                    "context_chunks": len(context_chunks),
                    "query_succeeded": True,
                },
            }

            return response

        except ValueError as e:
            logger.warning(f"Validation error: {e}")
            raise

        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            raise


    def health_check(self) -> dict:
        """
        Central health orchestrator.
        This is the ONLY source of truth for API health.
        """

        qdrant_ok = False
        cohere_ok = False

        # ---------- QDRANT ----------
        try:
            self.qdrant_service.client.get_collections()
            qdrant_ok = True
        except Exception as e:
            logger.error(f"Qdrant health failed: {e}")

         # ---------- COHERE ----------
        try:
            response = self.cohere_client.chat(
                model=self.chat_model,
                message="ping",
                max_tokens=5,
                temperature=0,
            )
            if response and response.text:
                cohere_ok = True
        except Exception as e:
            logger.error(f"Cohere health failed: {e}")

        status = "healthy" if qdrant_ok and cohere_ok else "degraded"

        return {
            "status": status,
            "qdrant": "connected" if qdrant_ok else "disconnected",
            "cohere": "connected" if cohere_ok else "disconnected",
            "model": self.model,
        }
