@echo off
echo ================================================
echo Monthly Close Checklist Automation Agent
echo ================================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
echo.

REM Check if .env file exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please copy .env.example to .env and configure your API keys.
    echo.
    pause
    exit /b 1
)

REM Generate sample data if not exists
if not exist "sample_data\complete_month_end" (
    echo Generating sample data...
    python generate_sample_data.py
    echo.
)

echo ================================================
echo Starting Application...
echo ================================================
echo.
echo FastAPI Backend will run on: http://localhost:8000
echo Streamlit Frontend will run on: http://localhost:8501
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop both servers
echo.

REM Start FastAPI in background
start "FastAPI Server" cmd /k "venv\Scripts\activate.bat && python -m uvicorn app.main:app --reload --port 8000"

REM Wait a bit for FastAPI to start
timeout /t 3 /nobreak > nul

REM Start Streamlit
start "Streamlit UI" cmd /k "venv\Scripts\activate.bat && streamlit run app/ui/streamlit_app.py"

echo.
echo ================================================
echo Application Started!
echo ================================================
echo Both servers are running in separate windows.
echo Close those windows to stop the servers.
echo.
pause
