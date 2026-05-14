#!/bin/bash

echo "========================================"
echo "  SmartOS - Local Development Setup"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3.11+ not found. Please install from python.org"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js 18+ not found. Please install from nodejs.org"
    exit 1
fi

echo "[1/5] Setting up Python virtual environment..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

echo "[2/5] Installing Python dependencies..."
pip install -r requirements.txt

echo "[3/5] Setting up Node.js dependencies..."
cd ../frontend
if [ ! -d "node_modules" ]; then
    npm install
fi

echo "[4/5] Checking environment configuration..."
cd ../backend
if [ ! -f ".env" ]; then
    echo "[WARNING] .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "Please edit backend/.env and add your API keys:"
    echo "  - SUPABASE_URL"
    echo "  - SUPABASE_KEY"
    echo "  - JWT_SECRET"
    echo "  - SMTP credentials (optional)"
    echo "  - AI API keys (optional)"
    echo ""
fi

echo "[5/5] Database setup instructions:"
echo "  1. Go to https://supabase.com and create account"
echo "  2. Create new project"
echo "  3. Go to SQL Editor"
echo "  4. Paste contents of database_schema_complete.sql"
echo "  5. Run the query"
echo ""

echo "========================================"
echo "Setup complete!"
echo "========================================"
echo ""
echo "To start development:"
echo ""
echo "   Terminal 1 (Backend):"
echo "     cd backend"
echo "     source venv/bin/activate"
echo "     python app_socketio.py"
echo ""
echo "   Terminal 2 (Frontend):"
echo "     cd frontend"
echo "     npm run dev"
echo ""
echo "Then open http://localhost:5173 in your browser"
echo ""