#!/bin/bash
# GrainRX UI - Quick start script
# Usage: ./grainui.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🎬 GrainRX UI - Starting server..."

# Check for virtual environment and source it
if [ -d "$SCRIPT_DIR/venv" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
elif [ -d "$SCRIPT_DIR/.venv" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
elif [ -d "$SCRIPT_DIR/../venv" ]; then
    source "$SCRIPT_DIR/../venv/bin/activate"
elif [ -d "$SCRIPT_DIR/../.venv" ]; then
    source "$SCRIPT_DIR/../.venv/bin/activate"
else
    echo "⚠️  No virtual environment found, using system Python..."
fi

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install fastapi uvicorn pillow numpy numba
fi

# Start the server
cd "$SCRIPT_DIR/grainui"
echo "🚀 Opening http://127.0.0.1:8000 in your browser..."
open http://127.0.0.1:8000 2>/dev/null || echo "🌐 Open http://127.0.0.1:8000 manually"
echo ""
uvicorn app:app --host 127.0.0.1 --port 8000 --reload