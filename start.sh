#!/bin/bash

echo "================================================"
echo "Monthly Close Checklist Automation Agent"
echo "================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found!"
    echo "Please copy .env.example to .env and configure your API keys."
    echo ""
    exit 1
fi

# Generate sample data if not exists
if [ ! -d "sample_data/complete_month_end" ]; then
    echo "Generating sample data..."
    python generate_sample_data.py
    echo ""
fi

echo "================================================"
echo "Starting Application..."
echo "================================================"
echo ""
echo "FastAPI Backend will run on: http://localhost:8000"
echo "Streamlit Frontend will run on: http://localhost:8501"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Start FastAPI in background
python -m uvicorn app.main:app --reload --port 8000 &
FASTAPI_PID=$!

# Wait a bit for FastAPI to start
sleep 3

# Start Streamlit
streamlit run app/ui/streamlit_app.py

# Cleanup on exit
kill $FASTAPI_PID
