"""
Database Models

SQLAlchemy models for PostgreSQL database.
"""

from datetime import date, datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class PolicyUpdate(Base):
    """Tracks policy updates from Fannie Mae and Freddie Mac."""

    __tablename__ = "policy_updates"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    gse: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # fannie_mae or freddie_mac
    update_type: Mapped[str] = mapped_column(String(50), nullable=False)  # lender_letter, bulletin, guide_update
    update_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    publish_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    effective_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    full_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    affected_sections: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    affected_rule_ids: Mapped[list[str]] = mapped_column(ARRAY(UUID(as_uuid=False)), default=list)
    impact_analysis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    code_update: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class EligibilityRule(Base):
    """Stores eligibility rules extracted from guides."""

    __tablename__ = "eligibility_rules"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    gse: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    product: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # homeready, home_possible
    rule_category: Mapped[str] = mapped_column(String(100), nullable=False)  # credit, dti, ltv, income, property
    rule_name: Mapped[str] = mapped_column(String(200), nullable=False)
    rule_value: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string for complex rules
    description: Mapped[str] = mapped_column(Text, nullable=False)
    source_section: Mapped[str] = mapped_column(String(100), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    effective_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class GuideSection(Base):
    """Stores indexed sections of GSE guides for search."""

    __tablename__ = "guide_sections"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    gse: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    section_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source_file: Mapped[str] = mapped_column(String(500), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    last_scraped: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    content_hash: Mapped[str] = mapped_column(String(64), nullable=True)  # For change detection
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class Conversation(Base):
    """Stores chat conversations for history."""

    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage", back_populates="conversation", cascade="all, delete-orphan"
    )


class ChatMessage(Base):
    """Stores individual chat messages."""

    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    conversation_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user, assistant
    content: Mapped[str] = mapped_column(Text, nullable=False)
    citations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array of citations
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")


class ScraperRun(Base):
    """Tracks scraper execution history."""

    __tablename__ = "scraper_runs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    scraper_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    gse: Mapped[str] = mapped_column(String(20), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="running")  # running, completed, failed
    items_found: Mapped[int] = mapped_column(Integer, default=0)
    items_new: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
