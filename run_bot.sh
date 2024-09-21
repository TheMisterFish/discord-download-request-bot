#!/bin/bash

# Check if screen is installed
if ! command -v screen &> /dev/null
then
    echo "Screen is not installed. Installing screen..."
    sudo apt-get update
    sudo apt-get install screen -y
fi

# Check if pip is installed
if ! command -v pip &> /dev/null
then
    echo "pip is not installed. Installing pip..."
    sudo apt-get update
    sudo apt-get install python3-pip -y
fi

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Create a new detached screen session named "bot_session"
screen -dmS bot_session bash -c '
    while true
    do
        echo "Starting Archiver Bot using bot.py..."
        python3 bot.py
        echo "Archiver Bot crashed or stopped. Restarting in 10 seconds..."
        echo "Press Enter within 10 seconds to stop the bot and exit..."
        if read -t 10 -r; then
            echo "Admin input detected. Stopping the bot and exiting..."
            exit 0
        fi
    done
'

echo "Archiver Bot is now running in a detached screen session named 'bot_session' with auto-restart."
echo "To attach to the session, use: screen -r bot_session"
echo "To detach from the session once attached, press Ctrl+A, then D"
echo "When the Archiver Bot crashes, you have 10 seconds to press Enter to stop it completely."