# utils/screenshot_tool.py

import os
import tkinter as tk
from tkinter import simpledialog
import subprocess
from datetime import datetime

# Function to check if scrot is installed
def check_scrot_installed():
    result = subprocess.run(["which", "scrot"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0

# Function to capture screenshots using scrot
def take_screenshot(option):
    home_dir = os.path.expanduser("~")
    screenshot_dir = os.path.join(home_dir, "Pictures", "screenshots")
    os.makedirs(screenshot_dir, exist_ok=True)
    
    # Create a temporary screenshot file
    temp_file_path = os.path.join(screenshot_dir, "temp_screenshot.png")

    # Execute the scrot command based on the user's choice
    if option == "Full Screen":
        subprocess.run(["scrot", temp_file_path])
    elif option == "Select Window":
        subprocess.run(["scrot", "-s", temp_file_path])

    # Prompt the user for a name after the screenshot is taken
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    name = simpledialog.askstring("Input", "Enter a name for the screenshot:", parent=root)
    
    # Generate the final filename
    if not name:
        current_date = datetime.now().strftime("%Y-%m-%d")
        counter = 1
        while True:
            file_path = os.path.join(screenshot_dir, f"Screenshot-{current_date}-{counter}.png")
            if not os.path.exists(file_path):
                break
            counter += 1
    else:
        file_path = os.path.join(screenshot_dir, f"{name}.png")

    # Rename the temporary screenshot file to the final file path
    os.rename(temp_file_path, file_path)

    root.destroy()

# Function to display the screenshot tool window
def display_screenshot_tool():
    # Check if scrot is installed
    if not check_scrot_installed():
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        messagebox.showerror("Error", "scrot is not installed.")
        root.destroy()
        return

    # Create the main window
    root = tk.Tk()
    root.title("Screenshot Tool")
    root.geometry("300x100")
    root.resizable(False, False)

    # Close the window on 'q' or 'Esc' key press
    def on_key_press(event):
        if event.keysym in ["q", "Escape"]:
            root.destroy()

    root.bind("<Key>", on_key_press)

    # Buttons for screenshot options
    tk.Button(root, text="Full Screen", command=lambda: (take_screenshot("Full Screen"), root.destroy())).pack(pady=10)
    tk.Button(root, text="Select Window", command=lambda: (take_screenshot("Select Window"), root.destroy())).pack(pady=10)
    tk.Button(root, text="Cancel", command=root.destroy).pack(pady=10)

    # Run the Tkinter event loop
    root.mainloop()

# If this script is executed, display the screenshot tool
if __name__ == "__main__":
    display_screenshot_tool()

