@echo off
echo ============================================
echo   SmartOS - All-in-One Starter
echo ============================================
echo.
echo This will start BOTH backend and frontend.
echo.
echo Step 1: Backend will start in a new window
echo         (Wait for it to say "Running on port 5000")
echo.
echo Step 2: Frontend will start in another window
echo         (Wait for "Local: http://localhost:5173")
echo.
echo Step 3: Open http://localhost:5173 in your browser
echo.
pause

REM Start Backend in separate window
cd /d "%~dp0backend"
call venv\Scripts\activate
start "SmartOS Backend" cmd /k "call venv\Scripts\activate && python app_socketio.py"

echo Backend starting... wait 3 seconds...
timeout /t 3 /nobreak >nul

REM Start Frontend in separate window
cd /d "%~dp0frontend"
start "SmartOS Frontend" cmd /k "npm run dev"

echo.
echo ============================================
echo   Both servers are starting!
echo ============================================
echo.
echo   Backend API:  http://localhost:5000
echo   Frontend App: http://localhost:5173
echo.
echo   Close the black windows to stop servers.
echo.
echo   IMPORTANT: First time? Register with any email.
echo ============================================
echo.
pause