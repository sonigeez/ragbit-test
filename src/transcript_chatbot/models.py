"""
Data models for the Transcript Chatbot application.
"""
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class User(BaseModel):
    """User model for authentication and authorization."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    email: str
    username: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TranscriptMetadata(BaseModel):
    """Metadata for a meeting transcript."""

    transcript_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    meeting_title: str
    meeting_date: Optional[datetime] = None
    participants: list[str] = Field(default_factory=list)
    duration_minutes: Optional[int] = None
    tags: list[str] = Field(default_factory=list)
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    file_size_bytes: Optional[int] = None
    source_format: Optional[str] = None  # e.g., "txt", "vtt", "json"


class Transcript(BaseModel):
    """Full transcript data with content and metadata."""

    metadata: TranscriptMetadata
    content: str
    summary: Optional[str] = None


class ChatMessage(BaseModel):
    """A single message in a chat conversation."""

    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ConversationContext(BaseModel):
    """Context for a conversation session."""

    user_id: str
    transcript_ids: list[str] = Field(default_factory=list)
    conversation_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    messages: list[ChatMessage] = Field(default_factory=list)
