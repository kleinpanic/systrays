#!/usr/bin/env bash

# Function to check if the user is using Xorg/Xserver or Wayland
check_display_server() {
    if [ "$XDG_SESSION_TYPE" = "x11" ]; then
        echo "Xorg detected."
        return 0
    elif [ "$XDG_SESSION_TYPE" = "wayland" ]; then
        echo "Wayland detected."
        return 1
    elif pgrep -x "Xorg" > /dev/null; then
        echo "Xorg detected."
        return 0
    elif pgrep -x "weston" > /dev/null || pgrep -x "gnome-shell" > /dev/null; then
        echo "Wayland detected."
        return 1
    else
        if [[ "$(systemctl get-default)" == "graphical.target" ]]; then
            echo "Graphical environment detected but unable to determine display server."
            return 2
        else
            echo "No graphical environment detected."
            exit 1
        fi
    fi
}

# Run the check
check_display_server
result=$?

# Handle Wayland scenario
if [ $result -eq 1 ]; then
    read -p "Do you want to download the Wayland equivalent? [Y/n] " choice
    choice=${choice:-Y}  # Default to 'Y' if the user presses enter
    if [[ "$choice" =~ ^[Yy]$ ]]; then
        echo "Wayland installation logic will be added here."
        # Add Wayland-specific installation logic here
        exit 0
    else
        echo "Exiting installation."
        exit 1
    fi
fi

# Handle Xorg scenario
if [ $result -eq 0 ]; then
    echo "Do you want to install the program locally or system-wide?"
    echo "0) Cancel"
    echo "1) Locally (current user)"
    echo "2) System-wide (requires sudo)"
    read -p "Choose an option [0/1/2]: " install_option

    # Check if the input is valid
    if [[ -z "$install_option" || ! "$install_option" =~ ^[012]$ ]]; then
        echo "Invalid option. Exiting."
        exit 1
    fi

    # If the user chooses to cancel
    if [ "$install_option" -eq 0 ]; then
        echo "Installation canceled."
        exit 0
    fi

    # Find the directory where the script is located
    DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

    if [ "$install_option" -eq 1 ]; then
        # Local installation
        VENV_DIR="$DIR/../venv"
        ASSETS_DIR="$DIR/../assets"
        SRC_DIR="$DIR/../src"

        # Check if the virtual environment exists, if not, create it
        if [ ! -d "$VENV_DIR" ]; then
            echo "Creating virtual environment..."
            python3 -m venv "$VENV_DIR"
        fi

        # Install the required packages
        echo "Installing dependencies..."
        "$VENV_DIR/bin/pip" install -r "$DIR/requirements.txt"

        # Make the wrapper script executable
        chmod +x "$DIR/run_systray.sh"
        
        # Make the uninstall script executable
        chmod +x "$DIR/uninstall.sh"

        # Ensure the assets directory is accessible
        echo "Ensuring assets directory is accessible..."
        if [ ! -d "$ASSETS_DIR" ]; then
            echo "Assets directory not found at $ASSETS_DIR."
            exit 1
        fi

        echo "Local install complete. Manually run the startup script."

    elif [ "$install_option" -eq 2 ]; then
        # System-wide installation
        VENV_DIR="/lib/python-venvs/systray-env"
        ASSETS_DIR="/usr/local/share/systray/assets"
        SRC_DIR="/usr/local/share/systray/src"
        
        # Create a directory for system-wide Python virtual environments if it doesn't exist
        if [ ! -d "/lib/python-venvs" ]; then
            sudo mkdir -p /lib/python-venvs
            sudo chmod 755 /lib/python-venvs
        fi

        # Check if the virtual environment exists, if not, create it
        if [ ! -d "$VENV_DIR" ]; then
            echo "Creating system-wide virtual environment..."
            sudo python3 -m venv "$VENV_DIR"
        fi

        # Install the required packages
        echo "Installing dependencies system-wide..."
        sudo "$VENV_DIR/bin/pip" install -r "$DIR/requirements.txt"

        # Create the necessary directories and copy the src/ and assets/
        sudo mkdir -p "$ASSETS_DIR"
        sudo mkdir -p "$SRC_DIR"
        sudo cp -r "$DIR/../assets/"* "$ASSETS_DIR/"
        sudo cp -r "$DIR/../src/"* "$SRC_DIR/"

        # Create a mastpysystray script with updated paths
        sudo cp "$DIR/run_systray.sh" "/usr/local/bin/mastpysystray"
        sudo chmod +x "/usr/local/bin/mastpysystray"

        # Move the uninstall script to a system-wide location
        sudo cp "$DIR/uninstall.sh" "/usr/local/bin/uninstall_systray.sh"
        sudo chmod +x "/usr/local/bin/uninstall_systray.sh"

        echo "Global install complete. Run 'mastpysystray' from /usr/local/bin or in shell."

        # Systemd user service setup
        echo "Would you like to set up the systemd user service?"
        echo "1) Manually"
        echo "2) Automatically"
        read -p "Choose an option [1/2]: " service_option

        # Validate service option input
        if [[ -z "$service_option" || ! "$service_option" =~ ^[12]$ ]]; then
            echo "Invalid option. Exiting."
            exit 1
        fi

        if [ "$service_option" -eq 1 ]; then
            echo "Read mastpysystray.service and set it up to ~/.config/systemd/user/."
            exit 0
        elif [ "$service_option" -eq 2 ]; then
            # Ensure the user systemd directory exists
            mkdir -p "$HOME/.config/systemd/user"

            # Automatically set up the systemd service
            SERVICE_FILE="$HOME/.config/systemd/user/mastpysystray.service"
            cp "$DIR/mastpysystray.service" "$SERVICE_FILE"
            systemctl --user daemon-reload
            systemctl --user enable mastpysystray.service
            systemctl --user restart mastpysystray.service

            # Check service status
            STATUS=$(systemctl --user is-active mastpysystray.service)
            if [ "$STATUS" != "active" ]; then
                echo "Error: mastpysystray.service failed to start. Check systemctl --user status mastpysystray.service for more information."
            else
                echo "mastpysystray.service was successfully set up and started."
            fi
        fi
    fi
fi
