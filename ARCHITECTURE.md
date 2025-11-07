# System Architecture

## Overview

The Transcript Chatbot is a production-ready RAG (Retrieval-Augmented Generation) system built with Ragbits. It enables users to upload meeting transcripts and interact with them through natural language conversations.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Mobile App                               │
│                    (iOS/Android Client)                          │
└────────────┬────────────────────────────────────────────────────┘
             │ HTTPS/WebSocket
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway / Load Balancer                 │
│                        (nginx/HAProxy)                           │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Application                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Authentication Middleware                    │  │
│  │  - JWT validation                                        │  │
│  │  - User context injection                                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────┐  ┌─────────────────────────────────┐    │
│  │  Auth Endpoints  │  │   Transcript Endpoints           │    │
│  │  /auth/register  │  │   /transcripts/upload            │    │
│  │  /auth/login     │  │   /transcripts/{id}              │    │
│  └──────────────────┘  └─────────────────────────────────┘    │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │            Ragbits Chat API (/chat/*)                     │  │
│  │  - WebSocket connections                                  │  │
│  │  - Streaming responses                                    │  │
│  │  - Conversation management                                │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────┬──────────────────────────┬──────────────────────────┘
             │                          │
             ▼                          ▼
┌─────────────────────────┐  ┌─────────────────────────────────┐
│  TranscriptChatInterface │  │   TranscriptService             │
│  - Chat orchestration    │  │   - Transcript ingestion        │
│  - Response streaming    │  │   - User data isolation         │
│  - Live updates          │  │   - Vector store management     │
└────────────┬─────────────┘  └──────────────┬──────────────────┘
             │                               │
             ▼                               │
┌─────────────────────────┐                 │
│   TranscriptChatbot     │◄────────────────┘
│  ┌──────────────────┐   │
│  │  RAG Pipeline    │   │
│  │  - Query         │   │
│  │  - Retrieve      │   │
│  │  - Generate      │   │
│  └──────────────────┘   │
└────────────┬─────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌──────────┐   ┌─────────────────┐
│   LLM    │   │ DocumentSearch  │
│ (OpenAI) │   │  - Chunking     │
│          │   │  - Embedding    │
│          │   │  - Retrieval    │
└──────────┘   └────────┬────────┘
                        │
                        ▼
              ┌──────────────────┐
              │  Vector Store     │
              │  ┌─────────────┐ │
              │  │  Qdrant     │ │
              │  │  or         │ │
              │  │  PgVector   │ │
              │  └─────────────┘ │
              └──────────────────┘
```

## Component Details

### 1. API Layer

**FastAPI Application** (`src/transcript_chatbot/api.py`)
- RESTful API endpoints
- Authentication middleware
- Request validation
- Error handling
- CORS configuration

**Key Endpoints:**
- `POST /auth/register` - User registration
- `POST /auth/login` - User authentication
- `POST /transcripts/upload` - Transcript upload
- `GET /transcripts/{id}` - Retrieve transcript
- `WS /chat/ws` - Chat WebSocket (via Ragbits)

### 2. Authentication Layer

**Auth Module** (`src/transcript_chatbot/auth.py`)
- JWT-based authentication
- Password hashing (bcrypt)
- Token generation and validation
- User management

**Security Features:**
- Secure password hashing
- Token expiration
- User data isolation
- Bearer token authentication

### 3. Chat Interface Layer

**TranscriptChatInterface** (`src/transcript_chatbot/chat_interface.py`)
- Implements Ragbits `ChatInterface`
- Manages conversation flow
- Handles streaming responses
- Provides live updates to UI

**Key Features:**
- User context injection
- Conversation history management
- Live update events (searching, answering)
- Error handling

### 4. Chatbot Core

**TranscriptChatbot** (`src/transcript_chatbot/chatbot.py`)
- Main RAG implementation
- Conversation state management
- Query processing
- Response generation

**RAG Pipeline:**
1. **Retrieve**: Search vector store for relevant chunks
2. **Augment**: Add context to prompt
3. **Generate**: Call LLM with augmented prompt

**Features:**
- Streaming and non-streaming modes
- Conversation history tracking
- Multi-transcript support
- User-specific isolation

### 5. Transcript Service Layer

**TranscriptService** (`src/transcript_chatbot/transcript_service.py`)
- Transcript ingestion
- Vector store management
- User data isolation
- Metadata handling

**Data Flow:**
```
Upload → Parse → Chunk → Embed → Store
           ↓
      Metadata
```

### 6. Vector Store Layer

**VectorStoreFactory** (`src/transcript_chatbot/vector_store_factory.py`)
- Creates vector store instances
- Supports multiple backends
- Configuration-based setup

**Supported Stores:**
- **InMemory**: Development/testing
- **Qdrant**: Production (recommended)
- **PgVector**: PostgreSQL-based alternative

### 7. LLM Layer

**Integration:**
- Uses Ragbits LiteLLM
- Supports 100+ models via LiteLLM
- Configurable via environment

**Models:**
- Default: `gpt-4o-mini` (cost-effective)
- Alternative: `gpt-4o` (higher quality)
- Custom: Any LiteLLM-supported model

### 8. Prompt Layer

**Prompts** (`src/transcript_chatbot/prompts.py`)
- Structured prompt templates
- Type-safe inputs/outputs
- Jinja2 templating

**Prompt Types:**
- `TranscriptQuestionPrompt`: Simple Q&A
- `ChatWithHistoryPrompt`: Conversational Q&A
- `TranscriptSummaryPrompt`: Transcript summarization

## Data Models

### User Model
```python
User:
  - id: str
  - email: str
  - username: str
  - created_at: datetime
```

### Transcript Model
```python
Transcript:
  - metadata: TranscriptMetadata
    - transcript_id: str
    - user_id: str
    - meeting_title: str
    - participants: list[str]
    - tags: list[str]
  - content: str
  - summary: str (optional)
```

### Conversation Model
```python
ConversationContext:
  - user_id: str
  - transcript_ids: list[str]
  - conversation_id: str
  - messages: list[ChatMessage]
```

## Data Flow

### 1. Transcript Upload Flow

```
Mobile App
  │
  │ POST /transcripts/upload
  │ (file, metadata)
  ▼
FastAPI
  │
  │ 1. Authenticate user (JWT)
  │ 2. Validate file
  ▼
TranscriptService
  │
  │ 1. Create Transcript object
  │ 2. Add user_id to metadata
  ▼
DocumentSearch
  │
  │ 1. Parse content
  │ 2. Chunk text
  │ 3. Generate embeddings
  ▼
Vector Store
  │
  │ Store chunks with metadata
  │ {user_id, transcript_id, ...}
  ▼
Response
  │
  └─► {transcript_id, message}
```

### 2. Chat Flow

```
Mobile App
  │
  │ WebSocket /chat/ws
  │ {message, context}
  ▼
TranscriptChatInterface
  │
  │ 1. Extract user_id
  │ 2. Get/create conversation
  ▼
TranscriptChatbot
  │
  ├─► TranscriptService
  │     │
  │     │ Search vector store
  │     │ Filter: user_id = current_user
  │     │
  │     └─► Relevant chunks
  │
  ├─► Build prompt
  │    │
  │    ├─ Question
  │    ├─ Context (chunks)
  │    └─ History (optional)
  │
  └─► LLM
       │
       │ Generate response
       │
       └─► Stream chunks
            │
            ▼
         Mobile App
```

## User Data Isolation

Every operation is scoped to the authenticated user:

1. **Upload**: `transcript.metadata.user_id = current_user.id`
2. **Search**: `filter = {user_id: current_user.id}`
3. **Chat**: Only searches user's transcripts

This ensures:
- Users only see their own data
- No cross-user information leakage
- Secure multi-tenancy

## Scaling Considerations

### Horizontal Scaling

**Stateless Design:**
- API servers are stateless
- Can scale horizontally
- Load balancer distributes traffic

**Scaling Strategy:**
```
1-100 users:    1 API server + 1 Qdrant instance
100-1000 users: 3-5 API servers + Qdrant cluster
1000+ users:    10+ API servers + Qdrant Cloud
```

### Vertical Scaling

**Resource Requirements:**

| Component | CPU | Memory | Storage |
|-----------|-----|--------|---------|
| API Server | 2-4 cores | 4-8 GB | Minimal |
| Qdrant | 4-8 cores | 8-16 GB | Depends on data |
| Total (small) | 4 cores | 8 GB | 10 GB |
| Total (medium) | 8 cores | 16 GB | 50 GB |
| Total (large) | 16+ cores | 32+ GB | 200+ GB |

### Caching Strategy

**Future Enhancement:**
```python
# Add Redis for caching
- User sessions
- Frequent queries
- Conversation state
- Embedding cache
```

## Security Architecture

### Authentication Flow

```
1. User Registration
   └─► Password hashed with bcrypt
       └─► User stored

2. User Login
   └─► Verify password hash
       └─► Generate JWT token
           └─► Return token

3. API Request
   └─► Extract Bearer token
       └─► Verify JWT
           └─► Extract user_id
               └─► Proceed with request
```

### Data Security

- **In Transit**: HTTPS/TLS
- **At Rest**: Vector store encryption (if supported)
- **Passwords**: Bcrypt hashing
- **Tokens**: JWT with expiration
- **Isolation**: User-scoped queries

## Monitoring & Observability

### Logging

**Levels:**
- DEBUG: Development details
- INFO: Normal operations
- WARNING: Potential issues
- ERROR: Failures

**Structured Logging:**
```json
{
  "timestamp": "2024-11-07T10:30:00Z",
  "level": "INFO",
  "message": "Transcript uploaded",
  "user_id": "user123",
  "transcript_id": "trans456"
}
```

### Metrics (Optional)

With OpenTelemetry:
- Request latency
- Token usage
- Vector store query time
- Error rates

### Tracing (Optional)

Distributed tracing shows:
1. API request received
2. Vector store search
3. LLM call
4. Response generation

## Performance Optimization

### Current Optimizations

1. **Streaming Responses**: Better UX, lower perceived latency
2. **Async I/O**: Non-blocking operations
3. **Configurable Chunk Size**: Balance precision vs. cost
4. **Vector Store Indexing**: Fast similarity search

### Future Optimizations

1. **Response Caching**: Cache common queries
2. **Embedding Cache**: Reuse embeddings
3. **Batch Processing**: Upload multiple transcripts
4. **Connection Pooling**: Database connections

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Web Framework** | FastAPI |
| **LLM Integration** | Ragbits + LiteLLM |
| **Vector Store** | Qdrant / PgVector |
| **Embeddings** | OpenAI text-embedding-3-small |
| **LLM** | OpenAI GPT-4o-mini |
| **Authentication** | JWT + Passlib |
| **Logging** | Python logging + JSON formatter |
| **Deployment** | Docker / Kubernetes |

## Configuration

Centralized in `config/settings.py`:

- **Environment-based**: Dev, staging, production
- **Type-safe**: Pydantic models
- **Validation**: Automatic validation
- **Defaults**: Sensible defaults provided

## Future Enhancements

### Planned Features

1. **Conversation Persistence**
   - Store conversations in database
   - Resume previous chats

2. **Multi-format Support**
   - PDF transcripts
   - Audio transcription
   - Video captions (VTT, SRT)

3. **Analytics Dashboard**
   - Usage statistics
   - Popular queries
   - System health

4. **Advanced Features**
   - Multi-transcript search
   - Transcript comparison
   - Action item extraction
   - Meeting insights

### Scalability Roadmap

1. **Phase 1** (Current): Single-server deployment
2. **Phase 2**: Horizontal scaling with load balancer
3. **Phase 3**: Kubernetes deployment
4. **Phase 4**: Multi-region deployment

---

**Document Version**: 1.0
**Last Updated**: November 2024
