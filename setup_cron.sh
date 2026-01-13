#!/bin/bash
# Setup script for cron job scheduling
# This script helps set up a daily cron job for FMCSA DOT Leads Automation

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH=$(which python3)
CRON_LOG="/var/log/dot_leads_automation.log"

echo "FMCSA DOT Leads Automation - Cron Setup"
echo "========================================"
echo ""
echo "Script directory: $SCRIPT_DIR"
echo "Python path: $PYTHON_PATH"
echo "Log file: $CRON_LOG"
echo ""

# Check if Python is available
if [ -z "$PYTHON_PATH" ]; then
    echo "ERROR: Python 3 not found. Please install Python 3.9+"
    exit 1
fi

# Create log directory if it doesn't exist
LOG_DIR=$(dirname "$CRON_LOG")
if [ ! -d "$LOG_DIR" ]; then
    echo "Creating log directory: $LOG_DIR"
    sudo mkdir -p "$LOG_DIR"
    sudo chmod 755 "$LOG_DIR"
fi

# Create cron job entry
CRON_TIME="0 2"  # 2:00 AM daily (adjust as needed)
CRON_ENTRY="$CRON_TIME * * * cd $SCRIPT_DIR && $PYTHON_PATH main.py >> $CRON_LOG 2>&1"

echo "Cron job entry:"
echo "$CRON_ENTRY"
echo ""

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "main.py"; then
    echo "WARNING: A cron job for this script already exists."
    read -p "Do you want to replace it? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Remove existing entry
        crontab -l 2>/dev/null | grep -v "main.py" | crontab -
    else
        echo "Keeping existing cron job. Exiting."
        exit 0
    fi
fi

# Add cron job
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

echo "✅ Cron job installed successfully!"
echo ""
echo "The script will run daily at 2:00 AM"
echo "Logs will be written to: $CRON_LOG"
echo ""
echo "To view current cron jobs: crontab -l"
echo "To remove this cron job: crontab -e (then delete the line)"
echo "To test manually: cd $SCRIPT_DIR && $PYTHON_PATH main.py"
