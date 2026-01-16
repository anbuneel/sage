"""
Pinecone Vector Store Service

Handles vector storage and retrieval for RAG chat.
"""

import asyncio
import logging
from typing import Any
from functools import lru_cache

from pinecone import Pinecone, ServerlessSpec

from ..config import get_settings

logger = logging.getLogger(__name__)


class PineconeService:
    """Service for interacting with Pinecone vector database."""

    def __init__(self):
        settings = get_settings()
        self._api_key = settings.pinecone_api_key
        self._index_name = settings.pinecone_index_name
        self._dimension = settings.pinecone_dimension
        self._client: Pinecone | None = None
        self._index = None

    def _ensure_client(self) -> Pinecone:
        """Initialize Pinecone client if not already done."""
        if self._client is None:
            if not self._api_key:
                raise ValueError("PINECONE_API_KEY not configured")
            self._client = Pinecone(api_key=self._api_key)
        return self._client

    def _ensure_index(self):
        """Ensure the index exists and return it."""
        if self._index is None:
            client = self._ensure_client()

            # Check if index exists
            existing_indexes = [idx.name for idx in client.list_indexes()]

            if self._index_name not in existing_indexes:
                # Create the index with serverless spec
                logger.info(f"Creating Pinecone index: {self._index_name}")
                client.create_index(
                    name=self._index_name,
                    dimension=self._dimension,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                )

            self._index = client.Index(self._index_name)

        return self._index

    async def upsert_vectors(
        self,
        vectors: list[dict[str, Any]],
        namespace: str = "guides",
    ) -> dict[str, Any]:
        """
        Upsert vectors to Pinecone.

        Args:
            vectors: List of dicts with 'id', 'values', and optional 'metadata'
            namespace: The namespace to use

        Returns:
            Upsert response from Pinecone
        """
        index = self._ensure_index()

        # Batch upsert in chunks of 100
        batch_size = 100
        results = []

        for i in range(0, len(vectors), batch_size):
            batch = vectors[i : i + batch_size]
            # Run blocking call in thread pool
            result = await asyncio.to_thread(
                index.upsert, vectors=batch, namespace=namespace
            )
            results.append(result)
            logger.info(f"Upserted batch {i // batch_size + 1}, count: {len(batch)}")

        return {"batches": len(results), "total_vectors": len(vectors)}

    async def query(
        self,
        vector: list[float],
        top_k: int = 5,
        namespace: str = "guides",
        filter: dict[str, Any] | None = None,
        include_metadata: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Query Pinecone for similar vectors.

        Args:
            vector: The query vector
            top_k: Number of results to return
            namespace: The namespace to search
            filter: Optional metadata filter
            include_metadata: Whether to include metadata in results

        Returns:
            List of matching documents with scores
        """
        index = self._ensure_index()

        # Run blocking call in thread pool
        response = await asyncio.to_thread(
            index.query,
            vector=vector,
            top_k=top_k,
            namespace=namespace,
            filter=filter,
            include_metadata=include_metadata,
        )

        results = []
        for match in response.matches:
            result = {
                "id": match.id,
                "score": match.score,
            }
            if include_metadata and match.metadata:
                result["metadata"] = match.metadata
            results.append(result)

        return results

    async def delete_namespace(self, namespace: str = "guides") -> None:
        """Delete all vectors in a namespace."""
        index = self._ensure_index()
        # Run blocking call in thread pool
        await asyncio.to_thread(index.delete, delete_all=True, namespace=namespace)
        logger.info(f"Deleted all vectors in namespace: {namespace}")

    def get_stats(self) -> dict[str, Any]:
        """Get index statistics."""
        index = self._ensure_index()
        return index.describe_index_stats()


@lru_cache
def get_pinecone_service() -> PineconeService:
    """Get cached Pinecone service instance."""
    return PineconeService()
