#!/bin/bash
# Run script for FastAPI application
# This ensures the virtual environment is used

cd "$(dirname "$0")"
source venv/bin/activate
cd market-insight
uvicorn main:app --reload --host 0.0.0.0 --port 8000

