#!/bin/bash
# Docker entrypoint script
# Allows running the script with different commands

set -e

# Wait for any initialization if needed
echo "Starting FMCSA DOT Leads Automation..."

# Execute the command passed to the container
exec "$@"
