"""
Factory for creating vector stores based on configuration.
"""
import os
from ragbits.core.embeddings import LiteLLMEmbedder
from ragbits.core.vector_stores.base import VectorStore
from ragbits.core.vector_stores.in_memory import InMemoryVectorStore

from config.settings import settings
from src.transcript_chatbot.logger import logger


def create_embedder() -> LiteLLMEmbedder:
    """
    Create an embedder instance based on configuration.
    Supports both OpenAI and OpenRouter providers.

    Returns:
        LiteLLMEmbedder: Configured embedder instance

    Raises:
        ValueError: If provider is not configured correctly
    """
    provider = settings.embedding_provider
    model_name = settings.embedding_model_name

    logger.info(f"Creating embedder with provider: {provider}, model: {model_name}")

    # Configure environment variables based on provider
    if provider == "openrouter":
        if not settings.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY is required when using OpenRouter provider")

        # Set OpenRouter environment variables for LiteLLM
        os.environ["OPENROUTER_API_KEY"] = settings.openrouter_api_key
        os.environ["OPENROUTER_API_BASE"] = settings.openrouter_api_base

        # For OpenRouter, ensure model name has the correct prefix
        if not model_name.startswith("openrouter/"):
            logger.warning(
                f"OpenRouter model '{model_name}' doesn't have 'openrouter/' prefix. "
                f"Using as-is, but you may need to add the prefix."
            )

        return LiteLLMEmbedder(model_name=model_name)

    elif provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")

        return LiteLLMEmbedder(
            model_name=model_name,
            api_key=settings.openai_api_key
        )

    else:
        raise ValueError(f"Unsupported embedding provider: {provider}")


def create_vector_store() -> VectorStore:
    """
    Create a vector store instance based on configuration.

    Returns:
        VectorStore: Configured vector store instance

    Raises:
        ValueError: If vector store type is not supported
    """
    embedder = create_embedder()

    if settings.vector_store_type == "in_memory":
        logger.info("Creating InMemoryVectorStore")
        return InMemoryVectorStore(embedder=embedder)

    elif settings.vector_store_type == "qdrant":
        logger.info(f"Creating Qdrant vector store at {settings.qdrant_url}")
        try:
            from ragbits.core.vector_stores.qdrant import QdrantVectorStore
            from qdrant_client import AsyncQdrantClient

            # Create Qdrant client
            client = AsyncQdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key if settings.qdrant_api_key else None,
            )

            return QdrantVectorStore(
                client=client,
                index_name=settings.qdrant_collection_name,
                embedder=embedder,
            )
        except ImportError as e:
            logger.error(f"Qdrant support not installed: {e}")
            logger.error("Install with: pip install qdrant-client")
            raise

    elif settings.vector_store_type == "pgvector":
        logger.info(f"Creating PgVector store at {settings.postgres_host}")
        try:
            from ragbits.core.vector_stores.pgvector import PGVectorStore

            connection_string = (
                f"postgresql://{settings.postgres_user}:{settings.postgres_password}"
                f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
            )

            return PGVectorStore(
                connection_string=connection_string,
                embedder=embedder,
            )
        except ImportError:
            logger.error("PgVector support not installed. Install with: pip install ragbits[pgvector]")
            raise

    else:
        raise ValueError(f"Unsupported vector store type: {settings.vector_store_type}")
