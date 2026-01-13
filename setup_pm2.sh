#!/bin/bash
# Setup script for PM2 process management
# PM2 can manage the Python script and provide process monitoring, logging, and auto-restart

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH=$(which python3)
NODE_PATH=$(which node)

echo "FMCSA DOT Leads Automation - PM2 Setup"
echo "======================================"
echo ""
echo "Script directory: $SCRIPT_DIR"
echo "Python path: $PYTHON_PATH"
echo ""

# Check if Node.js is installed
if [ -z "$NODE_PATH" ]; then
    echo "ERROR: Node.js not found. PM2 requires Node.js."
    echo "Please install Node.js: https://nodejs.org/"
    echo ""
    echo "Or use: brew install node (on macOS)"
    echo "Or use: apt-get install nodejs npm (on Ubuntu/Debian)"
    exit 1
fi

# Check if Python is available
if [ -z "$PYTHON_PATH" ]; then
    echo "ERROR: Python 3 not found. Please install Python 3.9+"
    exit 1
fi

# Check if PM2 is installed
if ! command -v pm2 &> /dev/null; then
    echo "PM2 not found. Installing PM2..."
    npm install -g pm2
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install PM2"
        exit 1
    fi
    echo "✅ PM2 installed successfully"
fi

# Create logs directory
mkdir -p "$SCRIPT_DIR/logs"
echo "Created logs directory: $SCRIPT_DIR/logs"

# Check if ecosystem.config.js exists
if [ ! -f "$SCRIPT_DIR/ecosystem.config.js" ]; then
    echo "ERROR: ecosystem.config.js not found"
    exit 1
fi

echo ""
echo "PM2 Configuration:"
echo "==================="
pm2 --version
echo ""

# Check if app is already running
if pm2 list | grep -q "dot-leads-automation"; then
    echo "WARNING: dot-leads-automation is already running in PM2"
    read -p "Do you want to restart it? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pm2 restart ecosystem.config.js
    else
        echo "Keeping existing PM2 process. Exiting."
        exit 0
    fi
else
    # Start the application
    echo "Starting application with PM2..."
    cd "$SCRIPT_DIR"
    pm2 start ecosystem.config.js
fi

echo ""
echo "✅ PM2 setup complete!"
echo ""
echo "Useful PM2 commands:"
echo "  pm2 list                    - List all processes"
echo "  pm2 logs dot-leads-automation - View logs"
echo "  pm2 monit                   - Monitor processes"
echo "  pm2 stop dot-leads-automation - Stop the process"
echo "  pm2 restart dot-leads-automation - Restart the process"
echo "  pm2 delete dot-leads-automation - Remove from PM2"
echo "  pm2 save                    - Save current process list"
echo "  pm2 startup                 - Generate startup script"
echo ""
echo "For scheduled execution (daily at 2 AM), the app uses cron_restart in ecosystem.config.js"
echo "Or use PM2 with external cron: pm2 start ecosystem.config.js --only dot-leads-automation-once"
