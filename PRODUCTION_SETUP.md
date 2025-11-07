# Production Setup Guide

This system is configured for **production use with Qdrant vector database**.

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# 1. Set your API keys in .env
cp .env.example .env
nano .env  # Add your OPENAI_API_KEY and OPENROUTER_API_KEY

# 2. Start everything (Qdrant + API)
docker-compose up -d

# 3. Check status
docker-compose ps

# 4. View logs
docker-compose logs -f api
```

Your API will be at: `http://localhost:8000`
Qdrant dashboard at: `http://localhost:6333/dashboard`

### Option 2: Local Development with Qdrant

```bash
# 1. Start Qdrant
docker run -d -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant:latest

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure .env
cp .env.example .env
nano .env  # Set VECTOR_STORE_TYPE=qdrant

# 4. Run the API
python run_server.py
```

## Production Configuration

Your `.env` should have:

```bash
# PRODUCTION SETTINGS
ENVIRONMENT=production
VECTOR_STORE_TYPE=qdrant

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=transcripts

# API Keys
OPENAI_API_KEY=sk-your-real-key
OPENROUTER_API_KEY=sk-or-v1-your-real-key

# Security
JWT_SECRET_KEY=use-openssl-rand-hex-32-to-generate-this
```

## Verify Qdrant is Running

```bash
# Check Qdrant health
curl http://localhost:6333/health

# View collections
curl http://localhost:6333/collections

# Or use the web UI
open http://localhost:6333/dashboard
```

## Data Persistence

### Qdrant Data
- **Docker Compose**: Data stored in `qdrant_data` Docker volume
- **Local**: Data stored in `./qdrant_storage/` directory

### To Backup Qdrant

```bash
# Create snapshot
curl -X POST http://localhost:6333/collections/transcripts/snapshots

# Download snapshot
curl http://localhost:6333/collections/transcripts/snapshots/<snapshot-name> \
  --output backup.snapshot
```

### To Restore

```bash
curl -X PUT http://localhost:6333/collections/transcripts/snapshots/upload \
  -F file=@backup.snapshot
```

## Production Checklist

- [ ] Qdrant is running and accessible
- [ ] Set strong `JWT_SECRET_KEY` (use `openssl rand -hex 32`)
- [ ] Configure proper CORS origins (not `*`)
- [ ] Enable HTTPS/TLS in production
- [ ] Set up backup schedule for Qdrant
- [ ] Configure monitoring and alerts
- [ ] Set appropriate rate limits
- [ ] Use environment variables (not hardcoded secrets)
- [ ] Enable proper logging
- [ ] Set up database backups

## Scaling

### Horizontal Scaling (API)

```bash
# Scale API servers
docker-compose up -d --scale api=3

# Use nginx/load balancer in front
```

### Qdrant Cluster

For high availability, use Qdrant Cloud or set up a cluster:
- https://qdrant.tech/documentation/cloud/

## Monitoring

### View Records

```bash
python scripts/view_records.py
```

### Check Qdrant Stats

```bash
curl http://localhost:6333/collections/transcripts
```

### API Health

```bash
curl http://localhost:8000/health
```

## Troubleshooting

### "Cannot connect to Qdrant"

```bash
# Check if Qdrant is running
docker ps | grep qdrant

# Check Qdrant logs
docker logs transcript-qdrant

# Restart Qdrant
docker-compose restart qdrant
```

### "Collection not found"

The collection is created automatically on first upload. If needed:

```bash
curl -X PUT http://localhost:6333/collections/transcripts \
  -H 'Content-Type: application/json' \
  -d '{
    "vectors": {
      "size": 1536,
      "distance": "Cosine"
    }
  }'
```

## NOT for Production

**DO NOT USE** `VECTOR_STORE_TYPE=in_memory` in production!
- Data is lost on restart
- No persistence
- No scalability
- Only for local testing

## Support

- Qdrant Docs: https://qdrant.tech/documentation/
- Ragbits Docs: https://ragbits.deepsense.ai/
- Issues: Check logs in `./logs/` directory
