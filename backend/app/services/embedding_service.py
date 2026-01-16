"""
Embedding Service

Handles text embedding generation using Voyage AI.
"""

import asyncio
import logging
import hashlib
from typing import Any
from functools import lru_cache

import tiktoken
import voyageai

from ..config import get_settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings."""

    def __init__(self):
        settings = get_settings()
        self._api_key = settings.voyage_api_key
        self._model = settings.voyage_embedding_model
        self._client: voyageai.Client | None = None
        self._tokenizer = None

    def _ensure_client(self) -> voyageai.Client:
        """Initialize Voyage AI client if not already done."""
        if self._client is None:
            if not self._api_key:
                raise ValueError("VOYAGE_API_KEY not configured")
            self._client = voyageai.Client(api_key=self._api_key)
        return self._client

    def _get_tokenizer(self):
        """Get the tokenizer for counting tokens."""
        if self._tokenizer is None:
            self._tokenizer = tiktoken.get_encoding("cl100k_base")
        return self._tokenizer

    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a text."""
        tokenizer = self._get_tokenizer()
        return len(tokenizer.encode(text))

    async def embed_text(self, text: str) -> list[float]:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed

        Returns:
            Embedding vector as list of floats
        """
        client = self._ensure_client()

        # Run blocking call in thread pool
        response = await asyncio.to_thread(
            client.embed,
            texts=[text],
            model=self._model,
        )

        return response.embeddings[0]

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        client = self._ensure_client()

        # Voyage AI free tier has 3 RPM and 10K TPM limits
        # Use small batches (4 chunks ~2K tokens) with 35s delays to stay under both limits
        batch_size = 4
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            # Run blocking call in thread pool
            response = await asyncio.to_thread(
                client.embed,
                texts=batch,
                model=self._model,
            )
            all_embeddings.extend(response.embeddings)
            logger.info(f"Embedded batch {i // batch_size + 1}, count: {len(batch)}")

            # Add delay to stay within rate limits (35s ensures ~2 requests/min under 10K TPM)
            if i + batch_size < len(texts):
                await asyncio.sleep(35)

        return all_embeddings

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Split text into overlapping chunks.

        Args:
            text: The text to chunk
            chunk_size: Target size in tokens
            chunk_overlap: Overlap between chunks in tokens

        Returns:
            List of chunk dicts with 'text', 'start_char', 'end_char'
        """
        tokenizer = self._get_tokenizer()
        tokens = tokenizer.encode(text)

        chunks = []
        start = 0

        while start < len(tokens):
            end = min(start + chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = tokenizer.decode(chunk_tokens)

            # Find character positions
            start_char = len(tokenizer.decode(tokens[:start]))
            end_char = start_char + len(chunk_text)

            chunk_id = hashlib.sha256(chunk_text.encode()).hexdigest()[:12]

            chunks.append(
                {
                    "id": chunk_id,
                    "text": chunk_text,
                    "start_char": start_char,
                    "end_char": end_char,
                    "token_count": len(chunk_tokens),
                }
            )

            # Move start forward, accounting for overlap
            start = end - chunk_overlap
            if start >= len(tokens) - chunk_overlap:
                break

        return chunks


@lru_cache
def get_embedding_service() -> EmbeddingService:
    """Get cached embedding service instance."""
    return EmbeddingService()
