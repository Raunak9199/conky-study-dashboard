#!/usr/bin/env bash
set -e

# Check if the virtual environment exists
if [ ! -d ".venv" ]; then
    read -p "Virtual environment (.venv) not found. Do you want to create it and install dependencies? (y/n): " choice
    case "$choice" in 
      y|Y ) 
        echo "Creating virtual environment..."
        python3 -m venv .venv
        .venv/bin/pip install --upgrade pip
        .venv/bin/pip install PyQt5 "qrcode[pil]"
        ;;
      * ) 
        echo "Skipping installation. Cannot run without dependencies. Exiting."
        exit 1
        ;;
    esac
fi

# Run the app in the background (detaches from the terminal)
echo "Starting Study Dashboard in the background..."
nohup .venv/bin/python dashboard_app.py >/tmp/study-dashboard.log 2>&1 &
