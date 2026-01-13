#!/bin/bash
# Stop script for FMCSA DOT Leads Automation
# Stops and removes the Docker container

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "FMCSA DOT Leads Automation - Stop"
echo "=========================================="
echo ""

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "ERROR: Docker Compose is not installed."
    exit 1
fi

# Check if container is running
cd "$SCRIPT_DIR"
if docker-compose ps | grep -q "dot-leads-automation.*Up"; then
    echo "Stopping Docker container..."
    docker-compose down
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Container stopped successfully!"
    else
        echo ""
        echo "❌ Error stopping container"
        exit 1
    fi
else
    echo "Container is not running."
    echo ""
    echo "To remove stopped containers:"
    echo "  docker-compose down"
fi

echo ""
echo "To start again:"
echo "  ./start.sh              - Production mode (daily at 2 AM)"
echo "  ./start-test.sh         - Test mode (every 5 minutes)"
echo ""
