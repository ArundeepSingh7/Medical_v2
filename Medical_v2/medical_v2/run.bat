@echo off
title Medical Screening Backend

echo.
echo   =====================================
echo    Medical Screening System (Backend)
echo   =====================================
echo.

REM Step 1: Activate virtual environment
IF EXIST ".venv\Scripts\activate.bat" (
    echo [1/5] Activating virtual environment...
    call .venv\Scripts\activate.bat
) ELSE (
    echo [!] Virtual environment not found. Run setup.bat first.
    pause
    exit /b 1
)

REM Step 2: Check FastAPI
python -c "import fastapi" >nul 2>&1
IF ERRORLEVEL 1 (
    echo [!] FastAPI not installed. Run setup.bat.
    pause
    exit /b 1
)

REM Step 3: Start FastAPI backend
echo.
echo [2/5] Starting FastAPI server...
start cmd /k "uvicorn api:app --host 0.0.0.0 --port 8000"

REM Wait for server
echo Waiting for API to initialize...
timeout /t 4 >nul

REM Step 4: Ask user if they want Streamlit (optional)
echo.
set /p choice="Do you want to start Streamlit UI for testing? (y/n): "

IF /I "%choice%"=="y" (
    echo.
    echo [3/5] Starting Streamlit...
    start cmd /k "python -m streamlit run app.py --server.port 8501"
    echo UI: http://localhost:8501
) ELSE (
    echo Skipping Streamlit UI.
)

echo.
echo =====================================
echo  System Running
echo =====================================
echo.
echo  API Docs: http://localhost:8000/docs
echo  Health:   http://localhost:8000/health
echo.

pause