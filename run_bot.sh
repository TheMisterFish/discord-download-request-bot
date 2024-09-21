#!/bin/bash

# Function to check Python version
check_python_version() {
    if command -v python3 >/dev/null 2>&1; then
        python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
        if [ "$(printf '%s\n' "3.10.6" "$python_version" | sort -V | head -n1)" = "3.10.6" ]; then
            return 0
        fi
    fi
    return 1
}

# Install Python 3.10.6 if not present
if ! check_python_version; then
    echo "Python 3.10.6 or higher not found. Installing..."
    sudo apt update
    sudo apt install -y software-properties-common
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt update
    sudo apt install -y python3.10 python3.10-venv python3.10-dev
fi

# Create virtual environment
VENV_NAME="archiver_bot_venv"
python3.10 -m venv $VENV_NAME
source $VENV_NAME/bin/activate

# Install requirements
pip install -r requirements.txt

# Function to run the bot
run_bot() {
    while true; do
        python3 bot.py
        echo "Bot crashed. Restarting in 10 seconds. Press Enter to stop."
        read -t 10 input
        if [ -n "$input" ]; then
            echo "User input detected. Stopping the bot."
            exit 0
        fi
        echo "Restarting the bot..."
    done
}

# Run the bot in a detached screen session
screen -dmS archive_bot_session bash -c "$(declare -f run_bot); run_bot"

# Display information message
echo "##############################################################################################"
echo ""
echo "Archive Bot is now running in a detached screen session named 'archive_bot_session' with auto-restart."
echo "To attach to the session, use: screen -r archive_bot_session"
echo "To detach from the session once attached, press Ctrl+A, then D"
echo "When the bot crashes, you have 10 seconds to press Enter to stop it completely."
echo ""
echo "##############################################################################################"