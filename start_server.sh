#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install dependencies if needed (optional, good for first run)
# pip install -r requirements.txt

# Start Gunicorn
# -w 4: Use 4 worker processes
# -b 0.0.0.0:5001: Bind to all interfaces on port 5001
# app:app : Module 'app' and callable 'app'
exec gunicorn -w 4 -b 0.0.0.0:5001 app:app
