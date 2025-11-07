# Deployment Guide

This guide covers deploying the Transcript Chatbot to production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Deployment Options](#deployment-options)
- [Post-Deployment](#post-deployment)
- [Monitoring](#monitoring)
- [Scaling](#scaling)

## Prerequisites

### Required Services

1. **OpenAI API Access**
   - Sign up at https://platform.openai.com/
   - Create an API key
   - Ensure you have credits

2. **Vector Store**
   - **Option A**: Qdrant Cloud (Recommended)
     - Sign up at https://qdrant.tech/
     - Create a cluster
     - Note the URL and API key

   - **Option B**: Self-hosted Qdrant
     ```bash
     docker run -p 6333:6333 -v $(pwd)/qdrant_data:/qdrant/storage qdrant/qdrant
     ```

   - **Option C**: PostgreSQL with pgvector
     - Install PostgreSQL 15+
     - Install pgvector extension

3. **Domain & SSL** (for production)
   - Domain name
   - SSL certificate (Let's Encrypt recommended)

## Environment Setup

### 1. Clone and Configure

```bash
git clone <your-repo>
cd ragbit-test

# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

### 2. Required Environment Variables

```bash
# CRITICAL - Must be set
OPENAI_API_KEY=sk-...
JWT_SECRET_KEY=$(openssl rand -hex 32)

# Vector Store
VECTOR_STORE_TYPE=qdrant  # or pgvector
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-api-key

# Production settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

## Deployment Options

### Option 1: Docker Compose (Recommended for Small-Medium Scale)

**Pros:**
- Easy to deploy
- All services in one place
- Good for single-server deployments

**Steps:**

1. **Prepare environment**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

2. **Build and start**
   ```bash
   docker-compose up -d
   ```

3. **Verify**
   ```bash
   curl http://localhost:8000/health
   ```

4. **Setup nginx reverse proxy**
   ```nginx
   server {
       listen 80;
       server_name api.yourdomain.com;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
       }
   }
   ```

5. **Enable SSL with Certbot**
   ```bash
   sudo certbot --nginx -d api.yourdomain.com
   ```

### Option 2: Kubernetes (Recommended for Large Scale)

**Pros:**
- Highly scalable
- Auto-healing
- Rolling updates
- Production-grade

**Prerequisites:**
- Kubernetes cluster (GKE, EKS, AKS, or self-hosted)
- kubectl configured
- Helm (optional but recommended)

**Steps:**

1. **Create namespace**
   ```bash
   kubectl create namespace transcript-chatbot
   ```

2. **Create secrets**
   ```bash
   kubectl create secret generic api-secrets \
     --from-literal=openai-api-key=$OPENAI_API_KEY \
     --from-literal=jwt-secret=$JWT_SECRET_KEY \
     -n transcript-chatbot
   ```

3. **Deploy (see k8s/ directory for manifests)**
   ```bash
   kubectl apply -f k8s/
   ```

### Option 3: Cloud Platform (AWS/GCP/Azure)

#### AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.11 transcript-chatbot

# Create environment
eb create production

# Deploy
eb deploy
```

#### Google Cloud Run

```bash
# Build image
gcloud builds submit --tag gcr.io/PROJECT_ID/transcript-chatbot

# Deploy
gcloud run deploy transcript-chatbot \
  --image gcr.io/PROJECT_ID/transcript-chatbot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Azure Container Instances

```bash
# Create resource group
az group create --name transcript-rg --location eastus

# Deploy
az container create \
  --resource-group transcript-rg \
  --name transcript-chatbot \
  --image your-registry/transcript-chatbot \
  --dns-name-label transcript-api \
  --ports 8000
```

## Post-Deployment

### 1. Health Checks

```bash
# API health
curl https://api.yourdomain.com/health

# Expected response
{"status": "healthy", "environment": "production", "version": "1.0.0"}
```

### 2. Test Authentication

```bash
# Register test user
curl -X POST https://api.yourdomain.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "securepass123"
  }'
```

### 3. Test Transcript Upload

```bash
# Login
TOKEN=$(curl -X POST https://api.yourdomain.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "securepass123"}' \
  | jq -r '.access_token')

# Upload
curl -X POST https://api.yourdomain.com/transcripts/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_transcript.txt" \
  -F "meeting_title=Test Meeting"
```

### 4. Setup Backups

#### Qdrant Backups

```bash
# Create snapshot
curl -X POST "http://qdrant:6333/collections/transcripts/snapshots"

# Download snapshot
curl "http://qdrant:6333/collections/transcripts/snapshots/snapshot-name" \
  -o backup.snapshot
```

#### PostgreSQL Backups

```bash
# Daily backup cron job
0 2 * * * pg_dump transcripts_db | gzip > /backups/db-$(date +\%Y\%m\%d).sql.gz
```

## Monitoring

### 1. Application Logs

```bash
# Docker
docker logs -f transcript-api

# Kubernetes
kubectl logs -f deployment/transcript-api -n transcript-chatbot
```

### 2. Metrics (Optional - Prometheus)

Add to docker-compose.yml:

```yaml
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
```

### 3. Alerts

Setup alerts for:
- API downtime
- High error rate
- Slow response times
- Vector store unavailable
- High memory usage

### 4. OpenTelemetry (Optional)

Enable in .env:
```bash
ENABLE_TRACING=true
OTEL_ENDPOINT=http://your-otel-collector:4318
```

## Scaling

### Horizontal Scaling

#### Docker Swarm

```bash
docker service scale transcript-api=3
```

#### Kubernetes

```bash
kubectl scale deployment transcript-api --replicas=3 -n transcript-chatbot

# Or autoscaling
kubectl autoscale deployment transcript-api \
  --min=2 --max=10 \
  --cpu-percent=70 \
  -n transcript-chatbot
```

### Performance Optimization

1. **Enable Redis Caching** (for conversations)
   ```bash
   # Add Redis to docker-compose.yml
   redis:
     image: redis:7-alpine
     ports:
       - "6379:6379"
   ```

2. **Use CDN** for static assets

3. **Database Connection Pooling**
   ```python
   # In settings.py
   postgres_pool_size: int = 20
   postgres_max_overflow: int = 10
   ```

4. **Rate Limiting**
   ```python
   # Already configured in settings
   rate_limit_requests_per_minute: int = 60
   ```

### Cost Optimization

1. **LLM Model Selection**
   ```bash
   # Cost-effective option
   LLM_MODEL_NAME=gpt-4o-mini

   # Higher quality (more expensive)
   LLM_MODEL_NAME=gpt-4o
   ```

2. **Embedding Model**
   ```bash
   # Standard
   EMBEDDING_MODEL_NAME=text-embedding-3-small

   # Higher quality
   EMBEDDING_MODEL_NAME=text-embedding-3-large
   ```

3. **Chunk Size Optimization**
   ```bash
   # Smaller chunks = more API calls but better precision
   CHUNK_SIZE=300

   # Larger chunks = fewer API calls but less precision
   CHUNK_SIZE=800
   ```

## Security Checklist

- [ ] Use HTTPS in production
- [ ] Rotate JWT secrets regularly
- [ ] Enable CORS only for your domain
- [ ] Implement rate limiting
- [ ] Use secrets management (AWS Secrets Manager, etc.)
- [ ] Enable firewall rules
- [ ] Regular security updates
- [ ] Monitor for suspicious activity
- [ ] Implement request validation
- [ ] Use environment-based configs (no hardcoded secrets)

## Troubleshooting

### API won't start

```bash
# Check logs
docker logs transcript-api

# Common issues:
# - Missing OPENAI_API_KEY
# - Vector store not accessible
# - Port already in use
```

### High memory usage

```bash
# Reduce worker count
API_WORKERS=2

# Or limit per-worker
gunicorn --workers 4 --max-requests 1000 --timeout 30
```

### Slow responses

```bash
# Check vector store latency
# Increase SEARCH_K if too few results
# Decrease CHUNK_SIZE if chunks too large
# Check LLM response times
```

## Rollback Procedure

### Docker Compose

```bash
# Stop current version
docker-compose down

# Checkout previous version
git checkout <previous-version>

# Start
docker-compose up -d
```

### Kubernetes

```bash
# Rollback to previous deployment
kubectl rollout undo deployment/transcript-api -n transcript-chatbot

# Rollback to specific revision
kubectl rollout undo deployment/transcript-api --to-revision=2 -n transcript-chatbot
```

## Support

For deployment issues:
- Check logs first
- Review this guide
- Open GitHub issue with logs and environment details
- Contact support@example.com

---

Last updated: November 2024
