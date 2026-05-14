@echo off
echo ============================================
echo   SmartOS - Development Server
echo ============================================
echo.

REM Check if .env exists
if not exist "backend\.env" (
    echo [WARNING] backend\.env not found!
    echo Copying from .env.example...
    copy backend\.env.example backend\.env
    echo.
    echo [IMPORTANT] Please edit backend\.env and add your Supabase credentials:
    echo   - SUPABASE_URL
    echo   - SUPABASE_KEY
    echo   - JWT_SECRET
    echo.
    pause
)

echo [1] Starting Backend API server...
echo     Press Ctrl+C to stop
echo ============================================

cd backend
call venv\Scripts\activate
python app_socketio.py