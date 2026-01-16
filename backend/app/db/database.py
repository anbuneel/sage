"""
Database Connection

PostgreSQL database connection using SQLAlchemy async.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..config import get_settings
from .models import Base

logger = logging.getLogger(__name__)

# Global engine and session factory
_engine = None
_session_factory = None


def get_database_url() -> str:
    """
    Get the database URL, converting postgres:// to postgresql+asyncpg://.
    """
    settings = get_settings()
    url = settings.database_url

    if not url:
        # Default to SQLite for development
        return "sqlite+aiosqlite:///./sage.db"

    # Convert postgres:// to postgresql+asyncpg:// for async support
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    return url


def get_engine():
    """Get or create the database engine."""
    global _engine

    if _engine is None:
        database_url = get_database_url()
        logger.info(f"Creating database engine for: {database_url.split('@')[-1] if '@' in database_url else database_url}")

        _engine = create_async_engine(
            database_url,
            echo=get_settings().debug,
            pool_pre_ping=True,
        )

    return _engine


def get_session_factory():
    """Get or create the session factory."""
    global _session_factory

    if _session_factory is None:
        engine = get_engine()
        _session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    return _session_factory


async def init_db() -> None:
    """Initialize the database, creating all tables."""
    engine = get_engine()

    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database initialized successfully")


async def close_db() -> None:
    """Close database connections."""
    global _engine, _session_factory

    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("Database connections closed")


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a database session as a context manager.

    Usage:
        async with get_session() as session:
            result = await session.execute(query)
    """
    factory = get_session_factory()
    session = factory()

    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI to get a database session.

    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with get_session() as session:
        yield session
