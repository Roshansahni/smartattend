#!/bin/bash
set -e

echo "=== SmartAttend Project Setup on macOS M1 / Apple Silicon ==="

cd "$(dirname "$0")/.."

# Check tools
echo "[1/4] Verifying development environment..."
python3 --version || { echo "Python 3 required"; exit 1; }
node --version || { echo "Node.js required"; exit 1; }

# Setup backend
echo "[2/4] Initializing Python Virtual Environment..."
cd backend
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
if [ ! -f ".env" ]; then
    cp .env.example .env
fi
cd ..

# Setup frontend
echo "[3/4] Installing Frontend Dependencies..."
cd frontend
if [ ! -f ".env" ]; then
    cp .env.example .env
fi
npm install
cd ..

echo "[4/4] Setup complete!"
echo ""
echo "Run backend:  cd backend && source .venv/bin/activate && uvicorn main:app --reload"
echo "Run frontend: cd frontend && npm run dev"
