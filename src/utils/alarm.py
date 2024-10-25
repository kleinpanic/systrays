import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os
import time
import signal
import sounddevice as sd
import numpy as np
from multiprocessing import Process, Manager

def display_alarm_tool(main_app):
    root = tk.Toplevel(main_app.root)
    root.title("Alarm")
    root.geometry("400x400")
    root.configure(bg='#17153B')

    main_app.alarm_window_open = True  # Indicate the window is open

    def close_alarm_window(event=None):
        main_app.alarm_window_open = False
        root.destroy()

    root.bind('<q>', close_alarm_window)
    root.bind('<Q>', close_alarm_window)
    root.bind('<Escape>', close_alarm_window)

    # Top frame to set future date and time
    top_frame = tk.Frame(root, bg='#2E236C')
    top_frame.pack(fill=tk.X, padx=10, pady=10)

    tk.Label(top_frame, text="Set Alarm Date (YYYY-MM-DD)", bg='#2E236C', fg='#C8ACD6').pack(pady=5)
    date_entry = tk.Entry(top_frame, width=20)
    date_entry.pack(pady=5)

    tk.Label(top_frame, text="Set Alarm Time (HH:MM:SS)", bg='#2E236C', fg='#C8ACD6').pack(pady=5)
    time_entry = tk.Entry(top_frame, width=20)
    time_entry.pack(pady=5)

    set_alarm_button = ttk.Button(top_frame, text="Set Alarm", command=lambda: set_alarm(root, date_entry.get(), time_entry.get(), main_app))
    set_alarm_button.pack(pady=5)

    # Bottom frame for active alarms
    bottom_frame = tk.Frame(root, bg='#2E236C')
    bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Assign alarm_listbox to main_app so it can be accessed from other methods
    main_app.alarm_listbox = tk.Listbox(bottom_frame, height=10, bg='#433D8B', fg='#C8ACD6')
    main_app.alarm_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    cancel_alarm_button = ttk.Button(bottom_frame, text="Cancel Selected Alarm", command=lambda: cancel_alarm(main_app.alarm_listbox, main_app))
    cancel_alarm_button.pack(pady=5)

def set_alarm(root, alarm_date, alarm_time, main_app):
    # Validate the future time and date
    try:
        alarm_datetime = datetime.strptime(f"{alarm_date} {alarm_time}", "%Y-%m-%d %H:%M:%S")
        current_time = datetime.now()

        if alarm_datetime > current_time:
            # Using Manager for inter-process communication (shared object)
            manager = Manager()
            alarm_trigger = manager.Value('i', 0)  # 0 means alarm is not triggered

            # Fork a new process for countdown
            alarm_proc = Process(target=countdown_to_alarm, args=(alarm_datetime, alarm_trigger))
            alarm_proc.start()

            # Store alarm info in main_app and update the alarm list (add 'handled' flag)
            alarm = {'datetime': alarm_datetime, 'proc': alarm_proc, 'trigger': alarm_trigger, 'handled': False}
            main_app.alarm_list.append(alarm)
            update_alarm_listbox(main_app)

            # Periodically check for triggered alarm
            root.after(1000, lambda: check_for_alarm(main_app))
        else:
            messagebox.showwarning("Invalid Time", "Please set a future date and time.")  # Popup notification
    except ValueError:
        messagebox.showerror("Invalid Format", "Please use YYYY-MM-DD for date and HH:MM:SS for time.")  # Popup notification for format error

def countdown_to_alarm(alarm_datetime, alarm_trigger):
    # Calculate the number of seconds until the alarm time
    current_time = datetime.now()
    total_seconds = (alarm_datetime - current_time).total_seconds()

    # Sleep until the alarm time
    time.sleep(total_seconds)

    # Set alarm trigger when time is up
    alarm_trigger.value = 1

def check_for_alarm(main_app):
    # Check if any alarm has been triggered and not yet handled
    for alarm in main_app.alarm_list:
        if alarm['trigger'].value == 1 and not alarm['handled']:
            # Show the popup and play the alarm tone
            show_alarm_popup(main_app, alarm)
            play_alarm_tone()
            
            # Mark the alarm as handled so it doesn't trigger again
            alarm['handled'] = True

    # Keep checking for triggered alarms every second
    main_app.root.after(1000, lambda: check_for_alarm(main_app))

def show_alarm_popup(main_app, alarm):
    # Show popup immediately
    popup = tk.Toplevel(main_app.root)
    popup.title("Alarm Alert")
    popup.geometry("200x100")
    popup.configure(bg='#17153B')

    tk.Label(popup, text="Alarm is going off!", bg='#17153B', fg='#C8ACD6').pack(pady=10)

    stop_button = ttk.Button(popup, text="Stop Alarm", command=lambda: stop_alarm(main_app, alarm, popup))
    stop_button.pack(pady=10)

def play_alarm_tone():
    duration = 10.0  # Play tone for 10 seconds or loop continuously until stopped
    frequency = 440.0  # A4 note frequency in Hz
    sample_rate = 44100  # Sample rate in Hz

    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = 0.5 * np.sin(2 * np.pi * frequency * t)

    # Start playing tone without waiting for completion
    sd.play(tone, samplerate=sample_rate)

def stop_alarm(main_app, alarm, popup):
    sd.stop()  # Stop the alarm sound
    popup.destroy()  # Close the alarm popup

    # Stop the alarm process
    alarm['proc'].terminate()

    # Remove alarm from the list and update listbox safely
    if alarm in main_app.alarm_list:
        main_app.alarm_list.remove(alarm)
        update_alarm_listbox(main_app)

def cancel_alarm(active_alarms_listbox, main_app):
    selected_index = active_alarms_listbox.curselection()
    if selected_index:
        selected_alarm = main_app.alarm_list[selected_index[0]]
        selected_alarm['proc'].terminate()  # Kill the alarm process
        main_app.alarm_list.pop(selected_index[0])  # Remove from the list
        update_alarm_listbox(main_app)

def update_alarm_listbox(main_app):
    # Update the listbox that displays active alarms
    main_app.alarm_listbox.delete(0, tk.END)
    for alarm in main_app.alarm_list:
        main_app.alarm_listbox.insert(tk.END, f"Alarm: {alarm['datetime']} | PID: {alarm['proc'].pid}")
