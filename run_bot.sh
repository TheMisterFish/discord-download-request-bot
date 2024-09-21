#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install the latest Python version available in Debian
install_latest_python() {
    echo "Updating Python and installing necessary packages..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-venv python3-pip
}

# Check if Python 3 is installed
if ! command_exists python3; then
    install_latest_python
else
    # If Python is installed but outdated, update it
    if python3 -c "import sys; exit(1) if sys.version_info < (3,6) else exit(0)"; then
        echo "Python version is 3.6 or higher."
    else
        echo "Python version is below 3.6. Updating..."
        install_latest_python
    fi
fi

# Get the Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Using Python version: $PYTHON_VERSION"

# Install python3-venv if not already installed
if ! dpkg -s python3-venv >/dev/null 2>&1; then
    echo "Installing python3-venv..."
    sudo apt-get install -y python3-venv
fi

# Create a virtual environment with the latest Python version
if [ ! -d "archive_bot_env" ]; then
    echo "Creating virtual environment for Archive Bot..."
    python3 -m venv archive_bot_env
fi

# Activate the virtual environment
source archive_bot_env/bin/activate

# Upgrade pip
python3 -m pip install --upgrade pip

# Check if screen is installed
if ! command_exists screen; then
    echo "Screen is not installed. Installing screen..."
    sudo apt-get update && sudo apt-get install screen -y
fi

# Install requirements
echo "Installing requirements..."
pip install --upgrade -r requirements.txt

# Create a new detached screen session named "archive_bot_session"
screen -dmS archive_bot_session bash -c '
    source archive_bot_env/bin/activate
    while true
    do
        echo "Starting bot.py..."
        python3 bot.py
        echo "Archive Bot crashed or stopped. Restarting in 10 seconds..."
        echo "Press Enter within 10 seconds to stop the Archive Bot and exit..."
        if read -t 10 -r; then
            echo "Admin input detected. Stopping the Archive Bot and exiting..."
            exit 0
        fi
    done
'

echo "##############################################################################################"
echo ""
echo "Archive Bot is now running in a detached screen session named 'archive_bot_session' with auto-restart."
echo "To attach to the session, use: screen -r archive_bot_session"
echo "To detach from the session once attached, press Ctrl+A, then D"
echo "When the bot crashes, you have 10 seconds to press Enter to stop it completely."
echo ""
echo "##############################################################################################"
