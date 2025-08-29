#!/bin/bash

# Daily sync wrapper script for cron job

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Activate virtual environment
source venv/bin/activate

# Run the sync with logging
python3 overload_spotify_sync.py >> daily_sync.log 2>&1

echo "$(date): Daily sync completed" >> daily_sync.log