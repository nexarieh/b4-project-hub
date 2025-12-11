#!/bin/bash
# Restart the B4 Dashboard server

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "Stopping existing server..."
pkill -f "serve.py" 2>/dev/null || pkill -f "http.server 8081" 2>/dev/null
sleep 1

echo "Starting server..."
python3 serve.py &

sleep 2
echo ""
echo "Dashboard running at: http://localhost:8081"
