# Transcript Chatbot - Production RAG System

A production-ready chatbot system built with [Ragbits](https://ragbits.deepsense.ai/) for analyzing meeting transcripts. Users can upload their meeting transcripts and ask questions about them using natural language.

## Features

✨ **Core Capabilities**
- 📝 Upload and index meeting transcripts
- 🔍 RAG-powered question answering
- 💬 Conversation history tracking
- 👥 User-specific data isolation
- 🔐 JWT-based authentication
- 📊 Structured logging and monitoring

🚀 **Production-Ready**
- Multiple vector store backends (In-Memory, Qdrant, PostgreSQL)
- Streaming responses for better UX
- Comprehensive error handling
- Environment-based configuration
- Docker support
- OpenTelemetry observability (optional)

## Architecture

```
┌─────────────┐
│ Mobile App  │
└──────┬──────┘
       │ HTTPS/WebSocket
       ▼
┌─────────────────────────┐
│   FastAPI Backend       │
│   - Authentication      │
│   - Transcript Upload   │
│   - Ragbits Chat API    │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  Transcript Chatbot     │
│  - RAG Pipeline         │
│  - LLM (OpenAI)         │
│  - Document Search      │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│   Vector Store          │
│   - Qdrant/PgVector     │
│   - Embeddings          │
└─────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.10+
- OpenAI API key
- (Optional) Qdrant or PostgreSQL for production vector storage

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ragbit-test
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

5. **Run the server**
   ```bash
   python run_server.py
   ```

The API will be available at `http://localhost:8000`

### Quick Test

Run the simple example to test the system:

```bash
python examples/simple_chat_example.py
```

## Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Required
OPENAI_API_KEY=your-key-here

# LLM Settings
LLM_MODEL_NAME=gpt-4o-mini
LLM_TEMPERATURE=0.7

# Vector Store (choose one)
VECTOR_STORE_TYPE=in_memory  # or: qdrant, pgvector

# For Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=transcripts

# Authentication
JWT_SECRET_KEY=your-secret-key-here
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

See `.env.example` for all available options.

### Vector Store Options

#### 1. In-Memory (Development)
```bash
VECTOR_STORE_TYPE=in_memory
```
- ✅ No setup required
- ✅ Fast for development
- ❌ Data lost on restart
- ❌ Not suitable for production

#### 2. Qdrant (Recommended for Production)
```bash
VECTOR_STORE_TYPE=qdrant
QDRANT_URL=http://localhost:6333
```

Install Qdrant:
```bash
docker run -p 6333:6333 qdrant/qdrant
```

#### 3. PostgreSQL with pgvector
```bash
VECTOR_STORE_TYPE=pgvector
POSTGRES_HOST=localhost
POSTGRES_DB=transcripts_db
```

Setup PostgreSQL with pgvector extension.

## Usage

### API Endpoints

#### Authentication

**Register**
```bash
POST /auth/register
{
  "email": "user@example.com",
  "username": "user",
  "password": "secure_password"
}
```

**Login**
```bash
POST /auth/login
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

Response:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

#### Transcript Management

**Upload Transcript**
```bash
POST /transcripts/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <transcript.txt>
meeting_title: "Q4 Planning"
participants: "Alice, Bob"
tags: "planning, q4"
```

#### Chat Interface

The chat interface uses the Ragbits Chat API with WebSocket support:

```
ws://localhost:8000/chat/ws
```

See `examples/api_client_example.py` for usage details.

### Python SDK Usage

```python
from src.transcript_chatbot.chatbot import TranscriptChatbot
from src.transcript_chatbot.models import Transcript, TranscriptMetadata
from src.transcript_chatbot.transcript_service import TranscriptServiceFactory

# Create transcript
transcript = Transcript(
    metadata=TranscriptMetadata(
        user_id="user123",
        meeting_title="Team Standup",
        participants=["Alice", "Bob"],
    ),
    content="Meeting content here...",
)

# Ingest transcript
service = TranscriptServiceFactory.get_service("user123")
await service.ingest_transcript(transcript)

# Chat with transcript
chatbot = TranscriptChatbot(user_id="user123")
response = await chatbot.chat("What were the action items?")
print(response)
```

## Production Deployment

### Using Docker

1. **Build the image**
   ```bash
   docker build -t transcript-chatbot .
   ```

2. **Run with docker-compose**
   ```bash
   docker-compose up -d
   ```

This starts:
- Transcript Chatbot API
- Qdrant vector store
- (Optional) PostgreSQL database

### Environment Setup

For production:

1. **Set secure secrets**
   ```bash
   # Generate secure JWT secret
   openssl rand -hex 32
   ```

2. **Configure production vector store**
   - Use Qdrant or PostgreSQL (not in-memory)
   - Set up proper backup strategy

3. **Enable observability**
   ```bash
   ENABLE_TRACING=true
   OTEL_ENDPOINT=http://your-otel-collector:4318
   ```

4. **Set up reverse proxy**
   - Use nginx/caddy for SSL termination
   - Enable rate limiting
   - Configure CORS properly

### Scaling Considerations

- **Horizontal scaling**: The API is stateless and can be scaled horizontally
- **Vector store**: Use managed Qdrant Cloud or properly configured PostgreSQL
- **Caching**: Implement Redis for session/conversation caching
- **Load balancing**: Use nginx/HAProxy for load balancing

## Project Structure

```
ragbit-test/
├── config/
│   ├── __init__.py
│   └── settings.py           # Configuration management
├── src/
│   └── transcript_chatbot/
│       ├── __init__.py
│       ├── api.py            # FastAPI application
│       ├── auth.py           # Authentication logic
│       ├── chatbot.py        # Main chatbot implementation
│       ├── chat_interface.py # Ragbits Chat interface
│       ├── logger.py         # Logging configuration
│       ├── models.py         # Data models
│       ├── prompts.py        # LLM prompts
│       ├── transcript_service.py  # Transcript management
│       └── vector_store_factory.py # Vector store creation
├── examples/
│   ├── simple_chat_example.py
│   └── api_client_example.py
├── tests/                    # Unit tests (TODO)
├── logs/                     # Application logs
├── data/                     # Upload directory
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
├── run_server.py           # Server entry point
├── docker-compose.yml      # Docker orchestration
└── README.md               # This file
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black src/

# Lint
ruff check src/
```

### Adding Custom Prompts

Edit `src/transcript_chatbot/prompts.py` to customize how the chatbot responds.

## Monitoring and Observability

### Logs

Logs are written to:
- Console (stdout)
- File: `logs/transcript_chatbot.log`

Format: JSON (configurable)

### OpenTelemetry (Optional)

Enable tracing:
```bash
ENABLE_TRACING=true
OTEL_ENDPOINT=http://localhost:4318
```

Traces include:
- LLM calls
- Vector store queries
- API requests

## Security

### Best Practices Implemented

- ✅ JWT-based authentication
- ✅ Password hashing (bcrypt)
- ✅ User data isolation
- ✅ Environment-based secrets
- ✅ CORS configuration
- ✅ Request validation

### Additional Recommendations

- Use HTTPS in production
- Implement rate limiting
- Add input sanitization
- Regular security audits
- Keep dependencies updated

## Troubleshooting

### Common Issues

**"No OpenAI API key found"**
```bash
# Set in .env file
OPENAI_API_KEY=sk-...
```

**"Vector store connection failed"**
```bash
# For Qdrant, ensure it's running:
docker ps | grep qdrant

# Start Qdrant:
docker run -p 6333:6333 qdrant/qdrant
```

**"Import error for ragbits"**
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt
```

## Performance Optimization

### Tips for Production

1. **Chunk Size Tuning**
   ```bash
   CHUNK_SIZE=500  # Adjust based on your transcripts
   CHUNK_OVERLAP=50
   ```

2. **Search Parameters**
   ```bash
   SEARCH_K=5  # Number of chunks to retrieve
   SEARCH_SCORE_THRESHOLD=0.7  # Minimum relevance
   ```

3. **LLM Configuration**
   ```bash
   LLM_MODEL_NAME=gpt-4o-mini  # Fast and cost-effective
   LLM_MAX_TOKENS=2000  # Adjust based on needs
   ```

## Roadmap

- [ ] Add support for video transcript formats (VTT, SRT)
- [ ] Implement conversation persistence (database)
- [ ] Add transcript summarization on upload
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Bulk transcript upload
- [ ] Export chat history

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [Create an issue]
- Documentation: https://ragbits.deepsense.ai/
- Email: support@example.com

## Acknowledgments

Built with:
- [Ragbits](https://ragbits.deepsense.ai/) - RAG framework
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [OpenAI](https://openai.com/) - LLM provider
- [Qdrant](https://qdrant.tech/) - Vector database

---

Made with ❤️ for better meeting insights
