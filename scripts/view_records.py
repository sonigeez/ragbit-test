#!/usr/bin/env python3
"""
Utility to view all records in the vector store.
Works with both in-memory and Qdrant storage.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from src.transcript_chatbot.auth import _users_db
from src.transcript_chatbot.transcript_service import TranscriptServiceFactory


async def view_in_memory_records():
    """View records in the in-memory vector store."""
    print("\n" + "=" * 70)
    print("IN-MEMORY VECTOR STORE RECORDS")
    print("=" * 70)

    # Show all user services
    services = TranscriptServiceFactory._instances

    if not services:
        print("\n⚠️  No services initialized yet.")
        print("   Transcripts are only loaded when a service is created.")
        print("\n   To see records:")
        print("   1. Run an ingestion script (e.g., python examples/ingest_transcript.py)")
        print("   2. Then run this script again")
        return

    print(f"\n📊 Found {len(services)} user service(s)")

    for user_id, service in services.items():
        print(f"\n{'─' * 70}")
        print(f"User ID: {user_id}")
        print(f"{'─' * 70}")

        # Access the vector store
        vector_store = service.vector_store

        # For in-memory vector store, we can access the internal storage
        if hasattr(vector_store, '_storage'):
            storage = vector_store._storage
            print(f"  Total entries: {len(storage)}")

            if storage:
                print("\n  Sample entries:")
                for i, (key, entry) in enumerate(list(storage.items())[:3], 1):
                    print(f"\n  Entry {i}:")
                    print(f"    Key: {key[:50]}...")
                    if hasattr(entry, 'content'):
                        preview = entry.content[:100].replace('\n', ' ')
                        print(f"    Content: {preview}...")
                    if hasattr(entry, 'metadata'):
                        print(f"    Metadata: {entry.metadata}")

                if len(storage) > 3:
                    print(f"\n  ... and {len(storage) - 3} more entries")
        else:
            print("  ⚠️  Cannot access internal storage structure")


async def view_qdrant_records():
    """View records in Qdrant."""
    print("\n" + "=" * 70)
    print("QDRANT VECTOR STORE RECORDS")
    print("=" * 70)

    try:
        from qdrant_client import QdrantClient

        client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key if settings.qdrant_api_key else None,
        )

        # Get collection info
        collection_name = settings.qdrant_collection_name

        try:
            collection_info = client.get_collection(collection_name)
            print(f"\n📊 Collection: {collection_name}")
            print(f"   Total vectors: {collection_info.points_count}")
            print(f"   Vector size: {collection_info.config.params.vectors.size}")
            print(f"   Distance: {collection_info.config.params.vectors.distance}")

            # Get some sample points
            print("\n🔍 Sample records:")
            scroll_result = client.scroll(
                collection_name=collection_name,
                limit=5,
                with_payload=True,
                with_vectors=False  # Don't fetch large vectors
            )

            points, _ = scroll_result

            if points:
                for i, point in enumerate(points, 1):
                    print(f"\n  Record {i}:")
                    print(f"    ID: {point.id}")
                    if point.payload:
                        print(f"    Payload keys: {list(point.payload.keys())}")

                        # Show metadata if available
                        if 'metadata' in point.payload:
                            metadata = point.payload['metadata']
                            print(f"    Metadata:")
                            for key, value in metadata.items():
                                if key != 'content':  # Skip large content
                                    print(f"      - {key}: {value}")

                        # Show content preview
                        if 'content' in point.payload or 'text' in point.payload:
                            content = point.payload.get('content') or point.payload.get('text', '')
                            preview = content[:100].replace('\n', ' ')
                            print(f"    Content preview: {preview}...")
            else:
                print("\n  No records found in collection")

        except Exception as e:
            print(f"\n⚠️  Collection '{collection_name}' not found or error: {e}")
            print("\n   Available collections:")
            collections = client.get_collections()
            if collections.collections:
                for col in collections.collections:
                    print(f"   - {col.name}")
            else:
                print("   (none)")

    except ImportError:
        print("\n⚠️  Qdrant client not installed.")
        print("   Install with: pip install qdrant-client")
    except Exception as e:
        print(f"\n❌ Error connecting to Qdrant: {e}")
        print(f"\n   Make sure Qdrant is running at: {settings.qdrant_url}")
        print("   Start Qdrant with: docker run -p 6333:6333 qdrant/qdrant")


def view_users():
    """View all registered users."""
    print("\n" + "=" * 70)
    print("REGISTERED USERS")
    print("=" * 70)

    if not _users_db:
        print("\n⚠️  No users registered yet")
        print("\n   To register a user:")
        print("   - Use the API: POST /auth/register")
        print("   - Or run: python examples/api_client_example.py")
        return

    print(f"\n👥 Total users: {len(_users_db)}")

    for email, user_data in _users_db.items():
        user = user_data['user']
        print(f"\n  • Email: {email}")
        print(f"    Username: {user.username}")
        print(f"    User ID: {user.id}")
        print(f"    Created: {user.created_at}")


async def main():
    """Main function to view all records."""
    print("=" * 70)
    print("RAGBIT TRANSCRIPT CHATBOT - DATABASE VIEWER")
    print("=" * 70)
    print(f"\nCurrent configuration:")
    print(f"  Vector Store: {settings.vector_store_type}")
    print(f"  Embedding Provider: {settings.embedding_provider}")
    print(f"  LLM Provider: {settings.llm_provider}")

    # View users
    view_users()

    # View vector store records based on type
    if settings.vector_store_type == "in_memory":
        await view_in_memory_records()

        print("\n" + "=" * 70)
        print("💡 TIP: Switch to Qdrant for persistent storage")
        print("=" * 70)
        print("\n1. Start Qdrant:")
        print("   docker run -p 6333:6333 qdrant/qdrant")
        print("\n2. Update .env:")
        print("   VECTOR_STORE_TYPE=qdrant")
        print("\n3. Restart your application")

    elif settings.vector_store_type == "qdrant":
        await view_qdrant_records()

    else:
        print(f"\n⚠️  Unsupported vector store type: {settings.vector_store_type}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
