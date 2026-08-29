@echo off
echo ===================================================
echo   Starting SetuX AI Assistant (Server & React App)
echo ===================================================
echo.

:: Start FastAPI Backend Server
start "SetuX FastAPI Backend (Port 8000)" cmd /k "python server.py"

:: Start React Frontend Web App
start "SetuX React Webpage (Port 5173)" cmd /k "cd webpage && npm run dev"

echo.
echo SetuX Backend starting on http://localhost:8000
echo SetuX React Webpage starting on http://localhost:5173
echo.
pause
