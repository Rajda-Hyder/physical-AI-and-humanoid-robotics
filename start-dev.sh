#!/bin/bash

# Development startup script
# This script helps start both backend and frontend in separate terminals

echo "🚀 Physical AI & Humanoid Robotics - Development Startup"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Warning: .env file not found${NC}"
    echo "Please create .env with:"
    echo "  QDRANT_API_KEY=your-key"
    echo "  QDRANT_URL=your-url"
    echo "  COHERE_API_KEY=your-key"
    echo ""
fi

# Check if .env.local exists
if [ ! -f .env.local ]; then
    echo -e "${YELLOW}⚠️  Warning: .env.local file not found${NC}"
    echo "Please create .env.local with frontend environment variables"
    echo ""
fi

echo "Choose an option:"
echo "  1) Start Backend (FastAPI on port 8000)"
echo "  2) Start Frontend (Docusaurus on port 3000)"
echo "  3) Test Backend Connection"
echo "  4) Show Logs"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo -e "${GREEN}Starting Backend...${NC}"
        cd backend
        source .venv/bin/activate
        python -m backend.app
        ;;
    2)
        echo -e "${GREEN}Starting Frontend...${NC}"
        pnpm start
        ;;
    3)
        echo -e "${GREEN}Testing Backend Connection...${NC}"
        node test-backend-connection.js
        ;;
    4)
        echo -e "${GREEN}Opening logs...${NC}"
        echo "Backend logs: Check terminal running backend"
        echo "Frontend logs: Check terminal running frontend"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
