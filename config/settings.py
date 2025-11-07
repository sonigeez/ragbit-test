"""
Configuration settings for the Transcript Chatbot application.
Supports environment-based configuration for production deployment.
"""
import os
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application Settings
    app_name: str = "Transcript Chatbot"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False

    # LLM Provider Settings
    llm_provider: Literal["openai", "openrouter"] = "openai"

    # LLM Settings
    llm_model_name: str = "gpt-4o-mini"  # For OpenRouter: "openrouter/anthropic/claude-3.5-sonnet"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2000
    use_structured_output: bool = True

    # Embedding Provider Settings
    embedding_provider: Literal["openai", "openrouter"] = "openai"

    # Embedding Settings
    embedding_model_name: str = "text-embedding-3-small"  # For OpenRouter: "openrouter/..." (if available)
    embedding_dimensions: int = 1536

    # Vector Store Settings
    vector_store_type: Literal["qdrant", "in_memory", "pgvector"] = "qdrant"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_collection_name: str = "transcripts"

    # For PostgreSQL Vector Store (alternative)
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "transcripts_db"
    postgres_user: str = "postgres"
    postgres_password: str = ""

    # Document Search Settings
    chunk_size: int = 500
    chunk_overlap: int = 50
    search_k: int = 5
    search_score_threshold: float = 0.7

    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_cors_origins: list[str] = ["*"]
    api_workers: int = 4

    # Authentication Settings
    jwt_secret_key: str = "change-this-to-a-secure-random-key-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60 * 24  # 24 hours

    # API Keys
    openai_api_key: str = ""  # Required if using OpenAI provider
    openrouter_api_key: str = ""  # Required if using OpenRouter provider
    openrouter_api_base: str = "https://openrouter.ai/api/v1"  # OpenRouter API base URL

    # Logging Settings
    log_level: str = "INFO"
    log_format: str = "json"  # "json" or "text"
    log_file: str = "logs/transcript_chatbot.log"

    # Rate Limiting
    rate_limit_requests_per_minute: int = 60

    # Storage Settings (for transcript uploads)
    upload_dir: str = "data/uploads"
    max_upload_size_mb: int = 10
    allowed_file_types: list[str] = [".txt", ".pdf", ".docx", ".json"]

    # Observability
    enable_tracing: bool = False
    otel_endpoint: str = "http://localhost:4318"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure required directories exist
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)


# Global settings instance
settings = Settings()
