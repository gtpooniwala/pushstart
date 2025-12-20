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
    if [ -n "$MCP_PID" ]; then
        kill $MCP_PID 2>/dev/null
    fi
    if [ -n "$CALENDAR_MCP_PID" ]; then
        kill $CALENDAR_MCP_PID 2>/dev/null
    fi
    if [ -n "$GMAIL_MCP_PID" ]; then
        kill $GMAIL_MCP_PID 2>/dev/null
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

echo "🚀 Starting Pushstart (Local Development)..."

# 1. Start Docker Dependencies (Database only)
echo "🐳 Starting Database (Docker)..."
cd "$DIR"
if command -v docker-compose &> /dev/null; then
    # Ensure MCP container is stopped to free up port 8001
    docker-compose stop mcp 2>/dev/null
    docker-compose up -d db
    elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    docker compose stop mcp 2>/dev/null
    docker compose up -d db
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

# 3. Start MCP Server (Local)
echo "🔌 Starting MCP Server (Local)..."
cd "$DIR/mcp"
# Install dependencies to ensure they are available in the conda env
echo "   Installing MCP dependencies..."
pip install -r todoist_server/requirements.txt > /dev/null 2>&1

# Run uvicorn for MCP
# We run on port 8001 to match what the backend expects
export PYTHONPATH=$PYTHONPATH:$(pwd)
python3 -m uvicorn todoist_server.server:app --port 8001 &
MCP_PID=$!

# 3b. Start Calendar MCP Server (Local)
echo "🔌 Starting Calendar MCP Server (Local)..."
# Install dependencies
pip install -r calendar_server/requirements.txt > /dev/null 2>&1
python3 -m uvicorn calendar_server.server:app --port 8002 &
CALENDAR_MCP_PID=$!

# 3c. Start Gmail MCP Server (Local)
echo "🔌 Starting Gmail MCP Server (Local)..."
# Install dependencies
pip install -r gmail_server/requirements.txt > /dev/null 2>&1
python3 -m uvicorn gmail_server.server:app --port 8003 &
GMAIL_MCP_PID=$!

# Wait for MCP Server to be ready
echo "   Waiting for MCP servers to be ready..."
for i in {1..30}; do
    if nc -z localhost 8001 2>/dev/null && nc -z localhost 8002 2>/dev/null && nc -z localhost 8003 2>/dev/null; then
        echo "   ✅ MCP Servers are ready!"
        break
    fi
    echo "   ...waiting for ports 8001/8002/8003..."
    sleep 1
done

# 4. Start Backend
echo "📦 Starting Backend (FastAPI)..."
cd "$DIR/backend"
# Check if uvicorn is available
if ! command -v uvicorn &> /dev/null; then
    echo "❌ Error: uvicorn not found. Please run ./setup.sh"
    exit 1
fi

# Run uvicorn
# Force DATABASE_URL to localhost for local run
export DATABASE_URL="postgresql+asyncpg://pushstart:pushstart_password@localhost:5432/pushstart_db"
# Force MCP_SERVER_URL to localhost for local run
export MCP_SERVER_URL="http://127.0.0.1:8001/sse"

python3 -m uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# 5. Start Frontend
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
