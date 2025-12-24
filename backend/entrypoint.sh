#!/bin/sh
# Entrypoint script for Railway deployment
# Reads PORT environment variable and starts uvicorn

# Get PORT from environment, default to 8000
PORT=${PORT:-8000}

echo "Starting uvicorn on port $PORT"

# Start uvicorn with the port from environment
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --workers 4
