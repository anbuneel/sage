"""
SAGE Backend Configuration

Uses pydantic-settings for environment variable management.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "SAGE"
    app_version: str = "0.1.0"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS
    cors_origins: list[str] = [
        "http://localhost:4000",
        "http://127.0.0.1:4000",
    ]

    # Database (Supabase)
    database_url: str = ""
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_key: str = ""

    # Vector Store (Pinecone)
    pinecone_api_key: str = ""
    pinecone_index_name: str = "sage-guides"
    pinecone_dimension: int = 1024  # voyage-2 dimension

    # AI (Anthropic)
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    # Embeddings (Voyage AI)
    voyage_api_key: str = ""
    voyage_embedding_model: str = "voyage-2"

    # Feature Flags
    enable_rag_chat: bool = True
    enable_change_detection: bool = True
    enable_rag_eligibility: bool = True  # Use RAG-powered eligibility reasoner

    # Scraping settings
    scrape_interval_hours: int = 24  # How often to check for updates

    # RAG Eligibility settings
    rag_eligibility_timeout: int = 30  # Max seconds for RAG eligibility analysis

    # Fix Finder Agent settings
    enable_fix_finder: bool = True  # Feature flag for Fix Finder Agent
    fix_finder_max_iterations: int = 3  # Max ReAct loop iterations
    fix_finder_timeout: int = 15  # Max seconds for Fix Finder analysis


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Using lru_cache ensures settings are only loaded once.
    """
    return Settings()
