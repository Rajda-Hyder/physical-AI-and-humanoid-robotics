#!/bin/bash

# RAG Chatbot Qdrant Setup Script Wrapper
# Activates virtual environment and runs the setup

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

echo "🚀 RAG Chatbot Qdrant Setup Launcher"
echo "===================================="
echo ""

# Check if .env exists
if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo "❌ Error: .env file not found in $BACKEND_DIR"
    echo "Please create .env with required variables:"
    echo "  - QDRANT_API_KEY"
    echo "  - QDRANT_URL"
    echo "  - COHERE_API_KEY"
    exit 1
fi

echo "✅ Configuration file found"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.9+"
    exit 1
fi

echo "✅ Python3 found: $(python3 --version)"
echo ""

# Activate virtual environment if exists
if [ -d "$BACKEND_DIR/.venv" ]; then
    echo "📦 Activating virtual environment..."
    source "$BACKEND_DIR/.venv/bin/activate"
    echo "✅ Virtual environment activated"
else
    echo "⚠️  Virtual environment not found"
    echo "   Make sure required packages are installed:"
    echo "   pip install -r requirements.txt"
fi

echo ""
echo "Starting setup in 3 seconds..."
sleep 3
echo ""

# Run the setup script
cd "$BACKEND_DIR"
python3 scripts/setup_qdrant.py

exit $?
