# Transcript Ingestion Guide

This guide explains all the ways you can ingest user transcripts into the system.

## Overview

The system supports multiple ingestion methods:
1. **REST API** - For mobile/web apps (production)
2. **Python SDK** - For scripts and backend services
3. **Example Scripts** - For testing and development

## Method 1: REST API (Mobile App Integration)

### Step 1: Authenticate User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "john_doe",
    "password": "secure_password"
  }'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### Step 2: Upload Transcript

```bash
curl -X POST http://localhost:8000/transcripts/upload \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@meeting_transcript.txt" \
  -F "meeting_title=Team Standup - Nov 7" \
  -F "meeting_date=2024-11-07" \
  -F "participants=Alice, Bob, Charlie" \
  -F "tags=standup, engineering"
```

Response:
```json
{
  "transcript_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Transcript uploaded and indexed successfully"
}
```

### Python Example

```python
import httpx

API_URL = "http://localhost:8000"

async def upload_transcript(token: str, file_path: str):
    async with httpx.AsyncClient() as client:
        # Upload transcript
        with open(file_path, "rb") as f:
            response = await client.post(
                f"{API_URL}/transcripts/upload",
                headers={"Authorization": f"Bearer {token}"},
                files={"file": ("transcript.txt", f, "text/plain")},
                data={
                    "meeting_title": "Sprint Planning",
                    "meeting_date": "2024-11-07",
                    "participants": "Alice, Bob",
                    "tags": "planning, sprint"
                }
            )

        result = response.json()
        return result["transcript_id"]
```

## Method 2: Python SDK (Direct)

### Basic Usage

```python
import asyncio
from src.transcript_chatbot.transcript_service import TranscriptServiceFactory
from src.transcript_chatbot.models import Transcript, TranscriptMetadata

async def ingest_transcript(user_id: str, content: str, title: str):
    # Get service for user
    service = TranscriptServiceFactory.get_service(user_id)

    # Create metadata
    metadata = TranscriptMetadata(
        user_id=user_id,
        meeting_title=title,
        meeting_date="2024-11-07",
        participants=["Alice", "Bob"],
        tags=["meeting"],
        file_size_bytes=len(content.encode()),
        source_format="txt"
    )

    # Create transcript
    transcript = Transcript(metadata=metadata, content=content)

    # Ingest
    transcript_id = await service.ingest_transcript(transcript)
    return transcript_id

# Run it
transcript_id = asyncio.run(ingest_transcript(
    user_id="user_123",
    content="Meeting transcript content...",
    title="Team Meeting"
))
```

### Batch Ingestion

```python
async def ingest_multiple_transcripts(user_id: str, transcripts_data: list):
    service = TranscriptServiceFactory.get_service(user_id)

    transcript_ids = []
    for data in transcripts_data:
        metadata = TranscriptMetadata(
            user_id=user_id,
            meeting_title=data["title"],
            meeting_date=data.get("date"),
            participants=data.get("participants", []),
            tags=data.get("tags", []),
            file_size_bytes=len(data["content"].encode()),
            source_format="txt"
        )

        transcript = Transcript(
            metadata=metadata,
            content=data["content"]
        )

        transcript_id = await service.ingest_transcript(transcript)
        transcript_ids.append(transcript_id)
        print(f"✓ Ingested: {data['title']} ({transcript_id})")

    return transcript_ids

# Usage
transcripts = [
    {
        "title": "Daily Standup - Nov 1",
        "content": "Team discussed progress...",
        "date": "2024-11-01",
        "participants": ["Alice", "Bob"],
        "tags": ["standup"]
    },
    {
        "title": "Sprint Planning - Nov 7",
        "content": "Planning for next sprint...",
        "date": "2024-11-07",
        "participants": ["Alice", "Bob", "Charlie"],
        "tags": ["planning", "sprint"]
    }
]

asyncio.run(ingest_multiple_transcripts("user_123", transcripts))
```

## Method 3: Example Scripts

### Quick Test

```bash
# Simple ingestion example
python examples/ingest_transcript.py

# Full chat example (includes ingestion)
python examples/simple_chat_example.py
```

### From File

```python
# examples/ingest_from_file.py
import asyncio
from pathlib import Path
from src.transcript_chatbot.transcript_service import TranscriptServiceFactory
from src.transcript_chatbot.models import Transcript, TranscriptMetadata

async def ingest_from_file(user_id: str, file_path: Path):
    service = TranscriptServiceFactory.get_service(user_id)

    # Read file
    content = file_path.read_text()

    # Create metadata
    metadata = TranscriptMetadata(
        user_id=user_id,
        meeting_title=file_path.stem,  # Use filename as title
        file_size_bytes=len(content.encode()),
        source_format=file_path.suffix[1:]  # Extension without dot
    )

    # Ingest
    transcript = Transcript(metadata=metadata, content=content)
    return await service.ingest_transcript(transcript)

# Usage
transcript_id = asyncio.run(ingest_from_file(
    "user_123",
    Path("data/transcripts/meeting_2024_11_07.txt")
))
```

## Data Format

### Transcript Object

```python
class TranscriptMetadata:
    user_id: str                    # Required: User who owns this transcript
    meeting_title: str              # Required: Title/name of the meeting
    meeting_date: str | None        # Optional: ISO date (YYYY-MM-DD)
    participants: list[str]         # Optional: List of participant names
    tags: list[str]                 # Optional: Tags for categorization
    file_size_bytes: int            # File size in bytes
    source_format: str              # Format: "txt", "pdf", "docx", etc.
    uploaded_at: datetime           # Auto-generated timestamp
    transcript_id: str              # Auto-generated UUID

class Transcript:
    metadata: TranscriptMetadata    # Metadata about the transcript
    content: str                    # The actual transcript text
```

### Supported Formats

The system can process:
- **Text files** (.txt) - Plain text transcripts
- **PDF files** (.pdf) - Via Ragbits document parsers
- **Word documents** (.docx) - Via Ragbits document parsers
- **JSON files** (.json) - Structured transcript data

## Best Practices

### 1. User Isolation

Always provide a unique `user_id` for each user:

```python
# Good - Each user has their own service
service_alice = TranscriptServiceFactory.get_service("alice_123")
service_bob = TranscriptServiceFactory.get_service("bob_456")

# Bad - Don't share services across users
service = TranscriptServiceFactory.get_service("shared")  # ❌
```

### 2. Meaningful Metadata

Provide rich metadata for better searchability:

```python
# Good
metadata = TranscriptMetadata(
    user_id="user_123",
    meeting_title="Q4 Planning - Engineering Team",
    meeting_date="2024-11-07",
    participants=["Sarah (PM)", "Mike (Tech Lead)", "Alice (Dev)"],
    tags=["planning", "engineering", "Q4", "roadmap"],
    file_size_bytes=len(content.encode()),
    source_format="txt"
)

# Minimal (still works)
metadata = TranscriptMetadata(
    user_id="user_123",
    meeting_title="Meeting",
    file_size_bytes=len(content.encode()),
    source_format="txt"
)
```

### 3. Error Handling

Always handle potential errors:

```python
async def safe_ingest(user_id: str, content: str, title: str):
    try:
        service = TranscriptServiceFactory.get_service(user_id)
        metadata = TranscriptMetadata(
            user_id=user_id,
            meeting_title=title,
            file_size_bytes=len(content.encode()),
            source_format="txt"
        )
        transcript = Transcript(metadata=metadata, content=content)
        transcript_id = await service.ingest_transcript(transcript)
        return {"success": True, "transcript_id": transcript_id}
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        return {"success": False, "error": str(e)}
```

### 4. Chunking Considerations

- The system automatically chunks transcripts for optimal retrieval
- Default chunk size: 500 characters
- Adjust in `.env` via `CHUNK_SIZE` if needed
- Smaller chunks = more precise but more API calls
- Larger chunks = more context but less precise

### 5. Performance Tips

For large batches:

```python
# Process in parallel (be careful with rate limits)
async def ingest_parallel(user_id: str, transcripts: list):
    tasks = [
        ingest_one_transcript(user_id, t)
        for t in transcripts
    ]
    return await asyncio.gather(*tasks)

# Or sequential with progress
async def ingest_with_progress(user_id: str, transcripts: list):
    for i, t in enumerate(transcripts, 1):
        transcript_id = await ingest_one_transcript(user_id, t)
        print(f"Progress: {i}/{len(transcripts)} - {transcript_id}")
```

## Troubleshooting

### "ValueError: OPENAI_API_KEY is required"

Make sure you've set your API keys in `.env`:

```bash
OPENAI_API_KEY=sk-your-key-here
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### "Module not found" errors

Install dependencies:

```bash
pip install -r requirements.txt
```

### Slow ingestion

- Check your embedding provider (OpenAI vs OpenRouter)
- Consider using a faster embedding model
- Use batch processing for multiple transcripts

### Memory issues with large files

For very large transcripts:
1. Split into multiple smaller transcripts
2. Use streaming if available
3. Increase chunk size to reduce number of chunks

## Next Steps

After ingesting transcripts:

1. **Search**: Use `service.search_transcripts(query, k=5)`
2. **Chat**: Use the chatbot to ask questions
3. **API**: Access via `/chat` WebSocket endpoint
4. **Mobile**: Integrate with your mobile app using the REST API

## Examples

See the `examples/` directory:
- `ingest_transcript.py` - Basic ingestion
- `simple_chat_example.py` - Ingest + chat
- `api_client_example.py` - Full API workflow

## Support

For more information:
- See `README.md` for full documentation
- Check `QUICKSTART.md` for setup instructions
- Review `ARCHITECTURE.md` for system design
