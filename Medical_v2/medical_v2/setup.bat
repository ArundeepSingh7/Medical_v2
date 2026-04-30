@echo off
title Setup - Medical Screening System

echo.
echo   =====================================
echo    Medical Screening — Setup
echo   =====================================
echo.

REM Step 1: Check Python
echo [1/6] Checking Python...
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)
python --version

REM Step 2: Create virtual environment
echo.
echo [2/6] Creating virtual environment...
IF NOT EXIST ".venv" (
    python -m venv .venv
    echo     Created
) ELSE (
    echo     Already exists
)

REM Step 3: Activate
echo.
echo [3/6] Activating environment...
call .venv\Scripts\activate.bat

REM Step 4: Upgrade pip
echo.
echo [4/6] Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Step 5: Install requirements
echo.
echo [5/6] Installing dependencies...
python -m pip install -r requirements.txt

IF ERRORLEVEL 1 (
    echo ERROR: Installation failed.
    pause
    exit /b 1
)

REM Step 6: Verify critical libraries
echo.
echo [6/6] Verifying installation...
python -c "import torch, fastapi, uvicorn, transformers, PIL" >nul 2>&1

IF ERRORLEVEL 1 (
    echo WARNING: Some libraries may not be installed correctly.
) ELSE (
    echo All core dependencies OK
)

echo.
echo =====================================
echo  Setup Complete
echo =====================================
echo.
echo  Start backend using: run.bat
echo  API will run at: http://localhost:8000
echo.

pause