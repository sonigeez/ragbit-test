"""
Ragbits Chat Interface implementation for the Transcript Chatbot.
"""
from collections.abc import AsyncGenerator
from typing import Any

from ragbits.chat.interface import ChatInterface
from ragbits.chat.interface.types import ChatContext, ChatResponse, LiveUpdateType

from src.transcript_chatbot.chatbot import TranscriptChatbot
from src.transcript_chatbot.logger import logger
from src.transcript_chatbot.models import ConversationContext


class TranscriptChatInterface(ChatInterface):
    """
    Chat interface for the transcript chatbot with Ragbits API integration.

    This provides the bridge between the Ragbits Chat API and our
    custom transcript chatbot implementation.
    """

    def __init__(self):
        """Initialize the chat interface."""
        super().__init__()
        self.chatbot: TranscriptChatbot | None = None
        logger.info("TranscriptChatInterface initialized")

    async def setup(self) -> None:
        """
        Setup method called when the chat interface is initialized.

        Note: The actual chatbot is created per-user in the chat method
        since we need user context from the request.
        """
        logger.info("TranscriptChatInterface setup completed")

    async def chat(
        self,
        message: str,
        history: list[dict[str, str]],
        context: ChatContext,
    ) -> AsyncGenerator[ChatResponse]:
        """
        Handle a chat message and generate responses.

        Args:
            message: The user's message
            history: Conversation history in OpenAI format
            context: Chat context containing user information

        Yields:
            ChatResponse objects with text, live updates, etc.
        """
        try:
            # Get user ID from context (set by auth middleware)
            user_id = context.extra.get("user_id")
            if not user_id:
                yield self.create_text_response(
                    "Error: User authentication required. Please log in."
                )
                return

            # Get or create conversation context
            conversation_id = context.extra.get("conversation_id")
            if conversation_id:
                # Restore conversation (in production, load from database)
                conversation_context = context.extra.get("conversation_context")
            else:
                conversation_context = None

            # Get transcript IDs to search (from context or user's active transcripts)
            transcript_ids = context.extra.get("transcript_ids")

            # Create chatbot instance for this user
            chatbot = TranscriptChatbot(
                user_id=user_id,
                conversation_context=conversation_context,
            )

            logger.info(
                f"Processing chat message for user {user_id}: '{message[:50]}...'"
            )

            # Start "searching" live update
            yield self.create_live_update(
                update_id="search",
                type=LiveUpdateType.START,
                label="Searching transcripts...",
            )

            # Start "answering" live update
            yield self.create_live_update(
                update_id="answer",
                type=LiveUpdateType.START,
                label="Generating answer...",
            )

            # Generate streaming response
            chunks_found = 0
            full_response = ""

            async for chunk in chatbot.chat_streaming(
                message=message,
                transcript_ids=transcript_ids,
                use_history=True,
            ):
                full_response += chunk
                yield self.create_text_response(chunk)

            # Finish search update
            yield self.create_live_update(
                update_id="search",
                type=LiveUpdateType.FINISH,
                label="Search complete",
                description=f"Found relevant context from your transcripts",
            )

            # Finish answer update
            yield self.create_live_update(
                update_id="answer",
                type=LiveUpdateType.FINISH,
                label="Answer complete",
            )

            # Store updated context back (in production, save to database)
            context.extra["conversation_context"] = chatbot.get_context()

            logger.info(
                f"Completed chat response for user {user_id}, "
                f"response length: {len(full_response)}"
            )

        except Exception as e:
            logger.error(f"Error in chat: {e}", exc_info=True)
            yield self.create_text_response(
                f"I'm sorry, I encountered an error processing your request. "
                f"Please try again or contact support if the problem persists."
            )


# For simple testing without the full API
class SimpleChatInterface(ChatInterface):
    """Simplified chat interface for testing without authentication."""

    def __init__(self, user_id: str = "test_user"):
        super().__init__()
        self.user_id = user_id
        self.chatbot: TranscriptChatbot | None = None

    async def setup(self) -> None:
        """Setup the chatbot."""
        self.chatbot = TranscriptChatbot(user_id=self.user_id)
        logger.info(f"SimpleChatInterface setup for user {self.user_id}")

    async def chat(
        self,
        message: str,
        history: list[dict[str, str]],
        context: ChatContext,
    ) -> AsyncGenerator[ChatResponse]:
        """Handle chat messages."""
        try:
            yield self.create_live_update(
                update_id="1",
                type=LiveUpdateType.START,
                label="Searching...",
            )

            async for chunk in self.chatbot.chat_streaming(message):
                yield self.create_text_response(chunk)

            yield self.create_live_update(
                update_id="1",
                type=LiveUpdateType.FINISH,
                label="Complete",
            )

        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            yield self.create_text_response(f"Error: {str(e)}")
