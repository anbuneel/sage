"""
SAGE Backend - Main Application

FastAPI application entry point for the SAGE (Smart Affordable-lending Guide Engine) API.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import eligibility_router, chat_router, changes_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan handler.

    Handles startup and shutdown events.
    """
    # Startup
    settings = get_settings()
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Debug mode: {settings.debug}")

    yield

    # Shutdown
    print(f"Shutting down {settings.app_name}")


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
