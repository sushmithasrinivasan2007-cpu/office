@echo off
echo ============================================
echo   SmartOS - ONE-CLICK START
echo ============================================
echo.

REM Change to project directory
cd /d "%~dp0"

echo [1] Checking Python virtual environment...
if not exist "backend\venv\" (
    echo Creating virtual environment...
    cd backend
    python -m venv venv
    cd ..
)

echo [2] Activating virtual environment...
call backend\venv\Scripts\activate

echo [3] Installing/updating dependencies...
pip install -q -r backend/requirements_minimal.txt

echo [4] Checking frontend dependencies...
if not exist "frontend\node_modules\" (
    echo Installing Node packages...
    cd frontend
    npm install
    cd ..
)

echo [5] Ensuring .env file exists...
if not exist "backend\.env" (
    echo Creating .env from template...
    copy backend\.env.example backend\.env
    echo.
    echo ============================================
    echo   IMPORTANT: Edit backend\.env and add your keys!
    echo   - SUPABASE_URL (from supabase.com)
    echo   - SUPABASE_KEY (from supabase.com)
    echo   - JWT_SECRET (any random string)
    echo ============================================
    echo.
    pause
)

echo [6] Starting Backend Server...
echo ============================================
echo Backend will run on http://localhost:5000
echo ============================================
echo.

cd backend
start "SmartOS Backend" cmd /k "venv\Scripts\activate && python app_socketio.py"

timeout /t 3 /nobreak >nul

echo [7] Starting Frontend Server...
echo ============================================
echo Frontend will run on http://localhost:5173
echo ============================================
echo.

cd ..\frontend
start "SmartOS Frontend" cmd /k "npm run dev"

timeout /t 5 /nobreak >nul

echo.
echo ============================================
echo   SmartOS is starting!
echo ============================================
echo.
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:5000
echo.
echo   Close the CMD windows to stop the servers.
echo.
echo   First time? Register with any email/password
echo ============================================
echo.
pause