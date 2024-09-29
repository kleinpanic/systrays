#!/usr/bin/env bash

# Find the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Determine if this is a system-wide or local installation or both
local_install=false
global_install=false

if [ -d "$DIR/../venv" ]; then
    echo "Local installation detected."
    local_install=true
fi

if [ -d "/lib/python-venvs/systray-env" ]; then
    echo "System-wide installation detected."
    global_install=true
fi

# Uninstall local installation
if [ "$local_install" = true ]; then
    VENV_DIR="$DIR/../venv"
    RUN_SCRIPT="$DIR/run_systray.sh"
    UNINSTALL_SCRIPT="$DIR/uninstall.sh"
    ASSETS_DIR="$DIR/../assets"
    SRC_DIR="$DIR/../src"

    echo "Uninstalling local installation..."

    # Remove the virtual environment
    if [ -d "$VENV_DIR" ]; then
        echo "Removing virtual environment..."
        rm -rf "$VENV_DIR"
    fi

    # Remove the run script
    if [ -f "$RUN_SCRIPT" ]; then
        echo "Removing run script..."
        rm "$RUN_SCRIPT"
    fi

    # Remove the uninstall script
    if [ -f "$UNINSTALL_SCRIPT" ]; then
        echo "Removing uninstall script..."
        rm "$UNINSTALL_SCRIPT"
    fi

    # Optionally remove the assets and src directories
    if [ -d "$ASSETS_DIR" ]; then
        echo "Removing assets directory..."
        rm -rf "$ASSETS_DIR"
    fi

    if [ -d "$SRC_DIR" ]; then
        echo "Removing src directory..."
        rm -rf "$SRC_DIR"
    fi
fi

# Uninstall system-wide installation
if [ "$global_install" = true ]; then
    VENV_DIR="/lib/python-venvs/systray-env"
    RUN_SCRIPT="/usr/local/bin/mastpysystray"
    UNINSTALL_SCRIPT="/usr/local/bin/uninstall_systray.sh"
    ASSETS_DIR="/usr/local/share/systray/assets"
    SRC_DIR="/usr/local/share/systray/src"
    SERVICE_FILE="$HOME/.config/systemd/user/mastpysystray.service"

    echo "Uninstalling system-wide installation..."

    # Remove the virtual environment
    if [ -d "$VENV_DIR" ]; then
        echo "Removing virtual environment..."
        sudo rm -rf "$VENV_DIR"
    fi

    # Remove the run script
    if [ -f "$RUN_SCRIPT" ]; then
        echo "Removing run script..."
        sudo rm "$RUN_SCRIPT"
    fi

    # Remove the uninstall script
    if [ -f "$UNINSTALL_SCRIPT" ]; then
        echo "Removing uninstall script..."
        sudo rm "$UNINSTALL_SCRIPT"
    fi

    # Remove the assets and src directories
    if [ -d "$ASSETS_DIR" ]; then
        echo "Removing assets directory..."
        sudo rm -rf "$ASSETS_DIR"
    fi

    if [ -d "$SRC_DIR" ]; then
        echo "Removing src directory..."
        sudo rm -rf "$SRC_DIR"
    fi

    # Remove the systemd user service file and reload daemon
    if [ -f "$SERVICE_FILE" ]; then
        echo "Removing systemd user service file..."
        systemctl --user stop mastpysystray.service
        systemctl --user disable mastpysystray.service
        rm "$SERVICE_FILE"
        systemctl --user daemon-reload
    fi
fi

# Optionally remove the log file
LOGFILE="/tmp/systray_output.log"
if [ -f "$LOGFILE" ]; then
    echo "Removing log file..."
    rm "$LOGFILE"
fi

echo "Uninstallation complete."
