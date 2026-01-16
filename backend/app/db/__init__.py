"""
SAGE Database Module

PostgreSQL database connections and models.
"""

from .connection import get_db_client
from .database import get_db, get_session, init_db, close_db
from .models import (
    Base,
    PolicyUpdate,
    EligibilityRule,
    GuideSection,
    Conversation,
    ChatMessage,
    ScraperRun,
)

__all__ = [
    "get_db_client",
    "get_db",
    "get_session",
    "init_db",
    "close_db",
    "Base",
    "PolicyUpdate",
    "EligibilityRule",
    "GuideSection",
    "Conversation",
    "ChatMessage",
    "ScraperRun",
]
