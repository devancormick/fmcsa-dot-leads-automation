#!/bin/bash
# Setup script for Docker deployment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "FMCSA DOT Leads Automation - Docker Setup"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed."
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "ERROR: Docker Compose is not installed."
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check for required files
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "WARNING: .env file not found"
    echo "Please create .env file with your configuration"
    echo "You can copy from .env.example if it exists"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

if [ ! -f "$SCRIPT_DIR/service_account.json" ]; then
    echo "WARNING: service_account.json not found"
    echo "Please ensure service_account.json is in the project root"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create necessary directories
mkdir -p "$SCRIPT_DIR/output/csv"
mkdir -p "$SCRIPT_DIR/logs"
echo "✅ Created output and logs directories"

echo ""
echo "Docker Setup Options:"
echo "====================="
echo "1. Build and run once (manual execution)"
echo "2. Build and run with Docker Compose (recommended)"
echo "3. Build and run with scheduled cron (inside container)"
echo ""
read -p "Select option (1-3): " -n 1 -r
echo

case $REPLY in
    1)
        echo ""
        echo "Building Docker image..."
        docker build -t dot-leads-automation:latest .
        
        echo ""
        echo "Running container..."
        docker run --rm \
            --env-file .env \
            -v "$SCRIPT_DIR/service_account.json:/app/service_account.json:ro" \
            -v "$SCRIPT_DIR/output:/app/output" \
            -v "$SCRIPT_DIR/logs:/app/logs" \
            dot-leads-automation:latest
        ;;
    2)
        echo ""
        echo "Building and starting with Docker Compose..."
        docker-compose up --build dot-leads-automation
        ;;
    3)
        echo ""
        echo "Building and starting scheduler with Docker Compose..."
        docker-compose up --build -d dot-leads-scheduler
        echo ""
        echo "✅ Scheduler container is running in the background"
        echo "View logs: docker-compose logs -f dot-leads-scheduler"
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

echo ""
echo "Useful Docker commands:"
echo "  docker-compose up -d              - Start in background"
echo "  docker-compose down               - Stop containers"
echo "  docker-compose logs -f            - View logs"
echo "  docker-compose ps                 - List containers"
echo "  docker-compose restart            - Restart containers"
echo "  docker-compose exec dot-leads-automation bash - Enter container"
