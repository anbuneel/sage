"""
SAGE API Routers

All FastAPI routers for the application.
"""

from .eligibility import router as eligibility_router
from .chat import router as chat_router
from .changes import router as changes_router

__all__ = [
    "eligibility_router",
    "chat_router",
    "changes_router",
]
