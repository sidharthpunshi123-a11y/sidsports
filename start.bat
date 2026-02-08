@echo off
REM Sports Betting Backend - Quick Start Script (Windows)

echo ========================================
echo Sports Betting Backend - Quick Start
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.9 or higher.
    pause
    exit /b 1
)

echo Python found
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

REM Create .env if it doesn't exist
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo Please edit .env and add your ODDS_API_KEY
    echo Get a free key at: https://the-odds-api.com
    echo.
)

REM Initialize database
echo Initializing database...
python -c "from app.database import init_db; init_db()" 2>nul
if errorlevel 1 (
    echo Warning: Database initialization failed
    echo Make sure PostgreSQL is running
) else (
    echo Database initialized successfully
)

echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo Next steps:
echo   1. Edit .env and add your ODDS_API_KEY
echo   2. Ensure PostgreSQL is running
echo   3. Run: python -m uvicorn app.main:app --reload
echo   4. Visit: http://localhost:8000/docs
echo.
echo Alternative: Use Docker
echo   docker-compose up
echo.
pause
