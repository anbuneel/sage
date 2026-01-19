"""
LLM Usage API Router

Endpoints for querying LLM usage statistics and cost tracking.
"""

from fastapi import APIRouter, Query

from app.services.llm_usage_service import get_usage_summary, get_tracker

router = APIRouter(prefix="/usage", tags=["usage"])


@router.get("/summary")
async def get_summary(
    days: int = Query(default=7, ge=1, le=90, description="Number of days to include in summary"),
):
    """
    Get LLM usage summary for the specified period.

    Returns:
        - Total tokens and cost
        - Breakdown by service (rag_service, eligibility_reasoner, fix_finder)
        - Breakdown by request type (chat, reasoning, fix_finding, embedding)
        - Recent requests (last 20)
    """
    summary = await get_usage_summary(days=days)
    return summary


@router.post("/flush")
async def flush_memory():
    """
    Flush any in-memory usage records to the database.

    This is typically called automatically, but can be triggered manually
    if needed for debugging or ensuring persistence.
    """
    tracker = get_tracker()
    count = await tracker.flush_memory()
    return {"flushed": count, "message": f"Flushed {count} records to database"}
