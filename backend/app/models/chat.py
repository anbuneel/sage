"""
Chat Models

Models for the RAG chat interface.
"""

from pydantic import BaseModel, Field


class Citation(BaseModel):
    """A citation from the GSE guides."""

    text: str = Field(..., description="Quoted text from the source")
    source: str = Field(..., description="Source reference (e.g., 'Fannie Mae Selling Guide B5-6-01')")
    url: str | None = Field(default=None, description="URL to the source if available")


class ChatMessage(BaseModel):
    """A single chat message."""

    role: str = Field(..., pattern="^(user|assistant)$", description="Message role")
    content: str = Field(..., description="Message content")
    citations: list[Citation] | None = Field(
        default=None, description="Citations for assistant messages"
    )


class ChatRequest(BaseModel):
    """Request to the chat endpoint."""

    message: str = Field(..., min_length=1, description="User's message")
    conversation_id: str | None = Field(
        default=None, description="Conversation ID for history tracking"
    )


class ChatResponse(BaseModel):
    """Response from the chat endpoint."""

    message: ChatMessage = Field(..., description="Assistant's response message")
    conversation_id: str = Field(..., description="Conversation ID for future messages")
