@echo off
echo ========================================
echo   SmartOS System Verification
echo ========================================
echo.

REM Check files
echo [1] Checking project structure...

set "missing=0"

if exist "backend\app_socketio.py" (
    echo  ✓ Backend found
) else (
    echo  ✗ Backend missing
    set /a missing+=1
)

if exist "frontend\src\App.jsx" (
    echo  ✓ Frontend found
) else (
    echo  ✗ Frontend missing
    set /a missing+=1
)

if exist "database_schema_complete.sql" (
    echo  ✓ Database schema found
) else (
    echo  ✗ Database schema missing
    set /a missing+=1
)

if exist "docker-compose.yml" (
    echo  ✓ Docker compose found
) else (
    echo  ✗ Docker compose missing
    set /a missing+=1
)

echo.
echo [2] Checking Python dependencies...

python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo  ✗ Flask not installed
    set /a missing+=1
) else (
    echo  ✓ Flask installed
)

python -c "import supabase" >nul 2>&1
if errorlevel 1 (
    echo  ✗ Supabase client not installed
    set /a missing+=1
) else (
    echo  ✓ Supabase client installed
)

python -c "import flask_socketio" >nul 2>&1
if errorlevel 1 (
    echo  ✗ Flask-SocketIO not installed
    set /a missing+=1
) else (
    echo  ✓ Flask-SocketIO installed
)

echo.
echo [3] Checking Node modules...

if exist "frontend\node_modules" (
    echo  ✓ Node modules installed
) else (
    echo  ✗ Node modules missing (run npm install)
    set /a missing+=1
)

echo.
echo ========================================
if %missing%==0 (
    echo  ✓ All checks passed! System ready.
    echo.
    echo  Next steps:
    echo    1. Set up backend/.env with your keys
    echo    2. Run: docker-compose up -d
    echo    3. Open http://localhost:3000
) else (
    echo  ✗ %missing% check(s) failed.
    echo  Please fix the issues above.
)
echo ========================================
pause