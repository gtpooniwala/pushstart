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
    exit
}

# Trap SIGINT (Ctrl+C)
trap cleanup SIGINT

echo "🚀 Starting Pushstart..."

# Activate Conda Environment
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
conda activate pushstart || { echo "❌ Failed to activate conda environment 'pushstart'"; exit 1; }

# Start Backend
echo "📦 Starting Backend (FastAPI)..."
cd "$DIR/backend"
# Check if uvicorn is available
if ! command -v uvicorn &> /dev/null; then
    echo "❌ Error: uvicorn not found. Please install backend dependencies."
    echo "   cd backend && pip install -r requirements.txt (or pip install fastapi uvicorn ...)"
    exit 1
fi

uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start Frontend
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
