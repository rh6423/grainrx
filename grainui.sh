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

# Install dependencies from the single source of truth if FastAPI isn't present
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing dependencies from requirements.txt..."
    pip install -r "$SCRIPT_DIR/requirements.txt"
    # requirements.txt may or may not pin the UI extras; ensure they're there
    pip install fastapi uvicorn
fi

# Start the server from the gui directory (matches the repo layout)
cd "$SCRIPT_DIR/gui"

URL="http://127.0.0.1:${PORT:-8000}"
echo "🚀 Opening $URL in your browser..."

# Cross-platform browser open: macOS uses `open`, Linux uses `xdg-open`,
# Windows (git-bash / WSL) uses `start`. Fall back to a printed URL.
if command -v open >/dev/null 2>&1; then
    open "$URL" 2>/dev/null || true
elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$URL" 2>/dev/null || true
elif command -v start >/dev/null 2>&1; then
    start "$URL" 2>/dev/null || true
else
    echo "🌐 Open $URL manually"
fi
echo ""

uvicorn app:app --host 127.0.0.1 --port "${PORT:-8000}" --reload
