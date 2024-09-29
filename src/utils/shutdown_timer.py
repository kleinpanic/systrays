#!/usr/bin/env python3
# src/utils/shutdown_timer.py

import tkinter as tk
import subprocess

shutdown_canceled = False

def shutdown_system():
    global shutdown_canceled
    if not shutdown_canceled:
        subprocess.run(['sudo', 'poweroff'])

def start_shutdown_timer(seconds):
    global shutdown_canceled
    shutdown_canceled = False

    def countdown(remaining):
        if shutdown_canceled:
            root.quit()
            return
        if remaining > 0:
            time_label.config(text=f"Shutting down in {remaining} seconds...")
            root.after(1000, countdown, remaining - 1)
        else:
            root.quit()
            shutdown_system()

    def cancel_shutdown():
        global shutdown_canceled
        shutdown_canceled = True
        root.quit()

    root = tk.Tk()
    root.title("Shutdown Timer")
    root.geometry("300x100")

    time_label = tk.Label(root, text=f"Shutting down in {seconds} seconds...")
    time_label.pack(pady=10)
    
    cancel_button = tk.Button(root, text="Cancel", command=cancel_shutdown)
    cancel_button.pack(pady=10)

    # Start the countdown
    root.after(1000, countdown, seconds)

    root.mainloop()
    root.destroy()
