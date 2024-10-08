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

# Get the full path of the current directory
CURRENT_DIR=$(pwd)

# Create virtual environment if it doesn't exist
VENV_NAME="archiver_bot"
VENV_PATH="$CURRENT_DIR/$VENV_NAME"
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating virtual environment: $VENV_NAME"
    $PYTHON_CMD -m venv $VENV_PATH
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Install requirements if requirements.txt exists
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Skipping package installation."
fi

# Create a wrapper script to run the bot with auto-restart
cat << EOF > run_bot_wrapper.sh
#!/bin/bash
source "$VENV_PATH/bin/activate"

run_bot() {
    python bot.py
}

while true; do
    run_bot
    echo "Bot stopped. Waiting 10 seconds before restarting. Press Ctrl+C to exit."
    for i in {10..1}; do
        echo -ne "\rRestarting in \$i seconds... "
        sleep 1
    done
    echo -e "\nRestarting bot..."
done
EOF

chmod +x run_bot_wrapper.sh

# Start the bot in a detached screen session
screen -dmS archive_bot bash -c './run_bot_wrapper.sh; exec bash'

# Display the information message
echo "##############################################################################################"
echo ""
echo "Archive Bot is now running in a detached screen session named 'archive_bot' with auto-restart."
echo "To attach to the session, use: screen -r archive_bot"
echo "To detach from the session once attached, press Ctrl+A, then D"
echo "When the bot stops, you have 10 seconds to press Ctrl+C to stop it completely."
echo ""
echo "##############################################################################################"

# Deactivate virtual environment
deactivate
