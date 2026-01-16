"""
RAG (Retrieval Augmented Generation) Service

Combines Pinecone retrieval with Claude generation for chat responses.
"""

import logging
from typing import Any
from functools import lru_cache

import anthropic

from ..config import get_settings
from ..models import Citation
from .pinecone_service import get_pinecone_service
from .embedding_service import get_embedding_service

logger = logging.getLogger(__name__)


class RAGService:
    """Service for RAG-based question answering."""

    def __init__(self):
        settings = get_settings()
        self._api_key = settings.anthropic_api_key
        self._model = settings.anthropic_model
        self._client: anthropic.Anthropic | None = None
        self._pinecone = get_pinecone_service()
        self._embedding = get_embedding_service()

    def _ensure_client(self) -> anthropic.Anthropic:
        """Initialize Anthropic client if not already done."""
        if self._client is None:
            if not self._api_key:
                raise ValueError("ANTHROPIC_API_KEY not configured")
            self._client = anthropic.Anthropic(api_key=self._api_key)
        return self._client

    async def retrieve_context(
        self,
        query: str,
        top_k: int = 5,
        gse_filter: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve relevant context chunks for a query.

        Args:
            query: The user's question
            top_k: Number of chunks to retrieve
            gse_filter: Optional filter for 'fannie_mae' or 'freddie_mac'

        Returns:
            List of relevant context chunks with metadata
        """
        # Generate query embedding
        query_vector = await self._embedding.embed_text(query)

        # Build filter if GSE specified
        metadata_filter = None
        if gse_filter:
            metadata_filter = {"gse": {"$eq": gse_filter}}

        # Query Pinecone
        results = await self._pinecone.query(
            vector=query_vector,
            top_k=top_k,
            filter=metadata_filter,
        )

        return results

    async def generate_response(
        self,
        query: str,
        context_chunks: list[dict[str, Any]],
        conversation_history: list[dict[str, str]] | None = None,
    ) -> tuple[str, list[Citation]]:
        """
        Generate a response using Claude with retrieved context.

        Args:
            query: The user's question
            context_chunks: Retrieved context from Pinecone
            conversation_history: Optional previous messages

        Returns:
            Tuple of (response_text, citations)
        """
        client = self._ensure_client()

        # Build context string from chunks
        context_parts = []
        source_map = {}

        for i, chunk in enumerate(context_chunks):
            metadata = chunk.get("metadata", {})
            source = metadata.get("source", f"Document {i + 1}")
            section = metadata.get("section", "")
            gse = metadata.get("gse", "")
            text = metadata.get("text", "")

            source_key = f"{gse}:{section}" if section else source
            source_map[i] = {
                "source": source,
                "section": section,
                "gse": gse,
                "url": metadata.get("url"),
            }

            context_parts.append(f"[{i + 1}] Source: {source}\nSection: {section}\n{text}\n")

        context_str = "\n---\n".join(context_parts)

        # Build system prompt
        system_prompt = """You are SAGE, a mortgage policy expert assistant that helps users understand Fannie Mae and Freddie Mac guidelines, particularly for HomeReady and Home Possible affordable lending products.

Your responses should be:
1. Accurate and based on the provided context
2. Clear and professional
3. Include specific citations to the source documents using [1], [2], etc.

When comparing products, highlight key differences in eligibility requirements, income limits, DTI ratios, and LTV limits.

If the context doesn't contain enough information to fully answer the question, acknowledge what you know from the context and indicate what additional information might be helpful.

Always cite your sources using the bracketed numbers that correspond to the context sections provided."""

        # Build messages
        messages = []

        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history[-6:]:  # Last 3 exchanges
                messages.append({"role": msg["role"], "content": msg["content"]})

        # Add current query with context
        user_message = f"""Based on the following context from mortgage guidelines, please answer my question.

CONTEXT:
{context_str}

QUESTION: {query}

Please provide a clear, accurate answer with citations to the relevant source sections."""

        messages.append({"role": "user", "content": user_message})

        # Generate response
        response = client.messages.create(
            model=self._model,
            max_tokens=2048,
            system=system_prompt,
            messages=messages,
        )

        response_text = response.content[0].text

        # Extract citations from response
        citations = self._extract_citations(response_text, source_map, context_chunks)

        return response_text, citations

    def _extract_citations(
        self,
        response_text: str,
        source_map: dict[int, dict[str, Any]],
        context_chunks: list[dict[str, Any]],
    ) -> list[Citation]:
        """Extract citations from the response text."""
        import re

        citations = []
        seen_sources = set()

        # Find all citation references like [1], [2], etc.
        citation_refs = re.findall(r"\[(\d+)\]", response_text)

        for ref in citation_refs:
            idx = int(ref) - 1  # Convert to 0-based index
            if idx in source_map and source_map[idx]["source"] not in seen_sources:
                source_info = source_map[idx]
                chunk_metadata = context_chunks[idx].get("metadata", {})

                citation = Citation(
                    text=chunk_metadata.get("text", "")[:200],
                    source=f"{source_info['gse'].replace('_', ' ').title()} - {source_info['section']}",
                    url=source_info.get("url"),
                )
                citations.append(citation)
                seen_sources.add(source_info["source"])

        return citations

    async def chat(
        self,
        query: str,
        conversation_history: list[dict[str, str]] | None = None,
        gse_filter: str | None = None,
    ) -> tuple[str, list[Citation]]:
        """
        Main chat method that retrieves context and generates a response.

        Args:
            query: The user's question
            conversation_history: Optional previous messages
            gse_filter: Optional GSE filter

        Returns:
            Tuple of (response_text, citations)
        """
        # Retrieve relevant context
        context_chunks = await self.retrieve_context(
            query=query,
            top_k=5,
            gse_filter=gse_filter,
        )

        if not context_chunks:
            # No context found, provide a helpful response
            return (
                "I couldn't find specific information about that in the mortgage guidelines. "
                "Could you rephrase your question or ask about HomeReady (Fannie Mae) or "
                "Home Possible (Freddie Mac) eligibility requirements?",
                [],
            )

        # Generate response with context
        response, citations = await self.generate_response(
            query=query,
            context_chunks=context_chunks,
            conversation_history=conversation_history,
        )

        return response, citations


@lru_cache
def get_rag_service() -> RAGService:
    """Get cached RAG service instance."""
    return RAGService()
