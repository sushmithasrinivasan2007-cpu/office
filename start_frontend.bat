@echo off
title SmartOS Frontend
cd /d "%~dp0frontend"
echo Starting SmartOS Frontend...
echo ============================================
echo App will be at: http://localhost:5173
echo ============================================
echo.
npm run dev
pause