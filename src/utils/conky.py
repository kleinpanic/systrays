#!/usr/bin/env python3
# src/utils/conky.py

import subprocess
import os
import signal
import time

conky_pid = None  # Global variable to track the Conky process ID

def toggle_conky():
    global conky_pid

    if conky_pid is None:
        # Start Conky and let it fork to the background, then track the background PID
        process = subprocess.Popen(['conky'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Capture the output to find the forked PID
        for line in process.stderr:
            if b'forked to background, pid is' in line:
                conky_pid = line.decode().strip().split()[-1]
                print(f"Conky started with background PID {conky_pid}.")
                break

        return "Quit Conky"
    else:
        # Check if the Conky process is still running
        if not os.path.exists(f"/proc/{conky_pid}"):
            print(f"Conky with PID {conky_pid} could not be found (already stopped).")
            conky_pid = None
            return "Start Conky"
        
        # Attempt to gracefully terminate the Conky process
        try:
            os.kill(int(conky_pid), signal.SIGTERM)
            time.sleep(1)  # Give the process some time to terminate

            # Check if the process is still running
            if os.path.exists(f"/proc/{conky_pid}"):
                print(f"Conky with PID {conky_pid} did not terminate with SIGTERM, sending SIGKILL...")
                os.kill(int(conky_pid), signal.SIGKILL)  # Force quit if it's still running
            else:
                print(f"Conky with PID {conky_pid} stopped.")

        except ProcessLookupError:
            print(f"Conky with PID {conky_pid} could not be found.")
        except Exception as e:
            print(f"An error occurred while stopping Conky: {e}")
        
        conky_pid = None
        return "Start Conky"

def check_conky_status():
    global conky_pid
    if conky_pid is None or not conky_pid.isdigit() or not os.path.exists(f"/proc/{conky_pid}"):
        conky_pid = None
        return "Start Conky"
    else:
        return "Quit Conky"
