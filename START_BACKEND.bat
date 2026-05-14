@echo off
title SmartOS Backend Server
cd /d "%~dp0backend"
call venv\Scripts\activate
echo Starting SmartOS Backend...
echo ============================================
echo API will be at: http://localhost:5000
echo ============================================
echo.
python app_socketio.py
pause