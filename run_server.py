#!/usr/bin/env python3
"""
Production server runner for the Transcript Chatbot API.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn
from config.settings import settings


if __name__ == "__main__":
    print("=" * 80)
    print(f"Starting {settings.app_name}")
    print("=" * 80)
    print(f"Environment: {settings.environment}")
    print(f"Host: {settings.api_host}")
    print(f"Port: {settings.api_port}")
    print(f"LLM Model: {settings.llm_model_name}")
    print(f"Vector Store: {settings.vector_store_type}")
    print("=" * 80)

    uvicorn.run(
        "src.transcript_chatbot.api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        workers=1 if settings.debug else settings.api_workers,
        log_level=settings.log_level.lower(),
        access_log=True,
    )
