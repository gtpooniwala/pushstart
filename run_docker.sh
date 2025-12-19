#!/bin/bash

# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Function to kill background processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping Pushstart..."
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    # Stop Docker containers
    echo "🐳 Stopping Docker containers..."
    if command -v docker-compose &> /dev/null; then
        docker-compose down
        elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
        docker compose down
    fi
    exit
}

# Trap SIGINT (Ctrl+C)
trap cleanup SIGINT

echo "🚀 Starting Pushstart (Dockerized Backend)..."

# 1. Start Backend, MCP & Database (Docker)
echo "🐳 Starting Backend, MCP & Database (Docker)..."
cd "$DIR"
if command -v docker-compose &> /dev/null; then
    docker-compose up -d --build
    elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    docker compose up -d --build
else
    echo "❌ Docker Compose not found. Cannot start services."
    exit 1
fi

echo "   Services started in background. Logs available via 'docker-compose logs -f'"

# 2. Start Frontend (Local)
# We still run frontend locally for better dev experience (HMR)
echo "🎨 Starting Frontend (Next.js)..."
cd "$DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo "✅ Pushstart is running!"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000/docs"
echo "   Press Ctrl+C to stop."

# Wait for processes
wait
