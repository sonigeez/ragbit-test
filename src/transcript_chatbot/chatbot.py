"""
Main chatbot implementation with RAG capabilities for transcript analysis.
"""
from typing import AsyncGenerator, Optional
from collections.abc import Iterable

from ragbits.core.llms import LiteLLM
from ragbits.document_search.documents.element import Element

from config.settings import settings
from src.transcript_chatbot.logger import logger
from src.transcript_chatbot.models import ChatMessage, ConversationContext
from src.transcript_chatbot.prompts import (
    ChatHistoryInput,
    ChatWithHistoryPrompt,
    TranscriptQuestionInput,
    TranscriptQuestionPrompt,
)
from src.transcript_chatbot.transcript_service import TranscriptServiceFactory


class TranscriptChatbot:
    """
    A chatbot that can answer questions about meeting transcripts using RAG.

    Features:
    - Retrieval-augmented generation for accurate answers
    - Conversation history tracking
    - User-specific data isolation
    - Streaming responses
    """

    def __init__(self, user_id: str, conversation_context: Optional[ConversationContext] = None):
        """
        Initialize the chatbot for a specific user.

        Args:
            user_id: The ID of the user
            conversation_context: Optional existing conversation context
        """
        self.user_id = user_id
        self.context = conversation_context or ConversationContext(user_id=user_id)

        # Initialize LLM
        self.llm = LiteLLM(
            model_name=settings.llm_model_name,
            api_key=settings.openai_api_key if settings.openai_api_key else None,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
        )

        # Get transcript service for this user
        self.transcript_service = TranscriptServiceFactory.get_service(user_id)

        logger.info(
            f"Initialized TranscriptChatbot for user {user_id}, "
            f"conversation {self.context.conversation_id}"
        )

    async def chat(
        self,
        message: str,
        transcript_ids: Optional[list[str]] = None,
        use_history: bool = True,
    ) -> str:
        """
        Send a message to the chatbot and get a response.

        Args:
            message: The user's message/question
            transcript_ids: Optional list of specific transcript IDs to search
            use_history: Whether to use conversation history (default: True)

        Returns:
            The chatbot's response

        Raises:
            Exception: If there's an error processing the message
        """
        logger.info(f"User {self.user_id} sent message: '{message[:100]}...'")

        try:
            # Search for relevant transcript chunks
            relevant_chunks = await self.transcript_service.search_transcripts(
                query=message,
                transcript_ids=transcript_ids or self.context.transcript_ids,
                max_results=settings.search_k,
            )

            if not relevant_chunks:
                logger.warning("No relevant transcript chunks found")
                return (
                    "I couldn't find any relevant information in your transcripts "
                    "to answer that question. Could you rephrase or ask about something else?"
                )

            # Build prompt based on whether we use history
            if use_history and len(self.context.messages) > 0:
                # Use chat with history prompt
                conversation_history = [
                    {"role": msg.role, "content": msg.content}
                    for msg in self.context.messages[-6:]  # Last 3 exchanges
                ]

                prompt = ChatWithHistoryPrompt(
                    ChatHistoryInput(
                        question=message,
                        context=relevant_chunks,
                        conversation_history=conversation_history,
                    )
                )
            else:
                # Use simple question-answering prompt
                metadata_str = self._build_metadata_string(relevant_chunks)
                prompt = TranscriptQuestionPrompt(
                    TranscriptQuestionInput(
                        question=message,
                        context=relevant_chunks,
                        transcript_metadata=metadata_str,
                    )
                )

            # Generate response
            response = await self.llm.generate(prompt)

            # Store in conversation history
            self.context.messages.append(
                ChatMessage(
                    role="user",
                    content=message,
                    metadata={"transcript_ids": transcript_ids or self.context.transcript_ids},
                )
            )
            self.context.messages.append(
                ChatMessage(
                    role="assistant",
                    content=response,
                    metadata={"chunks_used": len(relevant_chunks)},
                )
            )

            logger.info(f"Generated response with {len(relevant_chunks)} context chunks")
            return response

        except Exception as e:
            logger.error(f"Error in chat: {e}", exc_info=True)
            raise

    async def chat_streaming(
        self,
        message: str,
        transcript_ids: Optional[list[str]] = None,
        use_history: bool = True,
    ) -> AsyncGenerator[str, None]:
        """
        Send a message and get a streaming response.

        Args:
            message: The user's message/question
            transcript_ids: Optional list of specific transcript IDs to search
            use_history: Whether to use conversation history

        Yields:
            Chunks of the response as they're generated

        Raises:
            Exception: If there's an error processing the message
        """
        logger.info(f"User {self.user_id} sent streaming message: '{message[:100]}...'")

        try:
            # Search for relevant chunks
            relevant_chunks = await self.transcript_service.search_transcripts(
                query=message,
                transcript_ids=transcript_ids or self.context.transcript_ids,
                max_results=settings.search_k,
            )

            if not relevant_chunks:
                yield (
                    "I couldn't find any relevant information in your transcripts "
                    "to answer that question. Could you rephrase or ask about something else?"
                )
                return

            # Build prompt
            if use_history and len(self.context.messages) > 0:
                conversation_history = [
                    {"role": msg.role, "content": msg.content}
                    for msg in self.context.messages[-6:]
                ]

                prompt = ChatWithHistoryPrompt(
                    ChatHistoryInput(
                        question=message,
                        context=relevant_chunks,
                        conversation_history=conversation_history,
                    )
                )
            else:
                metadata_str = self._build_metadata_string(relevant_chunks)
                prompt = TranscriptQuestionPrompt(
                    TranscriptQuestionInput(
                        question=message,
                        context=relevant_chunks,
                        transcript_metadata=metadata_str,
                    )
                )

            # Stream response
            full_response = ""
            async for chunk in self.llm.generate_streaming(prompt):
                full_response += chunk
                yield chunk

            # Store in history
            self.context.messages.append(
                ChatMessage(
                    role="user",
                    content=message,
                    metadata={"transcript_ids": transcript_ids or self.context.transcript_ids},
                )
            )
            self.context.messages.append(
                ChatMessage(
                    role="assistant",
                    content=full_response,
                    metadata={"chunks_used": len(relevant_chunks)},
                )
            )

            logger.info(f"Completed streaming response with {len(relevant_chunks)} chunks")

        except Exception as e:
            logger.error(f"Error in streaming chat: {e}", exc_info=True)
            raise

    def _build_metadata_string(self, chunks: Iterable[Element]) -> str:
        """
        Build a metadata string from document chunks.

        Args:
            chunks: The document chunks

        Returns:
            A formatted string with metadata information
        """
        metadata_parts = []
        seen_transcripts = set()

        for chunk in chunks:
            if hasattr(chunk, "metadata") and chunk.metadata:
                transcript_id = chunk.metadata.get("transcript_id")
                if transcript_id and transcript_id not in seen_transcripts:
                    seen_transcripts.add(transcript_id)
                    meeting_title = chunk.metadata.get("meeting_title", "Unknown")
                    meeting_date = chunk.metadata.get("meeting_date", "Unknown")
                    metadata_parts.append(
                        f"- Meeting: {meeting_title} (Date: {meeting_date})"
                    )

        if metadata_parts:
            return "Searching in these transcripts:\n" + "\n".join(metadata_parts)
        return ""

    def clear_history(self) -> None:
        """Clear the conversation history."""
        logger.info(f"Clearing conversation history for user {self.user_id}")
        self.context.messages.clear()

    def get_context(self) -> ConversationContext:
        """
        Get the current conversation context.

        Returns:
            The conversation context
        """
        return self.context

    def set_active_transcripts(self, transcript_ids: list[str]) -> None:
        """
        Set which transcripts are active for this conversation.

        Args:
            transcript_ids: List of transcript IDs to make active
        """
        logger.info(
            f"Setting active transcripts for user {self.user_id}: {transcript_ids}"
        )
        self.context.transcript_ids = transcript_ids
