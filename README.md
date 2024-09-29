# Systray Project for Xserver

This project is a Python-based systray application designed for the X server environment. It provides various system utilities and functionalities through a system tray icon, allowing you to easily manage Conky, Bluetooth settings, system power options, display settings, and more.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Systemd Service](#systemd-service)
- [Configuration](#configuration)
- [Output](#output)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Systray Icon**: Provides a system tray icon for easy access to various utilities.
- **Conky Management**: Start and stop Conky with a single click.
- **Bluetooth Control**: Easily manage Bluetooth settings.
- **System Power Options**: Access shutdown, reboot, and other power options.
- **Display Settings**: Control brightness and other display-related settings.
- **Screenshot Tool**: Capture screenshots using `scrot`.
- Lots of other shit i built my self i need to still address

## Requirements

### Software Dependencies

To run this systray application, the following software must be installed:

- **Operating System**: Linux with X server (X11)
- **Python**: Version 3.6 or higher
- **Nerd Fonts**: Ensure that a Nerd Font is installed and set as the default font for your terminal.
- **System Utilities**:
  - `brightnessctl`: For controlling screen brightness.
  - `scrot`: For capturing screenshots.
  - `conky`: For displaying system statistics.
  - Some funky wonky programs i built myself.

### Python Packages

The following Python packages are required:

- `pam`
- `pillow`
- `pycairo`
- `PyGObject`
- `pystray`
- `python-pam`
- `python-xlib`
- `six`
- `psutil`

### Optional Dependencies

If your system uses fingerprint authentication, it's recommended to have `fprintd` installed to enable fingerprint-based authentication.

### Installation of System Utilities

Install the required system utilities using your package manager:

# For Debian/Ubuntu-based systems
sudo apt update
sudo apt install brightnessctl scrot conky fonts-noto-color-emoji

# For Arch-based systems
fuck you sincerely

### installation
For the installion of this code navigation to the build directory and run the ./install script. 
Make sure it is executable. It will ask you if you want to do a system wide install or a local install.
1) Local install: 
   - This will make the bash wrapper run script executable, and it will make the uninstall script executable
   - The deeper logic of this defines the local paths ad shit but thats not really improtant to discuss. Read the code if you want.
1) Global install:
    - This will make the bash wrapper script executable. It will copy the bash wrapper script to your /usr/local/bin dir named as mastpysystray (Why? because i suck at naming shit)
    - This will also make the unistall script executable and move it to the usr/local/bin as uninstall_systray.sh or something like that.
    - Anyways the cooler shit of this code is that it comes with a systemd script that is hopefully portable. Ifyou choose global install you can have the option to create a systemd service to take care of the startup of this script for ya. This will copy it to the .config/systemd/user directory or make one if you dont have one. It will then reload the --user daemon, enable the service for startup, restart the service, check the status and reprot back to the user.
    - The reason this is bash wrapepr script that executes the python rather than just the python script itself is because 1) i like bash. 2) It allows me to easily manage the entire system, redirect its log output, and make sure that certain depencies are met before the python script is started. Trust me you can start the python3 script yourself but right now theres a lot of output that igotta clean up. 
      
      

