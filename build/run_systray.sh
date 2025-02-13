#!/usr/bin/env bash

# Set environment variables explicitly with a fallback
if [ -z "$DISPLAY" ]; then
    export DISPLAY=:0
    echo "DISPLAY variable was not set. Setting DISPLAY=:0"
else
    echo "DISPLAY is set to $DISPLAY"
fi

if [ -z "$XAUTHORITY" ]; then
    export XAUTHORITY="$HOME/.Xauthority"
    echo "XAUTHORITY variable was not set. Setting XAUTHORITY=$HOME/.Xauthority"
else
    echo "XAUTHORITY is set to $XAUTHORITY"
fi

# Determine if using system-wide or local virtual environment
if [ -f "/usr/local/bin/mastpysystray" ]; then
    VENV_DIR="/lib/python-venvs/systray-env"
    ASSETS_DIR="/usr/local/share/systray/assets"
    SRC_DIR="/usr/local/share/systray/src"
else
    # Set DIR to the script's directory
    DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    VENV_DIR="$DIR/../venv"
    ASSETS_DIR="$DIR/../assets"
    SRC_DIR="$DIR/../src"
fi

# Check if the virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Running install script..."
    bash "$DIR/install.sh"
fi

# Ensure the assets directory is accessible
if [ ! -d "$ASSETS_DIR" ]; then
    echo "Assets directory not found at $ASSETS_DIR."
    exit 1
fi

# Function to check if the X server is running
check_x_server() {
    if xset q > /dev/null 2>&1; then
        echo "X server is running."
        return 0
    else
        echo "X server is not running yet."
        return 1
    fi
}

# Wait until the X server is running
until check_x_server; do
    echo "Waiting for X server to start..."
    sleep 1
done

while true; do
    if pgrep -x "dwm" > /dev/null; then
        echo "DWM is running. Starting systray..."

        # Run the main Python script using absolute paths
        LOGFILE="/tmp/systray_output.log"
        "$VENV_DIR/bin/python3" "$SRC_DIR/main.py" --assets-dir="$ASSETS_DIR" "$@" > "$LOGFILE" 2>&1 &
        SYSTRAY_PID=$!
        echo "Systray application started with PID $SYSTRAY_PID. Logs are being written to $LOGFILE"

        # Monitor DWM and kill systray if DWM stops
        while pgrep -x "dwm" > /dev/null; do
            if ! kill -0 $SYSTRAY_PID 2>/dev/null; then
                echo "Systray process has terminated unexpectedly."
                break
            fi
            sleep 1
        done

        echo "DWM has stopped or Systray crashed. Killing systray..."
        kill $SYSTRAY_PID 2>/dev/null
        echo "Waiting for DWM to restart..."
    else
        echo "Waiting for DWM to start..."
        sleep 1
    fi
done
