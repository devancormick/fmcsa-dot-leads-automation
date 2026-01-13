#!/bin/bash
# Stop script for FMCSA DOT Leads Automation (Docker)
# Stops and removes the Docker container

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "FMCSA DOT Leads Automation - Stop Docker"
echo "=========================================="
echo ""

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "ERROR: Docker Compose is not installed."
    exit 1
fi

# Run docker-compose down
cd "$SCRIPT_DIR"
echo "Stopping Docker container..."
docker-compose down

# Check the result
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Container stopped successfully!"
    
    # Verify it's actually stopped
    if docker-compose ps 2>/dev/null | grep -q "dot-leads-automation.*Up"; then
        echo "⚠️  Warning: Container may still be running"
    else
        echo "✅ Verified: Container is stopped"
    fi
else
    echo ""
    echo "❌ Error stopping container"
    exit 1
fi

echo ""
echo "To start again:"
echo "  ./start.sh                  - Production mode without Docker (daily at 2 AM)"
echo "  ./start-test.sh             - Test mode without Docker (every 5 minutes)"
echo "  ./start-docker.sh           - Production mode with Docker (daily at 2 AM)"
echo "  ./start-docker-test.sh      - Test mode with Docker (every 5 minutes)"
echo ""
