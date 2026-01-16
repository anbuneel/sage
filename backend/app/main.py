"""
SAGE Backend - Main Application

FastAPI application entry point for the SAGE (Smart Affordable-lending Guide Engine) API.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import eligibility_router, chat_router, changes_router
from .db import init_db, close_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan handler.

    Handles startup and shutdown events including database initialization.
    """
    # Startup
    settings = get_settings()
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")

    # Initialize database if configured
    if settings.database_url:
        logger.info("Initializing database connection...")
        try:
            await init_db()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            logger.warning("Continuing without database - using mock data")
    else:
        logger.info("No database URL configured - using mock data")

    # Log RAG configuration status
    if settings.anthropic_api_key and settings.pinecone_api_key:
        logger.info("RAG chat enabled (Anthropic + Pinecone configured)")
    else:
        logger.info("RAG chat disabled - using mock responses")

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")

    # Close database connections
    if settings.database_url:
        await close_db()
        logger.info("Database connections closed")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured application instance
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description=(
            "SAGE (Smart Affordable-lending Guide Engine) API. "
            "Provides eligibility checking, RAG-based Q&A, and policy change tracking "
            "for Fannie Mae HomeReady and Freddie Mac Home Possible loan products."
        ),
        version=settings.app_version,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(eligibility_router, prefix="/api")
    app.include_router(chat_router, prefix="/api")
    app.include_router(changes_router, prefix="/api")

    # Health check endpoint
    @app.get(
        "/api/health",
        tags=["health"],
        summary="Health check",
        description="Check if the API is running.",
    )
    async def health_check() -> dict[str, str]:
        """Return health status and version."""
        return {
            "status": "ok",
            "version": settings.app_version,
        }

    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
