"""
Service for managing and searching meeting transcripts with user isolation.
"""
from typing import Optional
from pathlib import Path
import json

from ragbits.document_search import DocumentSearch
from ragbits.document_search.documents.document import DocumentMeta, DocumentType
from ragbits.document_search.documents.sources import LocalFileSource
from ragbits.document_search.documents.element import Element

from config.settings import settings
from src.transcript_chatbot.logger import logger
from src.transcript_chatbot.models import Transcript, TranscriptMetadata
from src.transcript_chatbot.vector_store_factory import create_vector_store


class TranscriptService:
    """
    Service for managing meeting transcripts with user-level data isolation.

    This service handles:
    - Ingesting transcripts into the vector store
    - Searching transcripts with user-specific filtering
    - Managing transcript metadata
    """

    def __init__(self, user_id: str):
        """
        Initialize the transcript service for a specific user.

        Args:
            user_id: The ID of the user (for data isolation)
        """
        self.user_id = user_id
        self.vector_store = create_vector_store()
        self.document_search = DocumentSearch(
            vector_store=self.vector_store,
        )
        logger.info(f"Initialized TranscriptService for user: {user_id}")

    async def ingest_transcript(
        self,
        transcript: Transcript,
    ) -> str:
        """
        Ingest a transcript into the vector store.

        Args:
            transcript: The transcript to ingest

        Returns:
            str: The transcript ID

        Raises:
            ValueError: If the transcript user_id doesn't match the service user_id
        """
        if transcript.metadata.user_id != self.user_id:
            raise ValueError(
                f"Transcript user_id {transcript.metadata.user_id} "
                f"doesn't match service user_id {self.user_id}"
            )

        logger.info(
            f"Ingesting transcript {transcript.metadata.transcript_id} "
            f"for user {self.user_id}"
        )

        try:
            # Save transcript content to a temporary file for ingestion
            temp_file = Path(settings.upload_dir) / f"{transcript.metadata.transcript_id}.txt"
            temp_file.write_text(transcript.content, encoding="utf-8")

            # Create document metadata with user_id for filtering
            doc_meta = DocumentMeta(
                document_type=DocumentType.TXT,
                source=LocalFileSource(path=temp_file),
                metadata={
                    "user_id": self.user_id,
                    "transcript_id": transcript.metadata.transcript_id,
                    "meeting_title": transcript.metadata.meeting_title,
                    "meeting_date": (
                        transcript.metadata.meeting_date.isoformat()
                        if transcript.metadata.meeting_date
                        else None
                    ),
                    "participants": transcript.metadata.participants,
                    "tags": transcript.metadata.tags,
                    "summary": transcript.summary,
                }
            )

            # Ingest the transcript
            await self.document_search.ingest(
                [doc_meta],
            )

            # Clean up temp file
            if temp_file.exists():
                temp_file.unlink()

            logger.info(
                f"Successfully ingested transcript {transcript.metadata.transcript_id}"
            )
            return transcript.metadata.transcript_id

        except Exception as e:
            logger.error(
                f"Error ingesting transcript {transcript.metadata.transcript_id}: {e}",
                exc_info=True,
            )
            raise

    async def search_transcripts(
        self,
        query: str,
        transcript_ids: Optional[list[str]] = None,
        max_results: int = None,
    ) -> list[Element]:
        """
        Search transcripts for relevant content.

        Args:
            query: The search query
            transcript_ids: Optional list of specific transcript IDs to search
            max_results: Maximum number of results to return (default from settings)

        Returns:
            List of relevant document elements
        """
        max_results = max_results or settings.search_k

        logger.info(
            f"Searching transcripts for user {self.user_id} "
            f"with query: '{query[:100]}...'"
        )

        try:
            # Build metadata filters for user isolation
            metadata_filter = {"user_id": self.user_id}

            if transcript_ids:
                # If specific transcripts requested, add to filter
                metadata_filter["transcript_id"] = {"$in": transcript_ids}

            # Perform search
            results = await self.document_search.search(
                query=query,
                max_results=max_results,
                metadata_filter=metadata_filter,
            )

            logger.info(f"Found {len(results)} relevant chunks")
            return results

        except Exception as e:
            logger.error(f"Error searching transcripts: {e}", exc_info=True)
            raise

    async def delete_transcript(self, transcript_id: str) -> None:
        """
        Delete a transcript from the vector store.

        Args:
            transcript_id: The ID of the transcript to delete

        Raises:
            NotImplementedError: Vector store deletion not yet implemented
        """
        logger.info(f"Deleting transcript {transcript_id} for user {self.user_id}")

        # Note: Vector store deletion depends on the specific implementation
        # This would need to be implemented based on your vector store choice
        raise NotImplementedError(
            "Transcript deletion not yet implemented. "
            "This depends on vector store capabilities."
        )

    async def list_user_transcripts(self) -> list[TranscriptMetadata]:
        """
        List all transcripts for the current user.

        Returns:
            List of transcript metadata

        Note:
            This requires vector store support for listing/filtering by metadata.
            Implementation depends on your chosen vector store.
        """
        logger.info(f"Listing transcripts for user {self.user_id}")

        # This would need to be implemented based on vector store capabilities
        raise NotImplementedError(
            "Transcript listing not yet implemented. "
            "This depends on vector store capabilities."
        )


class TranscriptServiceFactory:
    """Factory for creating TranscriptService instances."""

    _instances: dict[str, TranscriptService] = {}

    @classmethod
    def get_service(cls, user_id: str) -> TranscriptService:
        """
        Get or create a TranscriptService instance for a user.

        Args:
            user_id: The user ID

        Returns:
            TranscriptService instance for the user
        """
        if user_id not in cls._instances:
            cls._instances[user_id] = TranscriptService(user_id)
        return cls._instances[user_id]

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the service cache."""
        cls._instances.clear()
