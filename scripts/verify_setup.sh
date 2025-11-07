#!/bin/bash
# Verify the production setup is working

echo "================================================================"
echo "Production System Verification"
echo "================================================================"

echo ""
echo "1. Checking Docker containers..."
docker ps --filter "name=transcript" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "2. Checking Qdrant health..."
if curl -sf http://localhost:6333/health > /dev/null 2>&1; then
    echo "✓ Qdrant is healthy"
    curl -s http://localhost:6333/health | python3 -m json.tool
else
    echo "✗ Qdrant not responding yet (may still be starting up)"
    echo "  Wait 10 seconds and try: curl http://localhost:6333/health"
fi

echo ""
echo "3. Checking API health..."
if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ API is healthy"
    curl -s http://localhost:8000/health | python3 -m json.tool
else
    echo "✗ API not responding yet (may still be starting up)"
    echo "  Check logs with: docker-compose logs api"
fi

echo ""
echo "4. Checking Qdrant collections..."
curl -s http://localhost:6333/collections 2>/dev/null | python3 -m json.tool || echo "  Waiting for Qdrant..."

echo ""
echo "================================================================"
echo "Next Steps:"
echo "================================================================"
echo ""
echo "View logs:"
echo "  docker-compose logs -f api"
echo "  docker-compose logs -f qdrant"
echo ""
echo "Access services:"
echo "  API: http://localhost:8000"
echo "  Qdrant Dashboard: http://localhost:6333/dashboard"
echo ""
echo "Ingest a transcript:"
echo "  python examples/ingest_transcript.py"
echo ""
echo "View records:"
echo "  python scripts/view_records.py"
echo ""
