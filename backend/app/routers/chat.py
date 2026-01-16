"""
Chat Router

Handles RAG chat endpoints for querying GSE guidelines.
"""

import uuid
from fastapi import APIRouter, HTTPException, status

from ..models import ChatRequest, ChatResponse, ChatMessage, Citation

router = APIRouter(prefix="/chat", tags=["chat"])


# In-memory conversation storage (placeholder)
# TODO: Replace with database storage in Phase 2
_conversations: dict[str, list[ChatMessage]] = {}


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

    This endpoint will use RAG (Retrieval Augmented Generation) to:
    1. Search relevant sections of Fannie Mae and Freddie Mac guides
    2. Generate a response using Claude with the retrieved context
    3. Include citations to the source documents

    Currently returns mock data. Full RAG implementation in Phase 2.
    """
    try:
        # Get or create conversation
        conversation_id = request.conversation_id or str(uuid.uuid4())

        if conversation_id not in _conversations:
            _conversations[conversation_id] = []

        # Store user message
        user_message = ChatMessage(role="user", content=request.message)
        _conversations[conversation_id].append(user_message)

        # Generate mock response based on common questions
        # TODO: Replace with actual RAG implementation in Phase 2
        response_content, citations = _generate_mock_response(request.message)

        # Create assistant message
        assistant_message = ChatMessage(
            role="assistant",
            content=response_content,
            citations=citations,
        )

        # Store assistant message
        _conversations[conversation_id].append(assistant_message)

        return ChatResponse(
            message=assistant_message,
            conversation_id=conversation_id,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat message: {str(e)}",
        )


def _generate_mock_response(message: str) -> tuple[str, list[Citation]]:
    """
    Generate a mock response based on the user's message.

    This is a placeholder until RAG is implemented.
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
