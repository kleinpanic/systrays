#!/usr/bin/env python3
# src/main.py

import os
import pystray
from pystray import MenuItem as item, Menu
from PIL import Image, ImageDraw
import subprocess
import threading
import signal
import psutil
import tkinter as tk
from tkinter import messagebox
from utils.sudo_prompt import prompt_sudo_password
from utils.shutdown_timer import start_shutdown_timer
from utils.conky import toggle_conky, check_conky_status
from utils.bluetooth_control import show_bluetooth_control
from utils.xrandr_tool import show_xrandr_control
from utils.brightness_slider import show_brightness_slider  
from utils.camera_recorder_control import toggle_camera, toggle_screenrecorder
from utils.screenshot_tool import display_screenshot_tool  # Import the screenshot tool

# Nerdfont glyphs for each action
GLYPHS = {
    "conky": "",
    "bluetooth": "",
    "power_off": "",
    "reboot": "",
    "display": "",
    "brightness": "",
    "camera": "",
    "screenrecorder": "",
    "screenshot": "",  
    "quit": ""  
}

# Global variables for PIDs
camera_pid = None
screenrecorder_pid = None
systray_pid = os.getpid()  # Record the PID of the systray process

def create_image():
    # Define possible paths for the systray icon
    local_path = os.path.join(os.path.dirname(__file__), '../assets/systray-icon.png')
    system_path = '/usr/local/share/systray/assets/systray-icon.png'

    try:
        # Try to load the image from the local installation path
        if os.path.exists(local_path):
            image = Image.open(local_path)
        # If not found, try the system-wide installation path
        elif os.path.exists(system_path):
            image = Image.open(system_path)
        else:
            raise FileNotFoundError("Systray icon not found in any known locations.")

        # Resize to fit the systray, typically 16x16 or 24x24
        image = image.resize((24, 24), Image.LANCZOS)  # Adjust the size as needed
        return image

    except Exception as e:
        print(f"Error loading image: {e}")
        # Fallback to a plain white image with a black rectangle if loading fails
        width = 24
        height = 24
        image = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        draw.rectangle(
            (width // 4, height // 4, width * 3 // 4, height * 3 // 4),
            fill='black')
        return image

def confirm_action(action_name):
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    result = messagebox.askyesno(f"{action_name} Confirmation", f"Are you sure you want to {action_name.lower()}?")
    root.destroy()
    return result

def on_toggle_conky(icon, item):
    toggle_conky()  # Toggle Conky state
    update_menu(icon)  # Update the menu item text

def on_bluetooth_control(icon, item):
    show_bluetooth_control()

def on_power_off(icon, item):
    if confirm_action("Power Off"):
        if prompt_sudo_password("Power off"):
            print("Starting shutdown timer...")
            start_shutdown_timer(60)  # Start a 60-second shutdown timer
        else:
            print("Shutdown canceled or failed due to incorrect password.")
    else:
        print("Power off canceled by user.")

def on_reboot(icon, item):
    if confirm_action("Reboot"):
        if prompt_sudo_password("Reboot"):
            subprocess.run(['sudo', 'reboot'])
        else:
            print("Reboot canceled or failed due to incorrect password.")
    else:
        print("Reboot canceled by user.")

def on_xrandr_tool(icon, item):
    show_xrandr_control()

def on_brightness_slider(icon, item):
    show_brightness_slider()  # Call the function to show the brightness slider window

def on_toggle_camera(icon, item):
    new_label = toggle_camera()  # Toggle camera state
    item.text = f"{GLYPHS['camera']} {new_label}"  # Update menu item text

def on_toggle_screenrecorder(icon, item):
    new_label = toggle_screenrecorder()  # Toggle screen recorder state
    item.text = f"{GLYPHS['screenrecorder']} {new_label}"  # Update menu item text

def on_screenshot_tool(icon, item):
    display_screenshot_tool()  # Display the screenshot tool window

def kill_process_tree(pid):
    try:
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            child.terminate()
        parent.terminate()
        gone, still_alive = psutil.wait_procs(parent.children(recursive=True), timeout=3)
        for p in still_alive:
            p.kill()  # Force kill if still running
        parent.kill()
        print(f"Process tree for PID {pid} terminated successfully.")
    except psutil.NoSuchProcess:
        print(f"No such process with PID {pid} found.")

def find_wrapper_pid():
    try:
        # Assuming the wrapper script is named `run_systray.sh` and is running as a bash process
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if 'bash' in proc.info['name'] and 'run_systray.sh' in proc.info['cmdline']:
                return proc.info['pid']
    except Exception as e:
        print(f"Error finding wrapper PID: {e}")
    return None

def stop_service_if_exists(service_name):
    try: 
        result = subprocess.run(
                ["systemctl", "--user", "status", service_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
        )
        if result.returncode == 0:
            print(f"Stopping service: {service_name}")
            subprocess.run(["systemctl", "--user", "stop", service_name])
            print(f"Service {service_name} stopped successfully.")
        else:
            print(f"Service {service_name} does not exist, or is inactive")
    except Exception as e:
        print(f"An error occured as: {e}")

def on_quit_systray(icon, item):
    if confirm_action("Quit Systray"):
        # Kill camera and screen recorder if they are running
        if camera_pid:
            kill_process_tree(camera_pid)
        if screenrecorder_pid:
            kill_process_tree(screenrecorder_pid)
        
        # Try to find and kill the wrapper process
        wrapper_pid = find_wrapper_pid()
        if wrapper_pid:
            kill_process_tree(wrapper_pid)
        else:
            print("Wrapper PID not found. Attempting to kill main.py script.")
            kill_process_tree(systray_pid)
        
        icon.stop()  # Stop the systray Icon
        service_name = "mastpysystray.service"
        stop_service_if_exists(service_name)
    else:
        print("Quit action canceled by user.")

def update_menu(icon):
    icon.menu = Menu(
        item(f"{GLYPHS['conky']} {check_conky_status()}", on_toggle_conky),
        item(f"{GLYPHS['bluetooth']} Bluetooth Control", on_bluetooth_control),
        item(f"{GLYPHS['camera']} Start Camera", on_toggle_camera),
        item(f"{GLYPHS['screenrecorder']} Start Screen Recorder", on_toggle_screenrecorder),
        item(f"{GLYPHS['screenshot']} Screenshot Tool", on_screenshot_tool),  # Screenshot tool added below screen recording
        item(f"{GLYPHS['power_off']} Power Off", on_power_off),
        item(f"{GLYPHS['reboot']} Reboot", on_reboot),
        item(f"{GLYPHS['display']} Display Settings", on_xrandr_tool),
        item(f"{GLYPHS['brightness']} Brightness Slider", on_brightness_slider),
        item(f"{GLYPHS['quit']} Quit", on_quit_systray)  # Quit option at the bottom
    )
    icon.update_menu()

def periodic_update(icon):
    update_menu(icon)
    threading.Timer(5.0, periodic_update, [icon]).start()  # Refresh every 5 seconds

def setup_systray():
    pid = os.getpid()  # Get the current process ID
    icon = pystray.Icon("systray_icon", create_image(), f"MPyStray {pid}")  # Set title with PID
    icon.title = f"MPyStray {pid}"  # Ensure title is set (some platforms require this explicitly)
    update_menu(icon)  # Set up the initial menu
    periodic_update(icon)  # Start periodic updates to keep the menu in sync
    icon.run()

if __name__ == "__main__":
    setup_systray()
