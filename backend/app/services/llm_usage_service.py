"""
LLM Usage Tracking Service

Centralized service for tracking all LLM API usage across the application.
Supports both synchronous recording and async database persistence.
"""

import logging
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.db.models import LLMUsage

logger = logging.getLogger(__name__)

# Pricing per 1 million tokens (as of January 2026)
MODEL_PRICING = {
    # Anthropic Claude models
    "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
    "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
    "claude-3-sonnet-20240229": {"input": 3.00, "output": 15.00},
    # Voyage AI embeddings (per 1M tokens)
    "voyage-2": {"input": 0.10, "output": 0.0},  # Embeddings only have input cost
    "voyage-large-2": {"input": 0.12, "output": 0.0},
}


def calculate_cost(
    model_name: str, tokens_input: int, tokens_output: int
) -> float:
    """Calculate the cost in USD for a given model and token usage."""
    pricing = MODEL_PRICING.get(model_name)
    if not pricing:
        # Default to Claude Sonnet pricing if model not found
        pricing = MODEL_PRICING["claude-sonnet-4-20250514"]
        logger.warning(f"Unknown model '{model_name}', using default Claude Sonnet pricing")

    input_cost = (tokens_input / 1_000_000) * pricing["input"]
    output_cost = (tokens_output / 1_000_000) * pricing["output"]
    return round(input_cost + output_cost, 6)


@dataclass
class UsageRecord:
    """Represents a single LLM usage record."""

    service_name: str
    model_name: str
    model_provider: str
    request_type: str
    tokens_input: int = 0
    tokens_output: int = 0
    duration_ms: int = 0
    success: bool = True
    error_message: Optional[str] = None

    @property
    def tokens_total(self) -> int:
        return self.tokens_input + self.tokens_output

    @property
    def cost_usd(self) -> float:
        return calculate_cost(self.model_name, self.tokens_input, self.tokens_output)


class LLMUsageTracker:
    """
    Tracks LLM usage and persists to database.

    Usage:
        tracker = LLMUsageTracker()

        # Option 1: Manual recording
        record = UsageRecord(
            service_name="fix_finder",
            model_name="claude-sonnet-4-20250514",
            model_provider="anthropic",
            request_type="fix_finding",
            tokens_input=5000,
            tokens_output=1500,
            duration_ms=2500
        )
        await tracker.record(record)

        # Option 2: Context manager with timing
        async with tracker.track("rag_service", "claude-sonnet-4-20250514", "anthropic", "chat") as ctx:
            # Do LLM call
            result = await call_llm()
            ctx.tokens_input = result.usage.input_tokens
            ctx.tokens_output = result.usage.output_tokens
    """

    def __init__(self):
        self._in_memory_records: list[UsageRecord] = []

    async def record(self, usage: UsageRecord) -> None:
        """Record a usage entry to the database."""
        try:
            async with get_session() as session:
                db_record = LLMUsage(
                    service_name=usage.service_name,
                    model_name=usage.model_name,
                    model_provider=usage.model_provider,
                    request_type=usage.request_type,
                    tokens_input=usage.tokens_input,
                    tokens_output=usage.tokens_output,
                    tokens_total=usage.tokens_total,
                    cost_usd=usage.cost_usd,
                    duration_ms=usage.duration_ms,
                    success=usage.success,
                    error_message=usage.error_message,
                )
                session.add(db_record)
                await session.commit()
                logger.debug(
                    f"Recorded LLM usage: {usage.service_name}/{usage.request_type} "
                    f"- {usage.tokens_total} tokens, ${usage.cost_usd:.6f}"
                )
        except Exception as e:
            logger.warning(f"Failed to record LLM usage to database: {e}")
            # Store in memory as fallback
            self._in_memory_records.append(usage)

    def record_sync(self, usage: UsageRecord) -> None:
        """
        Synchronously record a usage entry (stores in memory).
        Use flush_memory() to persist to database.
        """
        self._in_memory_records.append(usage)
        logger.debug(
            f"Stored LLM usage in memory: {usage.service_name}/{usage.request_type} "
            f"- {usage.tokens_total} tokens, ${usage.cost_usd:.6f}"
        )

    async def flush_memory(self) -> int:
        """Flush in-memory records to database. Returns count of records flushed."""
        if not self._in_memory_records:
            return 0

        count = 0
        try:
            async with get_session() as session:
                for usage in self._in_memory_records:
                    db_record = LLMUsage(
                        service_name=usage.service_name,
                        model_name=usage.model_name,
                        model_provider=usage.model_provider,
                        request_type=usage.request_type,
                        tokens_input=usage.tokens_input,
                        tokens_output=usage.tokens_output,
                        tokens_total=usage.tokens_total,
                        cost_usd=usage.cost_usd,
                        duration_ms=usage.duration_ms,
                        success=usage.success,
                        error_message=usage.error_message,
                    )
                    session.add(db_record)
                    count += 1
                await session.commit()
            self._in_memory_records.clear()
            logger.info(f"Flushed {count} LLM usage records to database")
        except Exception as e:
            logger.error(f"Failed to flush LLM usage records: {e}")
        return count

    @asynccontextmanager
    async def track(
        self,
        service_name: str,
        model_name: str,
        model_provider: str,
        request_type: str,
    ):
        """
        Context manager for tracking LLM usage with automatic timing.

        Usage:
            async with tracker.track("rag_service", "claude-sonnet-4-20250514", "anthropic", "chat") as ctx:
                result = await call_llm()
                ctx.tokens_input = result.usage.input_tokens
                ctx.tokens_output = result.usage.output_tokens
        """
        ctx = UsageRecord(
            service_name=service_name,
            model_name=model_name,
            model_provider=model_provider,
            request_type=request_type,
        )
        start_time = time.time()
        try:
            yield ctx
        except Exception as e:
            ctx.success = False
            ctx.error_message = str(e)
            raise
        finally:
            ctx.duration_ms = int((time.time() - start_time) * 1000)
            await self.record(ctx)


# Global tracker instance
_tracker: Optional[LLMUsageTracker] = None


def get_tracker() -> LLMUsageTracker:
    """Get the global tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = LLMUsageTracker()
    return _tracker


# Convenience functions for quick recording
async def record_usage(
    service_name: str,
    model_name: str,
    model_provider: str,
    request_type: str,
    tokens_input: int = 0,
    tokens_output: int = 0,
    duration_ms: int = 0,
    success: bool = True,
    error_message: Optional[str] = None,
) -> None:
    """Quick helper to record LLM usage."""
    tracker = get_tracker()
    await tracker.record(
        UsageRecord(
            service_name=service_name,
            model_name=model_name,
            model_provider=model_provider,
            request_type=request_type,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            duration_ms=duration_ms,
            success=success,
            error_message=error_message,
        )
    )


# Query functions for analytics
async def get_usage_summary(
    days: int = 7,
    session: Optional[AsyncSession] = None,
) -> dict[str, Any]:
    """Get usage summary for the past N days."""
    cutoff = datetime.utcnow() - timedelta(days=days)

    async def _query(s: AsyncSession) -> dict[str, Any]:
        # Total tokens and cost
        totals_query = select(
            func.sum(LLMUsage.tokens_input).label("total_input"),
            func.sum(LLMUsage.tokens_output).label("total_output"),
            func.sum(LLMUsage.tokens_total).label("total_tokens"),
            func.sum(LLMUsage.cost_usd).label("total_cost"),
            func.count(LLMUsage.id).label("total_requests"),
            func.avg(LLMUsage.duration_ms).label("avg_duration_ms"),
        ).where(LLMUsage.created_at >= cutoff)

        totals_result = await s.execute(totals_query)
        totals = totals_result.first()

        # By service
        by_service_query = (
            select(
                LLMUsage.service_name,
                func.sum(LLMUsage.tokens_total).label("tokens"),
                func.sum(LLMUsage.cost_usd).label("cost"),
                func.count(LLMUsage.id).label("requests"),
            )
            .where(LLMUsage.created_at >= cutoff)
            .group_by(LLMUsage.service_name)
        )
        by_service_result = await s.execute(by_service_query)
        by_service = [
            {
                "service": row.service_name,
                "tokens": row.tokens or 0,
                "cost": round(row.cost or 0, 6),
                "requests": row.requests,
            }
            for row in by_service_result
        ]

        # By request type
        by_type_query = (
            select(
                LLMUsage.request_type,
                func.sum(LLMUsage.tokens_total).label("tokens"),
                func.sum(LLMUsage.cost_usd).label("cost"),
                func.count(LLMUsage.id).label("requests"),
            )
            .where(LLMUsage.created_at >= cutoff)
            .group_by(LLMUsage.request_type)
        )
        by_type_result = await s.execute(by_type_query)
        by_type = [
            {
                "request_type": row.request_type,
                "tokens": row.tokens or 0,
                "cost": round(row.cost or 0, 6),
                "requests": row.requests,
            }
            for row in by_type_result
        ]

        # Recent requests (last 20)
        recent_query = (
            select(LLMUsage)
            .order_by(LLMUsage.created_at.desc())
            .limit(20)
        )
        recent_result = await s.execute(recent_query)
        recent = [
            {
                "id": str(row.id),
                "service": row.service_name,
                "request_type": row.request_type,
                "model": row.model_name,
                "tokens_input": row.tokens_input,
                "tokens_output": row.tokens_output,
                "cost": round(row.cost_usd, 6),
                "duration_ms": row.duration_ms,
                "success": row.success,
                "created_at": row.created_at.isoformat(),
            }
            for row in recent_result.scalars()
        ]

        return {
            "period_days": days,
            "totals": {
                "tokens_input": totals.total_input or 0,
                "tokens_output": totals.total_output or 0,
                "tokens_total": totals.total_tokens or 0,
                "cost_usd": round(totals.total_cost or 0, 6),
                "requests": totals.total_requests or 0,
                "avg_duration_ms": round(totals.avg_duration_ms or 0, 0),
            },
            "by_service": by_service,
            "by_request_type": by_type,
            "recent_requests": recent,
        }

    if session:
        return await _query(session)
    else:
        async with get_session() as s:
            return await _query(s)
