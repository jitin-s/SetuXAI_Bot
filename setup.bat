@echo off
echo ===================================================
echo   SetuX AI Assistant - Local Setup Script
echo ===================================================
echo.

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to PATH! Please install Python 3.10+.
    pause
    exit /b 1
)

:: 2. Check Node & NPM
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js / NPM is not installed! Please install Node.js 18+.
    pause
    exit /b 1
)

:: 3. Check Ollama
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Ollama is not detected! Please download Ollama from https://ollama.com
    echo.
) else (
    echo [✓] Pulling local LLM model (qwen2.5:1.5b)...
    ollama pull qwen2.5:1.5b
)

echo.
echo [✓] Installing Python backend dependencies...
pip install -r requirements.txt

echo.
echo [✓] Installing React frontend dependencies...
cd webpage
npm install
cd ..

echo.
echo ===================================================
echo   Setup Complete! Run 'run_all.bat' to start!
echo ===================================================
pause
