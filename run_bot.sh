#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if screen is installed
if ! command_exists screen; then
    echo "Screen is not installed. Please install it manually:"
    echo "sudo apt-get update && sudo apt-get install screen -y"
    exit 1
fi

# Check if pip3 is installed
if ! command_exists pip3; then
    echo "pip3 is not installed or not in PATH. Attempting to install..."
    sudo apt-get update
    sudo apt-get install python3-pip -y
    
    # Add pip3 to PATH if it's not already there
    export PATH="$PATH:$HOME/.local/bin"
fi

# Verify pip3 installation
if ! command_exists pip3; then
    echo "Failed to install or locate pip3. Please install it manually:"
    echo "sudo apt-get update && sudo apt-get install python3-pip -y"
    exit 1
fi

# Install requirements
echo "Installing requirements..."
pip3 install -r requirements.txt

# Create a new detached screen session named "bot_session"
screen -dmS bot_session bash -c '
    while true
    do
        echo "Starting bot.py..."
        python3 bot.py
        echo "Archiver Bot crashed or stopped. Restarting in 10 seconds..."
        echo "Press Enter within 10 seconds to stop the Archiver Bot and exit..."
        if read -t 10 -r; then
            echo "Admin input detected. Stopping the Archiver Bot and exiting..."
            exit 0
        fi
    done
'
echo "##############################################################################################"
echo ""
echo "Archiver Bot is now running in a detached screen session named 'bot_session' with auto-restart."
echo "To attach to the session, use: screen -r bot_session"
echo "To detach from the session once attached, press Ctrl+A, then D"
echo "When the bot crashes, you have 10 seconds to press Enter to stop it completely."
echo ""
echo "##############################################################################################"