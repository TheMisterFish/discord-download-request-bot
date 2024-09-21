#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install Python 3.8
install_python38() {
    echo "Installing Python 3.8..."
    sudo apt-get update
    sudo apt-get install -y software-properties-common
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt-get update
    sudo apt-get install -y python3.8 python3.8-venv python3.8-dev
}

# Check if Python 3.8 is installed
if ! command_exists python3.8; then
    install_python38
fi

# Create a virtual environment with Python 3.8
if [ ! -d "archive_bot_env" ]; then
    echo "Creating virtual environment for Archive Bot..."
    python3.8 -m venv archive_bot_env
fi

# Activate the virtual environment
source archive_bot_env/bin/activate

# Upgrade pip
pip install --upgrade pip

# Check if screen is installed
if ! command_exists screen; then
    echo "Screen is not installed. Please install it manually:"
    echo "sudo apt-get update && sudo apt-get install screen -y"
    exit 1
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
        python bot.py
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