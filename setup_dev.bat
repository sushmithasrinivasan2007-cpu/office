@echo off
echo ========================================
echo   SmartOS - Local Development Setup
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3.11+ not found. Please install from python.org
    pause
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js 18+ not found. Please install from nodejs.org
    pause
    exit /b 1
)

echo [1/5] Setting up Python virtual environment...
cd backend
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate

echo [2/5] Installing Python dependencies...
pip install -r requirements.txt

echo [3/5] Setting up Node.js dependencies...
cd ..\frontend
if not exist node_modules (
    npm install
)

echo [4/5] Checking environment configuration...
cd ..\backend
if not exist .env (
    echo [WARNING] .env file not found. Copying from .env.example...
    copy .env.example .env
    echo Please edit backend\.env and add your API keys:
    echo   - SUPABASE_URL
    echo   - SUPABASE_KEY
    echo   - JWT_SECRET
    echo   - SMTP credentials (optional)
    echo   - AI API keys (optional)
    echo.
    pause
)

echo [5/5] Database setup instructions:
echo   1. Go to https://supabase.com and create account
echo   2. Create new project
echo   3. Go to SQL Editor
echo   4. Paste contents of database_schema_complete.sql
echo   5. Run the query
echo.

echo ========================================
echo Setup complete!
echo ========================================
echo.
echo To start development:
echo.
echo   Terminal 1 (Backend):
echo     cd backend
echo     call venv\Scripts\activate
echo     python app_socketio.py
echo.
echo   Terminal 2 (Frontend):
echo     cd frontend
echo     npm run dev
echo.
echo Then open http://localhost:5173 in your browser
echo.
pause