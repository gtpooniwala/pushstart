#!/bin/bash

# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "🛠️  Setting up Pushstart..."

# 1. Conda Environment Setup
echo "🐍 Setting up Python Environment..."

# Try to find conda profile script
if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
    elif [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/anaconda3/etc/profile.d/conda.sh"
else
    if command -v conda &> /dev/null; then
        eval "$(conda shell.bash hook)"
    else
        echo "❌ Conda not found. Please install Miniconda or Anaconda."
        exit 1
    fi
fi

# Check if environment exists
if conda env list | grep -q "pushstart"; then
    echo "   Environment 'pushstart' already exists. Updating..."
    conda env update -f "$DIR/environment.yml" --prune
else
    echo "   Creating environment 'pushstart'..."
    conda env create -f "$DIR/environment.yml"
fi

# Activate for subsequent steps
conda activate pushstart

# Install backend dependencies if not fully covered by environment.yml (e.g. pip packages)
# Assuming environment.yml covers most, but we can run pip install just in case if there's a requirements.txt
# or if we want to ensure specific pip packages are installed.
# For now, we rely on environment.yml.

# 2. Frontend Setup
echo "⚛️  Setting up Frontend..."
cd "$DIR/frontend"
if [ ! -d "node_modules" ]; then
    echo "   Installing npm packages..."
    npm install
else
    echo "   Node modules found. Skipping install (run 'npm install' manually if needed)."
fi

# 3. Docker Setup (Pull images)
echo "🐳 Setting up Docker..."
cd "$DIR"
if command -v docker-compose &> /dev/null; then
    docker-compose pull
    elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    docker compose pull
else
    echo "⚠️  Docker Compose not found. Please ensure Docker is installed."
fi

echo "✅ Setup complete! You can now run './run.sh'"
