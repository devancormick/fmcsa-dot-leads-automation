#!/bin/bash
# Start script for FMCSA DOT Leads Automation - TEST MODE (without Docker)
# Runs the Python script directly with test mode (every 5 minutes)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "FMCSA DOT Leads Automation - TEST MODE"
echo "=========================================="
echo "Running without Docker (direct Python execution)"
echo ""
echo "⚠️  WARNING: This will run every 5 minutes for testing!"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed."
    echo "Please install Python 3.9+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"
echo ""

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

# Check if dependencies are installed
if ! python3 -c "import sodapy" 2>/dev/null; then
    echo "Dependencies not installed. Installing..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed"
    echo ""
fi

# Create necessary directories
mkdir -p "$SCRIPT_DIR/output/csv"
mkdir -p "$SCRIPT_DIR/logs"

echo "Starting scheduler in TEST MODE..."
echo "The scheduler will run continuously and execute tasks every 5 minutes"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Change to script directory and run scheduler in test mode
# Overrides MODE in .env to force test mode
cd "$SCRIPT_DIR"
python3 scheduler.py --test-mode
