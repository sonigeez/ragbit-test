"""
Simple example of using the Transcript Chatbot without the API.
This is useful for testing and development.
"""
import asyncio
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.transcript_chatbot.chatbot import TranscriptChatbot
from src.transcript_chatbot.models import Transcript, TranscriptMetadata
from src.transcript_chatbot.transcript_service import TranscriptServiceFactory


async def main():
    """Example usage of the Transcript Chatbot."""

    # User ID for this example
    user_id = "example_user_123"

    # Create a sample transcript
    sample_transcript = """
    Meeting Transcript - Q4 Planning Session
    Date: November 1, 2024
    Participants: Alice, Bob, Charlie

    Alice: Good morning everyone. Let's start with reviewing our Q4 objectives.

    Bob: Thanks Alice. Our main focus should be on improving user engagement.
    The data shows we need to work on retention.

    Charlie: Agreed. I propose we implement a new onboarding flow. We should also
    consider adding push notifications for important updates.

    Alice: Great ideas. Let's make sure we have the resources. Bob, can you lead
    the engagement initiative?

    Bob: Absolutely. I'll need support from the engineering team. Charlie, can you
    help with the technical implementation?

    Charlie: Yes, I can allocate 3 engineers to this project starting next week.

    Alice: Perfect. Let's target a launch date of December 15th. Any concerns?

    Bob: That timeline works for me.

    Charlie: Same here. We should schedule weekly check-ins though.

    Alice: Agreed. Action items:
    1. Bob to create detailed engagement strategy by Nov 8
    2. Charlie to assign engineering team by Nov 5
    3. Weekly check-ins every Friday at 10am
    4. Target launch: December 15, 2024

    Meeting adjourned.
    """

    # Create transcript metadata
    metadata = TranscriptMetadata(
        user_id=user_id,
        meeting_title="Q4 Planning Session",
        participants=["Alice", "Bob", "Charlie"],
        tags=["planning", "q4", "engagement"],
    )

    # Create transcript object
    transcript = Transcript(
        metadata=metadata,
        content=sample_transcript,
        summary="Team discussed Q4 objectives focusing on user engagement and retention.",
    )

    print("=" * 80)
    print("Transcript Chatbot - Simple Example")
    print("=" * 80)
    print("\nStep 1: Ingesting transcript into vector store...")

    # Get transcript service and ingest
    transcript_service = TranscriptServiceFactory.get_service(user_id)
    transcript_id = await transcript_service.ingest_transcript(transcript)

    print(f"✓ Transcript ingested successfully! ID: {transcript_id}")

    # Create chatbot
    print("\nStep 2: Creating chatbot instance...")
    chatbot = TranscriptChatbot(user_id=user_id)
    chatbot.set_active_transcripts([transcript_id])
    print("✓ Chatbot ready!")

    # Ask some questions
    print("\n" + "=" * 80)
    print("Chatbot Demo - Asking Questions")
    print("=" * 80)

    questions = [
        "What were the main topics discussed in the meeting?",
        "What are the action items from this meeting?",
        "Who is responsible for the engagement strategy?",
        "When is the target launch date?",
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n[Question {i}]: {question}")
        print("-" * 80)

        response = await chatbot.chat(question)
        print(f"[Answer]: {response}")

    # Example with streaming
    print("\n" + "=" * 80)
    print("Streaming Response Demo")
    print("=" * 80)

    question = "Summarize the key decisions and next steps from this meeting."
    print(f"\n[Question]: {question}")
    print("-" * 80)
    print("[Answer]: ", end="", flush=True)

    async for chunk in chatbot.chat_streaming(question):
        print(chunk, end="", flush=True)

    print("\n\n" + "=" * 80)
    print("Example completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
