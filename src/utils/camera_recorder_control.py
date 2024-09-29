# utils/camera_recorder_control.py

import os
import subprocess
import time


# Global variables to store the PIDs
camera_pid = None
screenrecorder_pid = None

def toggle_camera():
    global camera_pid

    if camera_pid is None:
        # Start the camera process
        process = subprocess.Popen(['/usr/local/bin/camera-op'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        camera_pid = process.pid
        print(f"Camera started with PID {camera_pid}")
        return "Quit Camera"
    else:
        # Stop the camera process
        os.kill(camera_pid, 15)  # Try to terminate the process
        time.sleep(3)
        # Check if the process is still running
        try:
            os.kill(camera_pid, 0)
        except OSError:
            print(f"Camera with PID {camera_pid} has been successfully terminated.")
        else:
            os.kill(camera_pid, 9)  # Force kill if still running
            print(f"Camera with PID {camera_pid} was forcefully terminated.")
        camera_pid = None
        return "Start Camera"

def toggle_screenrecorder():
    global screenrecorder_pid

    if screenrecorder_pid is None:
        # Start the screen recorder process
        process = subprocess.Popen(['/usr/local/bin/start_screenrecorder'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        screenrecorder_pid = process.pid
        print(f"Screen Recorder started with PID {screenrecorder_pid}")
        return "Quit Screen Recorder"
    else:
        # Stop the screen recorder process
        os.kill(screenrecorder_pid, 15)  # Try to terminate the process
        time.sleep(3)
        # Check if the process is still running
        try:
            os.kill(screenrecorder_pid, 0)
        except OSError:
            print(f"Screen Recorder with PID {screenrecorder_pid} has been successfully terminated.")
        else:
            os.kill(screenrecorder_pid, 9)  # Force kill if still running
            print(f"Screen Recorder with PID {screenrecorder_pid} was forcefully terminated.")
        screenrecorder_pid = None
        return "Start Screen Recorder"
