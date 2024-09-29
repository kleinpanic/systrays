#!/usr/bin/env python3
# src/utils/brightness_slider.py

import tkinter as tk

def set_brightness(percentage):
    # Ensure the brightness is not set to 0; adjust to 1% minimum.
    if percentage == 0:
        percentage = 1

    brightness_value = int((percentage / 100) * 96000)
    with open('/sys/class/backlight/intel_backlight/brightness', 'w') as f:
        f.write(str(brightness_value))

def on_brightness_slider_change(value):
    percentage = int(value)
    set_brightness(percentage)

def close_on_keypress(event):
    if event.keysym in ['q', 'Escape']:
        event.widget.quit()  # Closes the window

def show_brightness_slider():
    root = tk.Tk()
    root.title("Brightness Control")
    root.geometry("300x100")

    # Bind 'q' and 'Esc' keys to close the window
    root.bind('<KeyPress-q>', lambda event: root.destroy())
    root.bind('<KeyPress-Escape>', lambda event: root.destroy())

    # Add the brightness slider
    brightness_slider = tk.Scale(
        root, from_=0, to=100, orient=tk.HORIZONTAL, length=250,
        label="Brightness", command=on_brightness_slider_change
    )
    brightness_slider.pack(pady=10)

    # Read the current brightness to set the slider's initial position
    with open('/sys/class/backlight/intel_backlight/brightness', 'r') as f:
        current_brightness = int(f.read().strip())
        current_percentage = int((current_brightness / 96000) * 100)
        brightness_slider.set(current_percentage)

    root.mainloop()

