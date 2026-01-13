#!/bin/bash
# Start script for TEST MODE (runs every 5 minutes)
# This is useful for testing the application

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "FMCSA DOT Leads Automation - TEST MODE"
echo "=========================================="
echo ""
echo "⚠️  WARNING: This will run every 5 minutes for testing!"
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

echo "Starting Docker container in TEST MODE..."
echo "The container will run continuously and execute tasks every 5 minutes"
echo ""
echo "To stop: docker-compose down"
echo "To view logs: docker-compose logs -f"
echo ""

# Build and start the container with test mode
cd "$SCRIPT_DIR"
TEST_MODE=true TEST_INTERVAL_MINUTES=5 docker-compose up --build -d

# Show status
echo ""
echo "Container status:"
docker-compose ps

echo ""
echo "✅ Container is running in TEST MODE!"
echo ""
echo "🧪 Test Mode Features:"
echo "  - Runs every 5 minutes (instead of daily)"
echo "  - Useful for testing and development"
echo "  - Same functionality as production mode"
echo ""
echo "Useful commands:"
echo "  ./stop.sh                       - Stop the container"
echo "  docker-compose logs -f          - View logs (follow mode)"
echo "  docker-compose ps               - Check container status"
echo "  docker-compose restart          - Restart the container"
echo ""
echo "To switch to production mode (daily at 2 AM):"
echo "  ./stop.sh"
echo "  ./start.sh"
echo ""
