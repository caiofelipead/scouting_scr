#!/bin/sh
set -e

# Debug: Print environment
echo "=== Railway Environment Debug ==="
echo "PORT environment variable: ${PORT:-NOT SET}"
echo "=================================="

# Get PORT from environment, default to 8000
export LISTEN_PORT="${PORT:-8000}"

echo "Starting uvicorn on port $LISTEN_PORT"

# Start uvicorn - use Python to ensure proper variable expansion
exec python -m uvicorn app.main:app --host 0.0.0.0 --port $LISTEN_PORT
