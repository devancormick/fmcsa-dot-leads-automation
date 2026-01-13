#!/bin/bash
# Single command to start the FMCSA DOT Leads Automation
# This script starts Docker and keeps the container running with scheduled tasks

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "FMCSA DOT Leads Automation"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed."
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "ERROR: Docker Compose is not installed."
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check for required files
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "WARNING: .env file not found"
    echo "Please create .env file with your configuration"
    exit 1
fi

if [ ! -f "$SCRIPT_DIR/service_account.json" ]; then
    echo "WARNING: service_account.json not found"
    echo "Please ensure service_account.json is in the project root"
    exit 1
fi

# Create necessary directories
mkdir -p "$SCRIPT_DIR/output/csv"
mkdir -p "$SCRIPT_DIR/logs"

echo "Starting Docker container..."
echo "The container will run continuously and execute tasks daily at 2:00 AM"
echo ""
echo "To stop: ./stop.sh"
echo "To view logs: docker-compose logs -f"
echo ""

# Build and start the container
cd "$SCRIPT_DIR"
docker-compose up --build -d

# Show status
echo ""
echo "Container status:"
docker-compose ps

echo ""
echo "✅ Container is running!"
echo ""
echo "Useful commands:"
echo "  ./stop.sh                       - Stop the container"
echo "  docker-compose logs -f          - View logs (follow mode)"
echo "  docker-compose ps               - Check container status"
echo "  docker-compose restart          - Restart the container"
echo ""
