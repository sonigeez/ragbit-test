"""
FastAPI application for the Transcript Chatbot.
"""
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr

from ragbits.chat.api import RagbitsAPI

from config.settings import settings
from src.transcript_chatbot.logger import logger
from src.transcript_chatbot.auth import (
    create_access_token,
    create_user,
    authenticate_user,
    get_current_user,
)
from src.transcript_chatbot.chat_interface import TranscriptChatInterface
from src.transcript_chatbot.models import Transcript, TranscriptMetadata
from src.transcript_chatbot.transcript_service import TranscriptServiceFactory


# Request/Response Models
class RegisterRequest(BaseModel):
    """Request model for user registration."""

    email: EmailStr
    username: str
    password: str


class LoginRequest(BaseModel):
    """Request model for user login."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response model for authentication token."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TranscriptUploadResponse(BaseModel):
    """Response model for transcript upload."""

    transcript_id: str
    message: str


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str
    error_code: Optional[str] = None


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    logger.info("Starting Transcript Chatbot API")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"LLM Model: {settings.llm_model_name}")
    logger.info(f"Vector Store: {settings.vector_store_type}")

    yield

    logger.info("Shutting down Transcript Chatbot API")
    # Cleanup
    TranscriptServiceFactory.clear_cache()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Production-ready chatbot for meeting transcript analysis with RAG",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": "1.0.0",
    }


# Authentication endpoints
@app.post("/auth/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    """
    Register a new user.

    Args:
        request: Registration request with email, username, and password

    Returns:
        Access token for the new user

    Raises:
        HTTPException: If user already exists
    """
    try:
        user = create_user(
            email=request.email,
            username=request.username,
            password=request.password,
        )

        access_token = create_access_token(user.id)

        return TokenResponse(
            access_token=access_token,
            expires_in=settings.jwt_access_token_expire_minutes * 60,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@app.post("/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Authenticate a user and return access token.

    Args:
        request: Login request with email and password

    Returns:
        Access token

    Raises:
        HTTPException: If authentication fails
    """
    user = authenticate_user(request.email, request.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(user.id)

    return TokenResponse(
        access_token=access_token,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


# Transcript management endpoints
@app.post("/transcripts/upload", response_model=TranscriptUploadResponse)
async def upload_transcript(
    file: UploadFile = File(...),
    meeting_title: str = Form(...),
    meeting_date: Optional[str] = Form(None),
    participants: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    user_id: str = Depends(get_current_user),
):
    """
    Upload a meeting transcript.

    Args:
        file: The transcript file (text, PDF, etc.)
        meeting_title: Title of the meeting
        meeting_date: Optional meeting date (ISO format)
        participants: Optional comma-separated list of participants
        tags: Optional comma-separated list of tags
        user_id: Current user ID (from auth)

    Returns:
        Transcript ID and success message

    Raises:
        HTTPException: If upload fails
    """
    try:
        # Read file content
        content = await file.read()
        content_str = content.decode("utf-8")

        # Parse optional fields
        participants_list = (
            [p.strip() for p in participants.split(",")]
            if participants
            else []
        )
        tags_list = [t.strip() for t in tags.split(",")] if tags else []

        # Create transcript metadata
        metadata = TranscriptMetadata(
            user_id=user_id,
            meeting_title=meeting_title,
            meeting_date=meeting_date,
            participants=participants_list,
            tags=tags_list,
            file_size_bytes=len(content),
            source_format=file.filename.split(".")[-1] if file.filename else "txt",
        )

        # Create transcript
        transcript = Transcript(
            metadata=metadata,
            content=content_str,
        )

        # Ingest into vector store
        transcript_service = TranscriptServiceFactory.get_service(user_id)
        transcript_id = await transcript_service.ingest_transcript(transcript)

        logger.info(f"Successfully uploaded transcript {transcript_id} for user {user_id}")

        return TranscriptUploadResponse(
            transcript_id=transcript_id,
            message="Transcript uploaded and indexed successfully",
        )

    except Exception as e:
        logger.error(f"Error uploading transcript: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload transcript: {str(e)}",
        )


@app.get("/transcripts/{transcript_id}")
async def get_transcript(
    transcript_id: str,
    user_id: str = Depends(get_current_user),
):
    """
    Get transcript metadata.

    Note: This is a placeholder. In production, you'd store and retrieve
    full transcript metadata from a database.

    Args:
        transcript_id: The transcript ID
        user_id: Current user ID (from auth)

    Returns:
        Transcript metadata
    """
    # This would query your database in production
    return {
        "transcript_id": transcript_id,
        "user_id": user_id,
        "message": "Transcript retrieval not yet implemented. Use chat to query transcripts.",
    }


# Mount Ragbits Chat API
# Note: RagbitsAPI expects a class, not an instance
ragbits_api = RagbitsAPI(TranscriptChatInterface)

# Mount the chat endpoints under /chat
app.mount("/chat", ragbits_api.app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.transcript_chatbot.api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
