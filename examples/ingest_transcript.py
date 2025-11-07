#!/usr/bin/env python3
"""
Simple example of ingesting a transcript into the system.
This demonstrates how to programmatically add transcripts for a user.
"""
import asyncio
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.transcript_chatbot.transcript_service import TranscriptServiceFactory
from src.transcript_chatbot.models import Transcript, TranscriptMetadata


async def ingest_sample_transcript():
    """Ingest a sample meeting transcript."""

    # User ID (in production, this comes from authentication)
    user_id = "demo_user_123"

    print("=" * 70)
    print("Transcript Ingestion Example")
    print("=" * 70)

    # Sample transcript content
    transcript_content = """
    Sprint Planning Meeting - November 7, 2024
    Participants: Sarah (Product Manager), Mike (Tech Lead), Alice (Developer)

    Sarah: Good morning everyone! Let's plan our sprint for the next two weeks.

    Mike: Thanks Sarah. I've reviewed the backlog and identified three key priorities:
    1. Fix the authentication bug that's affecting mobile users
    2. Implement the new dashboard analytics feature
    3. Optimize database queries for the reporting module

    Alice: The authentication bug is critical. I can take that on - it should be
    about 5 story points. I estimate it'll take 3 days.

    Mike: Perfect. I'll handle the dashboard feature. That's around 8 points, and
    I'm targeting completion by next Wednesday.

    Sarah: What about the database optimization?

    Mike: Let's defer that to the next sprint. We should focus on the user-facing
    issues first.

    Alice: Agreed. When's our sprint review?

    Sarah: November 19th at 2 PM. Let's make sure we demo both features.

    Mike: Sounds good. I'll update the sprint board.

    Sarah: Great! Any blockers or concerns?

    Alice: I might need help with iOS testing for the auth fix.

    Mike: I can help with that. Let's sync on Friday.

    Sarah: Perfect. Let's get to work!
    """

    print(f"\n[1] Creating TranscriptService for user: {user_id}")
    service = TranscriptServiceFactory.get_service(user_id)
    print("✓ Service created")

    print("\n[2] Preparing transcript metadata...")
    metadata = TranscriptMetadata(
        user_id=user_id,
        meeting_title="Sprint Planning - November 2024",
        meeting_date="2024-11-07",
        participants=["Sarah", "Mike", "Alice"],
        tags=["sprint-planning", "engineering", "product"],
        file_size_bytes=len(transcript_content.encode()),
        source_format="txt"
    )
    print(f"✓ Metadata prepared")
    print(f"  - Title: {metadata.meeting_title}")
    print(f"  - Participants: {', '.join(metadata.participants)}")
    print(f"  - Tags: {', '.join(metadata.tags)}")

    print("\n[3] Creating transcript object...")
    transcript = Transcript(
        metadata=metadata,
        content=transcript_content
    )
    print("✓ Transcript created")

    print("\n[4] Ingesting transcript into vector store...")
    print("  (This will chunk the text and create embeddings)")
    transcript_id = await service.ingest_transcript(transcript)
    print(f"✓ Transcript ingested successfully!")
    print(f"  Transcript ID: {transcript_id}")

    print("\n[5] Testing search...")
    results = await service.search_transcripts(
        query="What tasks were assigned?",
        k=3
    )
    print(f"✓ Found {len(results)} relevant chunks")
    if results:
        print(f"\n  Top result preview:")
        print(f"  {results[0].text_representation[:200]}...")

    print("\n" + "=" * 70)
    print("✓ Ingestion Complete!")
    print("=" * 70)
    print("\nYou can now:")
    print("1. Search this transcript using the search API")
    print("2. Ask questions about it using the chat interface")
    print("3. Ingest more transcripts for this user")
    print("\nNext steps:")
    print("- Run: python examples/simple_chat_example.py")
    print("- Or start the API server and use the REST endpoints")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(ingest_sample_transcript())
