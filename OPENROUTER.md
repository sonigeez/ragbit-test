# OpenRouter Integration Guide

This guide explains how to use OpenRouter with the Transcript Chatbot.

## What is OpenRouter?

OpenRouter provides unified access to 500+ AI models through a single API, including:
- Anthropic Claude models
- Meta Llama models
- Google Gemini models
- OpenAI models (if you prefer)
- And many more!

**Benefits:**
- ✅ Access to many models with one API key
- ✅ Competitive pricing
- ✅ Free tier available for testing
- ✅ Unified API interface

## Setup

### 1. Get Your OpenRouter API Key

1. Visit https://openrouter.ai/
2. Sign up for an account
3. Go to https://openrouter.ai/keys
4. Create a new API key
5. Copy your API key

### 2. Configure Your Environment

Edit your `.env` file:

```bash
# Provider Settings
LLM_PROVIDER=openrouter
EMBEDDING_PROVIDER=openai  # Keep using OpenAI for embeddings (more reliable)

# OpenRouter API Key
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Choose your model
LLM_MODEL_NAME=openrouter/meta-llama/llama-3.1-8b-instruct:free

# You still need OpenAI key for embeddings
OPENAI_API_KEY=sk-your-openai-key-here
```

## Available Models

### Popular Free Models

Perfect for testing and development:

```bash
# Llama 3.1 8B (Free)
LLM_MODEL_NAME=openrouter/meta-llama/llama-3.1-8b-instruct:free

# Llama 3.2 3B (Free)
LLM_MODEL_NAME=openrouter/meta-llama/llama-3.2-3b-instruct:free

# Gemma 2 9B (Free)
LLM_MODEL_NAME=openrouter/google/gemma-2-9b-it:free
```

### Premium Models

For production use:

```bash
# Claude 3.5 Sonnet (Best quality)
LLM_MODEL_NAME=openrouter/anthropic/claude-3.5-sonnet

# GPT-4o (OpenAI via OpenRouter)
LLM_MODEL_NAME=openrouter/openai/gpt-4o

# Llama 3.1 70B (Large, powerful)
LLM_MODEL_NAME=openrouter/meta-llama/llama-3.1-70b-instruct

# Claude 3 Opus (Highest quality)
LLM_MODEL_NAME=openrouter/anthropic/claude-3-opus
```

See all models at: https://openrouter.ai/models

## Configuration Options

### Option 1: OpenRouter for LLM + OpenAI for Embeddings (Recommended)

This is the recommended configuration because OpenRouter's embedding support is limited.

```bash
# .env
LLM_PROVIDER=openrouter
EMBEDDING_PROVIDER=openai

LLM_MODEL_NAME=openrouter/meta-llama/llama-3.1-8b-instruct:free
EMBEDDING_MODEL_NAME=text-embedding-3-small

OPENROUTER_API_KEY=your-openrouter-key
OPENAI_API_KEY=your-openai-key
```

**Pros:**
- ✅ Access to many LLM models
- ✅ Reliable embeddings from OpenAI
- ✅ Best of both worlds

**Cons:**
- ❌ Need two API keys
- ❌ Two services to manage

### Option 2: OpenRouter for Both (Experimental)

```bash
# .env
LLM_PROVIDER=openrouter
EMBEDDING_PROVIDER=openrouter

LLM_MODEL_NAME=openrouter/meta-llama/llama-3.1-8b-instruct:free
EMBEDDING_MODEL_NAME=openrouter/... # Check OpenRouter for available embedding models

OPENROUTER_API_KEY=your-openrouter-key
```

**Note:** OpenRouter's embedding support is limited. Check their documentation for available models.

### Option 3: Pure OpenAI (Original)

```bash
# .env
LLM_PROVIDER=openai
EMBEDDING_PROVIDER=openai

LLM_MODEL_NAME=gpt-4o-mini
EMBEDDING_MODEL_NAME=text-embedding-3-small

OPENAI_API_KEY=your-openai-key
```

## Quick Start Example

1. **Setup environment:**
   ```bash
   cp .env.example .env
   nano .env  # Edit and add your OPENROUTER_API_KEY
   ```

2. **Configure for OpenRouter:**
   ```bash
   LLM_PROVIDER=openrouter
   LLM_MODEL_NAME=openrouter/meta-llama/llama-3.1-8b-instruct:free
   OPENROUTER_API_KEY=sk-or-v1-your-key-here

   # Keep OpenAI for embeddings
   EMBEDDING_PROVIDER=openai
   OPENAI_API_KEY=sk-your-openai-key
   ```

3. **Run the server:**
   ```bash
   python run_server.py
   ```

4. **Test it:**
   ```bash
   python examples/simple_chat_example.py
   ```

## Model Selection Guide

### For Development/Testing
Use free models to save costs:
```bash
LLM_MODEL_NAME=openrouter/meta-llama/llama-3.1-8b-instruct:free
```

### For Production
Consider these factors:

**Need best quality?**
```bash
LLM_MODEL_NAME=openrouter/anthropic/claude-3.5-sonnet
```

**Need cost efficiency?**
```bash
LLM_MODEL_NAME=openrouter/meta-llama/llama-3.1-70b-instruct
```

**Need OpenAI compatibility?**
```bash
LLM_MODEL_NAME=openrouter/openai/gpt-4o-mini
```

**Need fast responses?**
```bash
LLM_MODEL_NAME=openrouter/meta-llama/llama-3.1-8b-instruct
```

## Pricing

OpenRouter pricing varies by model:

- **Free models**: $0 (rate limited)
- **Budget models**: ~$0.10-0.50 per million tokens
- **Premium models**: ~$3-15 per million tokens

Check current pricing at: https://openrouter.ai/models

**Cost Comparison:**

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| Llama 3.1 8B (free) | $0 | $0 |
| Llama 3.1 70B | ~$0.50 | ~$0.80 |
| Claude 3.5 Sonnet | ~$3 | ~$15 |
| GPT-4o | ~$5 | ~$15 |

## Advanced Configuration

### Custom OpenRouter Base URL

If you need to use a different endpoint:

```bash
OPENROUTER_API_BASE=https://your-custom-endpoint.com/api/v1
```

### Model-Specific Parameters

You can adjust these in `config/settings.py`:

```python
# For creative outputs
LLM_TEMPERATURE=0.9

# For factual/deterministic outputs
LLM_TEMPERATURE=0.3

# For longer responses
LLM_MAX_TOKENS=4000
```

### Environment Variables

The system automatically sets these environment variables when using OpenRouter:

```python
os.environ["OPENROUTER_API_KEY"] = settings.openrouter_api_key
os.environ["OPENROUTER_API_BASE"] = settings.openrouter_api_base
```

This allows LiteLLM to properly route requests to OpenRouter.

## Troubleshooting

### "OPENROUTER_API_KEY is required"

Make sure you've set the API key in your `.env` file:
```bash
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
```

### "Model not found"

Ensure your model name has the `openrouter/` prefix:
```bash
# Correct
LLM_MODEL_NAME=openrouter/meta-llama/llama-3.1-8b-instruct:free

# Wrong
LLM_MODEL_NAME=meta-llama/llama-3.1-8b-instruct:free
```

The system will auto-add the prefix if missing, but it's better to include it.

### Rate Limits

Free tier models have rate limits. If you hit them:
- Wait a few minutes
- Upgrade to a paid model
- Add credits to your OpenRouter account

### Embeddings Not Working

If you're having issues with embeddings:
- Switch to OpenAI for embeddings: `EMBEDDING_PROVIDER=openai`
- OpenRouter's embedding support is limited
- OpenAI embeddings are more reliable

## Testing Different Models

You can easily test different models by changing the environment variable:

```bash
# Test Llama
export LLM_MODEL_NAME=openrouter/meta-llama/llama-3.1-8b-instruct:free
python examples/simple_chat_example.py

# Test Claude
export LLM_MODEL_NAME=openrouter/anthropic/claude-3.5-sonnet
python examples/simple_chat_example.py

# Test GPT-4
export LLM_MODEL_NAME=openrouter/openai/gpt-4o
python examples/simple_chat_example.py
```

## Best Practices

1. **Use free models for development**
   - Save costs during testing
   - Switch to premium for production

2. **Keep embeddings on OpenAI**
   - More reliable
   - Better supported
   - Cost-effective

3. **Monitor usage**
   - Check OpenRouter dashboard
   - Set up billing alerts
   - Track token usage

4. **Test model quality**
   - Different models excel at different tasks
   - Run tests with your specific use case
   - Compare responses

5. **Consider latency**
   - Larger models are slower
   - 8B models: ~1-2 seconds
   - 70B models: ~3-5 seconds
   - Claude/GPT: varies by load

## Migration from OpenAI

If you're currently using pure OpenAI:

1. **Add OpenRouter key:**
   ```bash
   OPENROUTER_API_KEY=your-key
   ```

2. **Switch provider:**
   ```bash
   LLM_PROVIDER=openrouter
   ```

3. **Choose model:**
   ```bash
   # Similar quality to GPT-4o
   LLM_MODEL_NAME=openrouter/anthropic/claude-3.5-sonnet

   # Similar to GPT-3.5
   LLM_MODEL_NAME=openrouter/meta-llama/llama-3.1-8b-instruct
   ```

4. **Keep embeddings on OpenAI:**
   ```bash
   EMBEDDING_PROVIDER=openai
   ```

That's it! The system will automatically route LLM requests to OpenRouter and embedding requests to OpenAI.

## Resources

- **OpenRouter Dashboard**: https://openrouter.ai/
- **Model List**: https://openrouter.ai/models
- **API Keys**: https://openrouter.ai/keys
- **Documentation**: https://openrouter.ai/docs
- **LiteLLM Docs**: https://docs.litellm.ai/docs/providers/openrouter

## Support

Having issues? Check:
1. This documentation
2. OpenRouter documentation
3. LiteLLM documentation
4. GitHub issues

---

**Last Updated**: November 2024
