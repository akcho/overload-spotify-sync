#!/bin/bash

# Install cron job for daily sync

set -e

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🕒 Installing daily cron job..."

# Make scripts executable
chmod +x "$SCRIPT_DIR/daily_sync.sh"
chmod +x "$SCRIPT_DIR/setup.sh"

# Create cron job entry (runs daily at 11:30 PM)
CRON_JOB="30 23 * * * $SCRIPT_DIR/daily_sync.sh"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "$SCRIPT_DIR/daily_sync.sh"; then
    echo "⚠️  Cron job already exists"
else
    # Add cron job
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✅ Cron job installed successfully"
    echo "   Runs daily at 11:30 PM"
fi

echo ""
echo "To manage your cron jobs:"
echo "  View: crontab -l"
echo "  Edit: crontab -e"
echo "  Remove: crontab -r"
echo ""
echo "Log files:"
echo "  Daily sync: $PROJECT_DIR/daily_sync.log"
echo "  App logs: $PROJECT_DIR/overload_spotify_sync.log"