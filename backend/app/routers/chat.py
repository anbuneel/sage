"""
Chat Router

Handles RAG chat endpoints for querying GSE guidelines.
"""

import json
import logging
import uuid
from collections import OrderedDict
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from ..config import get_settings
from ..models import ChatRequest, ChatResponse, ChatMessage, Citation
from ..db import get_session, Conversation, ChatMessage as DBChatMessage
from ..services import get_rag_service

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)

# Maximum message length (characters)
MAX_MESSAGE_LENGTH = 10000

# Maximum conversations to keep in memory (LRU eviction)
MAX_IN_MEMORY_CONVERSATIONS = 1000


class LRUConversationCache(OrderedDict):
    """LRU cache for in-memory conversation storage with max size limit."""

    def __init__(self, max_size: int = MAX_IN_MEMORY_CONVERSATIONS):
        super().__init__()
        self.max_size = max_size

    def __setitem__(self, key, value):
        if key in self:
            self.move_to_end(key)
        super().__setitem__(key, value)
        if len(self) > self.max_size:
            oldest = next(iter(self))
            del self[oldest]

    def __getitem__(self, key):
        self.move_to_end(key)
        return super().__getitem__(key)


# In-memory conversation storage with LRU eviction (fallback when DB not configured)
_conversations: LRUConversationCache = LRUConversationCache()


async def _get_conversation_history(conversation_id: str) -> list[dict[str, str]]:
    """Get conversation history from database or memory."""
    settings = get_settings()

    if settings.database_url:
        # Use database
        async with get_session() as session:
            result = await session.execute(
                select(DBChatMessage)
                .where(DBChatMessage.conversation_id == conversation_id)
                .order_by(DBChatMessage.created_at)
            )
            messages = result.scalars().all()
            return [{"role": msg.role, "content": msg.content} for msg in messages]
    else:
        # Use in-memory fallback
        if conversation_id in _conversations:
            return [{"role": msg.role, "content": msg.content} for msg in _conversations[conversation_id]]
        return []


async def _save_messages(
    conversation_id: str,
    user_message: ChatMessage,
    assistant_message: ChatMessage,
) -> None:
    """Save messages to database or memory."""
    settings = get_settings()

    if settings.database_url:
        # Use database
        async with get_session() as session:
            # Check if conversation exists
            result = await session.execute(
                select(Conversation).where(Conversation.id == conversation_id)
            )
            conversation = result.scalar_one_or_none()

            if not conversation:
                # Create new conversation
                conversation = Conversation(id=conversation_id)
                session.add(conversation)

            # Add messages
            user_db_msg = DBChatMessage(
                conversation_id=conversation_id,
                role=user_message.role,
                content=user_message.content,
            )
            session.add(user_db_msg)

            # Serialize citations
            citations_json = None
            if assistant_message.citations:
                citations_json = json.dumps([c.model_dump() for c in assistant_message.citations])

            assistant_db_msg = DBChatMessage(
                conversation_id=conversation_id,
                role=assistant_message.role,
                content=assistant_message.content,
                citations=citations_json,
            )
            session.add(assistant_db_msg)
    else:
        # Use in-memory fallback
        if conversation_id not in _conversations:
            _conversations[conversation_id] = []
        _conversations[conversation_id].append(user_message)
        _conversations[conversation_id].append(assistant_message)


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a chat message",
    description="Send a message and receive a response with citations from GSE guidelines.",
)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a chat message and return a response with citations.

    This endpoint uses RAG (Retrieval Augmented Generation) to:
    1. Search relevant sections of Fannie Mae and Freddie Mac guides
    2. Generate a response using Claude with the retrieved context
    3. Include citations to the source documents
    """
    # Input validation
    if len(request.message) > MAX_MESSAGE_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Message too long. Maximum length is {MAX_MESSAGE_LENGTH} characters.",
        )

    if not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty.",
        )

    # Get or create conversation ID
    conversation_id = request.conversation_id or str(uuid.uuid4())

    try:
        # Check if RAG is enabled and configured
        settings = get_settings()

        if settings.enable_rag_chat and settings.anthropic_api_key and settings.pinecone_api_key:
            # Use real RAG implementation
            return await _process_rag_chat(request, conversation_id)
        else:
            # Fall back to mock responses
            logger.info("RAG not configured, using mock responses")
            return await _process_mock_chat(request, conversation_id)

    except ValueError as e:
        # Configuration errors
        logger.warning(f"RAG configuration error: {e}, falling back to mock")
        return await _process_mock_chat(request, conversation_id)
    except Exception as e:
        # Log full error but return generic message to client
        logger.exception("Error processing chat message")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred processing your message. Please try again.",
        )


async def _process_rag_chat(request: ChatRequest, conversation_id: str) -> ChatResponse:
    """Process chat using real RAG pipeline."""
    rag_service = get_rag_service()

    # Get conversation history
    history = await _get_conversation_history(conversation_id)

    # Detect if user is asking about a specific GSE
    gse_filter = None
    message_lower = request.message.lower()
    if "fannie" in message_lower or "homeready" in message_lower:
        gse_filter = "fannie_mae"
    elif "freddie" in message_lower or "home possible" in message_lower:
        gse_filter = "freddie_mac"

    # Generate response using RAG
    response_content, citations = await rag_service.chat(
        query=request.message,
        conversation_history=history,
        gse_filter=gse_filter,
    )

    # Create user message
    user_message = ChatMessage(role="user", content=request.message)

    # Create assistant message
    assistant_message = ChatMessage(
        role="assistant",
        content=response_content,
        citations=citations,
    )

    # Save messages
    await _save_messages(conversation_id, user_message, assistant_message)

    return ChatResponse(
        message=assistant_message,
        conversation_id=conversation_id,
    )


async def _process_mock_chat(request: ChatRequest, conversation_id: str) -> ChatResponse:
    """Process chat using mock responses (fallback)."""
    # Store user message
    user_message = ChatMessage(role="user", content=request.message)

    # Generate mock response based on common questions
    response_content, citations = _generate_mock_response(request.message)

    # Create assistant message
    assistant_message = ChatMessage(
        role="assistant",
        content=response_content,
        citations=citations,
    )

    # Save messages
    await _save_messages(conversation_id, user_message, assistant_message)

    return ChatResponse(
        message=assistant_message,
        conversation_id=conversation_id,
    )


def _generate_mock_response(message: str) -> tuple[str, list[Citation]]:
    """
    Generate a mock response based on the user's message.

    This is a fallback when RAG is not configured.
    """
    message_lower = message.lower()

    # HomeReady questions
    if "homeready" in message_lower or "home ready" in message_lower:
        return (
            "HomeReady is Fannie Mae's affordable lending product designed for "
            "low-to-moderate income borrowers. Key features include:\n\n"
            "- Minimum credit score: 620\n"
            "- Maximum LTV: 97% for 1-unit primary residence\n"
            "- Maximum DTI: 50%\n"
            "- Income limit: 80% of Area Median Income (AMI)\n"
            "- Reduced MI coverage requirements\n\n"
            "Homeownership education is required if all borrowers are first-time homebuyers.",
            [
                Citation(
                    text="The HomeReady mortgage is designed to help lenders serve "
                    "creditworthy low-income borrowers",
                    source="Fannie Mae Selling Guide B5-6-01",
                    url="https://selling-guide.fanniemae.com/Selling-Guide/Origination-thru-Closing/Subpart-B5-Unique-Eligibility-Underwriting-Considerations/Chapter-B5-6-HomeReady-Mortgage/1032996841/B5-6-01-HomeReady-Mortgage-Loan-and-Borrower-Eligibility-05-01-2024.htm",
                ),
                Citation(
                    text="Minimum representative credit score of 620",
                    source="Fannie Mae Selling Guide B5-6-02",
                    url="https://selling-guide.fanniemae.com/Selling-Guide/Origination-thru-Closing/Subpart-B5-Unique-Eligibility-Underwriting-Considerations/Chapter-B5-6-HomeReady-Mortgage/",
                ),
            ],
        )

    # Home Possible questions
    if "home possible" in message_lower or "homepossible" in message_lower:
        return (
            "Home Possible is Freddie Mac's affordable lending product for "
            "low-to-moderate income borrowers. Key features include:\n\n"
            "- Minimum credit score: 660\n"
            "- Maximum LTV: 97%\n"
            "- Maximum DTI: 45% (43% for Loan Product Advisor)\n"
            "- Income limit: 80% of Area Median Income (AMI)\n"
            "- Flexible sources of funds for down payment\n\n"
            "Homeownership education is required for first-time homebuyers.",
            [
                Citation(
                    text="Home Possible mortgages offer low down payments for "
                    "low-to-moderate income borrowers",
                    source="Freddie Mac Single-Family Seller/Servicer Guide 4501.5",
                    url="https://guide.freddiemac.com/app/guide/section/4501.5",
                ),
            ],
        )

    # Credit score questions
    if "credit score" in message_lower or "credit" in message_lower:
        return (
            "Credit score requirements differ between the two affordable lending products:\n\n"
            "**HomeReady (Fannie Mae):**\n"
            "- Minimum credit score: 620\n\n"
            "**Home Possible (Freddie Mac):**\n"
            "- Minimum credit score: 660\n\n"
            "Both products use the middle credit score when multiple scores are available. "
            "Higher credit scores may qualify for better pricing adjustments.",
            [
                Citation(
                    text="Minimum representative credit score of 620 for HomeReady",
                    source="Fannie Mae Selling Guide B5-6-02",
                    url=None,
                ),
                Citation(
                    text="Minimum indicator score of 660 for Home Possible",
                    source="Freddie Mac Guide 4501.5",
                    url=None,
                ),
            ],
        )

    # DTI questions
    if "dti" in message_lower or "debt-to-income" in message_lower or "debt to income" in message_lower:
        return (
            "Debt-to-Income (DTI) ratio limits for affordable lending products:\n\n"
            "**HomeReady (Fannie Mae):**\n"
            "- Maximum DTI: 50%\n"
            "- Desktop Underwriter (DU) may approve higher DTI with compensating factors\n\n"
            "**Home Possible (Freddie Mac):**\n"
            "- Maximum DTI: 45%\n"
            "- Loan Product Advisor (LPA): 43%\n\n"
            "DTI is calculated as total monthly debt obligations divided by gross monthly income.",
            [
                Citation(
                    text="Maximum DTI ratio of 50% for HomeReady",
                    source="Fannie Mae Selling Guide B5-6-02",
                    url=None,
                ),
                Citation(
                    text="Maximum DTI ratio of 45% for Home Possible",
                    source="Freddie Mac Guide 4501.5",
                    url=None,
                ),
            ],
        )

    # LTV questions
    if "ltv" in message_lower or "loan-to-value" in message_lower or "loan to value" in message_lower:
        return (
            "Loan-to-Value (LTV) limits for affordable lending products:\n\n"
            "**HomeReady (Fannie Mae):**\n"
            "- Maximum LTV: 97% for 1-unit primary residence\n"
            "- Lower LTV limits may apply for 2-4 unit properties\n\n"
            "**Home Possible (Freddie Mac):**\n"
            "- Maximum LTV: 97%\n\n"
            "Both products require private mortgage insurance (MI) for LTV > 80%, "
            "though coverage requirements may be reduced.",
            [
                Citation(
                    text="Maximum LTV of 97% for HomeReady 1-unit primary residence",
                    source="Fannie Mae Selling Guide B5-6-01",
                    url=None,
                ),
                Citation(
                    text="Maximum LTV of 97% for Home Possible",
                    source="Freddie Mac Guide 4501.5",
                    url=None,
                ),
            ],
        )

    # Default response
    return (
        "I can help you understand the eligibility requirements for HomeReady "
        "(Fannie Mae) and Home Possible (Freddie Mac) affordable lending products. "
        "You can ask me about:\n\n"
        "- Credit score requirements\n"
        "- DTI (debt-to-income) limits\n"
        "- LTV (loan-to-value) limits\n"
        "- Income limits and AMI requirements\n"
        "- Property eligibility\n"
        "- Homeownership education requirements\n\n"
        "What would you like to know?",
        [],
    )
