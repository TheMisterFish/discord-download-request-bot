#!/bin/bash

# Check if Python 3.10 or newer is installed
if command -v python3.10 &>/dev/null; then
    PYTHON_CMD=python3.10
elif command -v python3 &>/dev/null && [[ $(python3 -c "import sys; print(sys.version_info >= (3, 10))") == "True" ]]; then
    PYTHON_CMD=python3
else
    echo "Python 3.10 or newer is required but not found. Please install it and try again."
    exit 1
fi

# Create virtual environment if it doesn't exist
VENV_NAME="archiver_bot"
if [ ! -d "$VENV_NAME" ]; then
    echo "Creating virtual environment: $VENV_NAME"
    $PYTHON_CMD -m venv $VENV_NAME
fi

# Activate virtual environment
source "$VENV_NAME/bin/activate"

# Install requirements if requirements.txt exists
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Skipping package installation."
fi

# Function to run the bot
run_bot() {
    while true; do
        screen -S archive_bot -dm python bot.py
        echo "Bot started. Waiting for potential crash..."
        
        # Wait for the screen session to end (bot crash)
        while screen -list | grep -q "archive_bot"; do
            sleep 1
        done
        
        echo "Bot crashed. Restarting in 10 seconds. Press Enter to stop."
        
        # Wait 10 seconds, allow interruption
        if read -t 10 -n 1; then
            echo "Interrupted by user. Exiting."
            exit 0
        fi
        echo "Restarting bot..."
    done
}

# Start the bot in the background
run_bot &

# Save the PID of the background process
BOT_PID=$!

# Display the information message
echo "##############################################################################################"
echo ""
echo "Archive Bot is now running in a detached screen session named 'archive_bot' with auto-restart."
echo "To attach to the session, use: screen -r archive_bot"
echo "To detach from the session once attached, press Ctrl+A, then D"
echo "When the bot crashes, you have 10 seconds to press Enter to stop it completely."
echo ""
echo "##############################################################################################"

# Wait for the bot process to finish
wait $BOT_PID

# Deactivate virtual environment
deactivate
