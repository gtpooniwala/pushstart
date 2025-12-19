#!/bin/bash

# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Function to kill background processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping Pushstart..."
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    # Stop Docker containers
    echo "� Stopping Docker containers..."
    if command -v docker-compose &> /dev/null; then
        docker-compose down
        elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
        docker compose down
    fi
    exit
}

# Trap SIGINT (Ctrl+C)
trap cleanup SIGINT

echo "🚀 Starting Pushstart (Local Development)..."

# 1. Start Docker Dependencies (Database & MCP)
echo "� Starting Database & MCP Server (Docker)..."
cd "$DIR"
if command -v docker-compose &> /dev/null; then
    docker-compose up -d db mcp
    elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    docker compose up -d db mcp
else
    echo "❌ Docker Compose not found. Cannot start dependencies."
    exit 1
fi

# Wait for DB to be ready
echo "   Waiting for database to be ready..."
# Loop until we can connect to the port
for i in {1..30}; do
    if nc -z localhost 5432 2>/dev/null; then
        echo "   ✅ Database is ready!"
        break
    fi
    echo "   ...waiting for port 5432..."
    sleep 1
done

# 2. Activate Conda Environment
# Try to find conda profile script
if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
    elif [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/anaconda3/etc/profile.d/conda.sh"
else
    # Fallback: try to use conda from path if available
    if command -v conda &> /dev/null; then
        eval "$(conda shell.bash hook)"
    fi
fi

# Activate the environment
conda activate pushstart || { echo "❌ Failed to activate conda environment 'pushstart'. Run ./setup.sh first."; exit 1; }

# 3. Start Backend
echo "📦 Starting Backend (FastAPI)..."
cd "$DIR/backend"
# Check if uvicorn is available
if ! command -v uvicorn &> /dev/null; then
    echo "❌ Error: uvicorn not found. Please run ./setup.sh"
    exit 1
fi

# Run uvicorn
# Note: MCP_SERVER_URL defaults to http://localhost:8001/sse which matches docker-compose port mapping
# Force DATABASE_URL to localhost for local run
export DATABASE_URL="postgresql+asyncpg://pushstart:pushstart_password@localhost:5432/pushstart_db"
python3 -m uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# 4. Start Frontend
echo "🎨 Starting Frontend (Next.js)..."
cd "$DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo "✅ Pushstart is running!"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000/docs"
echo "   MCP:      http://localhost:8001/sse"
echo "   Press Ctrl+C to stop."

# Wait for processes
wait
