# Quick Start Guide

Get the Transcript Chatbot running in 5 minutes!

## 🚀 1-Minute Setup

```bash
# 1. Clone and enter directory
git clone <your-repo>
cd ragbit-test

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure (add your OpenAI API key)
cp .env.example .env
nano .env  # or use your favorite editor

# 5. Run!
python run_server.py
```

Visit http://localhost:8000 🎉

## 📝 Test It Out

### Option 1: Run the Example Script

```bash
python examples/simple_chat_example.py
```

This will:
1. Upload a sample transcript
2. Ask several questions
3. Show you how it works

### Option 2: Use the API

1. **Register a user**
   ```bash
   curl -X POST http://localhost:8000/auth/register \
     -H "Content-Type: application/json" \
     -d '{
       "email": "demo@test.com",
       "username": "demo",
       "password": "demo123"
     }'
   ```

2. **Login and get token**
   ```bash
   TOKEN=$(curl -X POST http://localhost:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "demo@test.com", "password": "demo123"}' \
     | jq -r '.access_token')
   ```

3. **Upload a transcript**
   ```bash
   echo "Team meeting on Nov 5. Alice said we need to ship feature X by Friday. Bob will handle the backend." > meeting.txt

   curl -X POST http://localhost:8000/transcripts/upload \
     -H "Authorization: Bearer $TOKEN" \
     -F "file=@meeting.txt" \
     -F "meeting_title=Team Standup"
   ```

4. **Chat with it** (use the WebSocket endpoint - see docs)

## 🐳 Docker Version

```bash
# Start everything with one command
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api
```

## ⚙️ Essential Configuration

In your `.env` file, you can choose between OpenAI or OpenRouter:

### Option 1: OpenRouter (Recommended - Free Models Available!)

```bash
# Provider
LLM_PROVIDER=openrouter
EMBEDDING_PROVIDER=openai

# API Keys
OPENROUTER_API_KEY=sk-or-v1-your-key-here  # Get from https://openrouter.ai/keys
OPENAI_API_KEY=sk-your-openai-key  # For embeddings

# Model (Free tier!)
LLM_MODEL_NAME=openrouter/meta-llama/llama-3.1-8b-instruct:free

# Security
JWT_SECRET_KEY=your-secret-key-here

# Optional (defaults work fine for testing)
VECTOR_STORE_TYPE=in_memory
```

### Option 2: Pure OpenAI (Original)

```bash
# Provider
LLM_PROVIDER=openai
EMBEDDING_PROVIDER=openai

# API Key
OPENAI_API_KEY=sk-your-key-here

# Model
LLM_MODEL_NAME=gpt-4o-mini

# Security
JWT_SECRET_KEY=your-secret-key-here
```

**💡 Tip**: OpenRouter gives you access to 500+ models including free ones! See [OPENROUTER.md](OPENROUTER.md) for details.

## 🎯 What's Next?

- **Production Setup**: Read [DEPLOYMENT.md](DEPLOYMENT.md)
- **Full Documentation**: See [README.md](README.md)
- **API Reference**: Visit http://localhost:8000/docs
- **Customize Prompts**: Edit `src/transcript_chatbot/prompts.py`

## 🆘 Troubleshooting

**"No module named 'ragbits'"**
```bash
pip install -r requirements.txt
```

**"OpenAI API key not found"**
```bash
# Make sure .env has:
OPENAI_API_KEY=sk-...
```

**"Port 8000 already in use"**
```bash
# Change port in .env:
API_PORT=8001
```

**Still stuck?**
- Check logs in `logs/transcript_chatbot.log`
- Ensure Python 3.10+ is installed
- Make sure you activated the virtual environment

## 📱 Mobile App Integration

Your mobile app should:

1. **Register/Login users** → Get JWT token
2. **Upload transcripts** → POST to `/transcripts/upload`
3. **Chat via WebSocket** → Connect to `ws://your-server/chat/ws`

See `examples/api_client_example.py` for details.

---

That's it! You're ready to go. Happy chatting! 🤖💬
