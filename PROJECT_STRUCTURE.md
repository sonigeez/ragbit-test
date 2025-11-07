# Project Structure

```
ragbit-test/
│
├── README.md                    # Main documentation
├── QUICKSTART.md               # Quick start guide
├── DEPLOYMENT.md               # Deployment guide
├── ARCHITECTURE.md             # System architecture
├── PROJECT_STRUCTURE.md        # This file
│
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
├── .dockerignore              # Docker ignore rules
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker image definition
├── docker-compose.yml         # Docker orchestration
├── run_server.py              # Server entry point
│
├── config/                     # Configuration
│   ├── __init__.py
│   └── settings.py            # Application settings
│
├── src/                        # Source code
│   └── transcript_chatbot/
│       ├── __init__.py
│       ├── api.py             # FastAPI application
│       ├── auth.py            # Authentication
│       ├── chatbot.py         # Main chatbot logic
│       ├── chat_interface.py  # Ragbits Chat interface
│       ├── logger.py          # Logging configuration
│       ├── models.py          # Data models
│       ├── prompts.py         # LLM prompts
│       ├── transcript_service.py      # Transcript management
│       └── vector_store_factory.py    # Vector store creation
│
├── examples/                   # Example scripts
│   ├── simple_chat_example.py # Simple usage example
│   └── api_client_example.py  # API client example
│
├── tests/                      # Unit tests (TODO)
│   └── (test files here)
│
├── logs/                       # Application logs
│   └── transcript_chatbot.log
│
└── data/                       # Upload directory
    └── uploads/
```

## File Descriptions

### Root Level Files

| File | Description |
|------|-------------|
| `README.md` | Complete project documentation |
| `QUICKSTART.md` | 5-minute quick start guide |
| `DEPLOYMENT.md` | Production deployment guide |
| `ARCHITECTURE.md` | System architecture details |
| `.env.example` | Environment variable template |
| `requirements.txt` | Python package dependencies |
| `Dockerfile` | Container image definition |
| `docker-compose.yml` | Multi-container orchestration |
| `run_server.py` | Application entry point |

### Configuration (`config/`)

| File | Description |
|------|-------------|
| `settings.py` | Centralized configuration with environment variable support |

**Features:**
- Pydantic-based validation
- Environment-specific settings
- Secure defaults
- Type hints

### Source Code (`src/transcript_chatbot/`)

| File | Description | Key Classes/Functions |
|------|-------------|---------------------|
| `api.py` | FastAPI application | `app`, endpoints |
| `auth.py` | Authentication & JWT | `create_access_token`, `get_current_user` |
| `chatbot.py` | Main chatbot implementation | `TranscriptChatbot` |
| `chat_interface.py` | Ragbits Chat integration | `TranscriptChatInterface` |
| `logger.py` | Logging setup | `setup_logging`, `JSONFormatter` |
| `models.py` | Data models | `User`, `Transcript`, `ConversationContext` |
| `prompts.py` | LLM prompt templates | `TranscriptQuestionPrompt`, etc. |
| `transcript_service.py` | Transcript CRUD | `TranscriptService` |
| `vector_store_factory.py` | Vector store creation | `create_vector_store` |

### Examples (`examples/`)

| File | Description |
|------|-------------|
| `simple_chat_example.py` | Standalone chatbot demo without API |
| `api_client_example.py` | API client usage example |

### Tests (`tests/`)

Directory for unit and integration tests (to be implemented).

Suggested structure:
```
tests/
├── test_api.py
├── test_auth.py
├── test_chatbot.py
├── test_transcript_service.py
└── conftest.py
```

## Module Dependencies

```
api.py
  ├─► auth.py (authentication)
  ├─► chat_interface.py (chat handling)
  ├─► transcript_service.py (transcript mgmt)
  └─► models.py (data models)

chat_interface.py
  └─► chatbot.py (RAG logic)

chatbot.py
  ├─► transcript_service.py (search)
  ├─► prompts.py (prompt templates)
  └─► models.py (data models)

transcript_service.py
  ├─► vector_store_factory.py (vector store)
  └─► models.py (data models)

vector_store_factory.py
  └─► settings.py (configuration)

All modules
  └─► logger.py (logging)
      └─► settings.py (configuration)
```

## Key Design Patterns

### 1. Factory Pattern
- `TranscriptServiceFactory`: Creates service instances per user
- `create_vector_store()`: Creates appropriate vector store

### 2. Dependency Injection
- Settings injected via `config.settings`
- LLM and vector store injected into services

### 3. Service Layer Pattern
- `TranscriptService`: Business logic for transcripts
- `TranscriptChatbot`: Business logic for chat

### 4. Repository Pattern
- Vector store abstracts storage implementation
- Easy to swap backends (In-Memory → Qdrant → PgVector)

## Adding New Features

### 1. Add a New API Endpoint

Edit `src/transcript_chatbot/api.py`:
```python
@app.get("/my-endpoint")
async def my_endpoint(user_id: str = Depends(get_current_user)):
    # Implementation
    pass
```

### 2. Add a New Prompt

Edit `src/transcript_chatbot/prompts.py`:
```python
class MyPrompt(Prompt[MyInput, MyOutput]):
    system_prompt = "..."
    user_prompt = "..."
```

### 3. Add New Configuration

Edit `config/settings.py`:
```python
class Settings(BaseSettings):
    new_setting: str = "default"
```

### 4. Add New Data Model

Edit `src/transcript_chatbot/models.py`:
```python
class MyModel(BaseModel):
    field1: str
    field2: int
```

## Environment Variables

All configuration is managed through environment variables.

**Priority:**
1. Environment variables (highest)
2. `.env` file
3. Default values in `settings.py` (lowest)

**Example:**
```bash
# Set in .env
LLM_MODEL_NAME=gpt-4o

# Or export in shell
export LLM_MODEL_NAME=gpt-4o

# Or in docker-compose.yml
environment:
  - LLM_MODEL_NAME=gpt-4o
```

## Development Workflow

### 1. Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Development
```bash
# Run server with hot reload
python run_server.py

# Run example
python examples/simple_chat_example.py

# Run tests (when implemented)
pytest tests/
```

### 3. Code Quality
```bash
# Format
black src/

# Lint
ruff check src/

# Type check
mypy src/
```

### 4. Docker Development
```bash
# Build
docker build -t transcript-chatbot .

# Run
docker-compose up

# Logs
docker-compose logs -f api
```

## Production Deployment

See `DEPLOYMENT.md` for detailed instructions.

**Quick summary:**
1. Set production environment variables
2. Use Qdrant or PgVector (not in-memory)
3. Enable HTTPS
4. Set secure JWT secret
5. Configure logging
6. Set up monitoring

## Code Organization Principles

1. **Separation of Concerns**: Each module has a single responsibility
2. **Dependency Injection**: Dependencies passed explicitly
3. **Type Safety**: Full type hints throughout
4. **Configuration**: Centralized in `settings.py`
5. **Error Handling**: Comprehensive try/except blocks
6. **Logging**: Structured logging at all levels
7. **User Isolation**: All operations scoped to user

## Performance Considerations

### File Sizes (approximate)

| File | Lines of Code | Complexity |
|------|--------------|------------|
| `api.py` | 200 | Medium |
| `chatbot.py` | 250 | High |
| `transcript_service.py` | 150 | Medium |
| `prompts.py` | 150 | Low |
| `settings.py` | 120 | Low |

### Memory Usage

- Base application: ~100-200 MB
- Per conversation: ~10-50 MB
- Vector store: Depends on data size

### Disk Usage

- Application code: < 1 MB
- Dependencies: ~500 MB
- Logs: Grows over time (rotate recommended)
- Vector store: Grows with transcripts

## Extension Points

The system is designed for easy extension:

1. **New Vector Stores**: Implement in `vector_store_factory.py`
2. **New LLM Providers**: Configure via LiteLLM
3. **New Prompt Types**: Add to `prompts.py`
4. **New Endpoints**: Add to `api.py`
5. **Custom Authentication**: Extend `auth.py`
6. **Custom Logging**: Modify `logger.py`

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-11 | Initial production release |

---

**Last Updated**: November 2024
