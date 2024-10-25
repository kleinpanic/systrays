import tkinter as tk
from tkinter import ttk
import datetime
import math
import time
import sounddevice as sd
import numpy as np
from utils.alarm import display_alarm_tool

class ClockApp:
    def __init__(self, root):
        self.root = root
        self.root.title(datetime.datetime.now().strftime("%A, %d/%m/%Y"))  # Date as the title
        self.alarm_list = []
        
        # Set window size and disable resizing
        self.root.geometry("350x250")
        self.root.resizable(False, False)

        self.create_widgets()
        self.bind_quit_keys()  

    def create_widgets(self):
        # Define color palette
        bg_color = '#17153B'      # Dark background
        frame_color = '#2E236C'   # Frame background
        button_bg = '#433D8B'     # Button background
        text_color = '#C8ACD6'    # Text color
        
        # Set window background
        self.root.configure(bg=bg_color)

        # Create frames for clock (left) and date/time info (right)
        self.frame_left = tk.Frame(self.root, width=150, height=150, bg=frame_color)  # Clock frame
        self.frame_left.grid(row=0, column=0, padx=10, pady=10)

        self.frame_right = tk.Frame(self.root, bg=frame_color)  # Info frame
        self.frame_right.grid(row=0, column=1, padx=10, pady=10)

        # Analog clock drawing
        self.canvas = tk.Canvas(self.frame_left, width=150, height=150, bg=frame_color, highlightthickness=0)
        self.canvas.pack()

        # Date and time labels
        self.date_label = tk.Label(self.frame_right, font=("Helvetica", 14), bg=frame_color, fg=text_color)
        self.date_label.grid(row=0, column=0, pady=5)

        self.time_label = tk.Label(self.frame_right, font=("Helvetica", 14), bg=frame_color, fg=text_color)
        self.time_label.grid(row=1, column=0, pady=5)

        # Configure button styles
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background=button_bg, foreground=text_color)
        style.map('TButton', background=[('active', '#433D8B')], foreground=[('active', text_color)])

        # Buttons for Alarm, Stopwatch, Timer with new color scheme
        self.alarm_button = ttk.Button(self.frame_right, text="Alarm", command=self.set_alarm)
        self.alarm_button.grid(row=2, column=0, pady=5)

        self.stopwatch_button = ttk.Button(self.frame_right, text="Stopwatch", command=self.start_stopwatch)
        self.stopwatch_button.grid(row=3, column=0, pady=5)

        self.timer_button = ttk.Button(self.frame_right, text="Timer", command=self.set_timer)
        self.timer_button.grid(row=4, column=0, pady=5)

        # Update clock and time every second
        self.update_clock()
        self.update_time()

    def update_clock(self):
        now = datetime.datetime.now()

        # Clear canvas
        self.canvas.delete("all")

        # Clock center and radius
        center_x = 75
        center_y = 75
        clock_radius = 60

        # Draw the clock face with numbers
        self.canvas.create_oval(center_x - clock_radius, center_y - clock_radius, center_x + clock_radius, center_y + clock_radius, outline="white", width=2)

        # Draw numbers around the clock face
        for i in range(1, 13):
            angle = math.radians(i * 30 - 90)  # Each number is 30 degrees apart
            x = center_x + (clock_radius - 15) * math.cos(angle)
            y = center_y + (clock_radius - 15) * math.sin(angle)
            self.canvas.create_text(x, y, text=str(i), font=("Helvetica", 10), fill="white")

        # Calculate angles for hour, minute, second hands
        second_angle = (now.second / 60) * 360
        minute_angle = (now.minute / 60) * 360 + (now.second / 60) * 6
        hour_angle = ((now.hour % 12) / 12) * 360 + (now.minute / 60) * 30

        # Convert angles to radians
        def get_coords(angle, length):
            angle_rad = math.radians(angle - 90)
            x = center_x + length * math.cos(angle_rad)
            y = center_y + length * math.sin(angle_rad)
            return x, y

        # Draw hands
        second_hand = get_coords(second_angle, 55)
        minute_hand = get_coords(minute_angle, 45)
        hour_hand = get_coords(hour_angle, 35)

        self.canvas.create_line(center_x, center_y, second_hand[0], second_hand[1], fill="red", width=1)
        self.canvas.create_line(center_x, center_y, minute_hand[0], minute_hand[1], fill="white", width=3)
        self.canvas.create_line(center_x, center_y, hour_hand[0], hour_hand[1], fill="white", width=4)

        # Call the update_clock again after 1000 ms
        self.root.after(1000, self.update_clock)

    def update_time(self):
        now = datetime.datetime.now()
        self.date_label.config(text=now.strftime("%d/%m/%Y"))  # Display date in numbers
        self.time_label.config(text=now.strftime("%H:%M:%S"))  # Display time in 24-hour format
        self.root.after(1000, self.update_time)

    # ======================= Stopwatch ==========================
    def start_stopwatch(self):
        sw_window = tk.Toplevel(self.root)
        sw_window.title("Stopwatch")
        sw_window.geometry("300x200")
        sw_window.configure(bg='#17153B')

        sw_time_label = tk.Label(sw_window, text="00:00.0", font=("Helvetica", 24), bg='#17153B', fg='#C8ACD6')
        sw_time_label.pack(pady=10)

        buttons_frame = tk.Frame(sw_window, bg='#17153B')
        buttons_frame.pack()

        lap_list = []
        running = False
        elapsed_time = 0
        last_time = 0
        lap_reset_button = None

        def update_time():
            nonlocal elapsed_time, last_time
            if running:
                now = time.time()
                elapsed_time += now - last_time
                last_time = now
                sw_time_label.config(text=self.format_dynamic_time(elapsed_time))
            sw_window.after(100, update_time)

        def toggle_stopwatch():
            nonlocal running, last_time
            if not running:
                running = True
                last_time = time.time()
                start_stop_button.config(text="Stop")
                lap_reset_button.config(text="Lap")
            else:
                running = False
                start_stop_button.config(text="Start")
                if lap_list:
                    lap_reset_button.config(text="Reset")


        def reset_stopwatch():
            nonlocal elapsed_time, running, lap_list
            elapsed_time = 0
            lap_list = []  # Clear the laps when reset is pressed
            lap_label.config(text="")
            sw_time_label.config(text="00:00.0")
            running = False
            start_stop_button.config(text="Start")
            lap_reset_button.config(text="Lap")

        def add_lap_or_reset():
            if running:
                add_lap()
            else:
                reset_stopwatch()

        def add_lap():
            if len(lap_list) < 5:
                lap_list.append(self.format_dynamic_time(elapsed_time))
                lap_label.config(text="\n".join(lap_list))

        def close_stopwatch(event=None):
            sw_window.destroy()

        # Bind q, Q, and Esc keys to quit the stopwatch window
        sw_window.bind('<q>', close_stopwatch)
        sw_window.bind('<Q>', close_stopwatch)
        sw_window.bind('<Escape>', close_stopwatch)

        start_stop_button = ttk.Button(buttons_frame, text="Start", command=toggle_stopwatch)
        start_stop_button.grid(row=0, column=0, padx=10, pady=10)

        lap_reset_button = ttk.Button(buttons_frame, text="Lap", command=add_lap_or_reset)
        lap_reset_button.grid(row=0, column=1, padx=10, pady=10)

        lap_label = tk.Label(sw_window, text="", bg='#17153B', fg='#C8ACD6')
        lap_label.pack(pady=10)

        update_time()

    def format_dynamic_time(self, time_value):
        if time_value >= 3600:  # If over 1 hour, use hours in format
            hours = int(time_value // 3600)
            minutes = int((time_value % 3600) // 60)
            seconds = int(time_value % 60)
            milliseconds = int((time_value % 1) * 10)
            return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds}"
        else:
            minutes = int(time_value // 60)
            seconds = int(time_value % 60)
            milliseconds = int((time_value % 1) * 10)
            return f"{minutes:02}:{seconds:02}.{milliseconds}"

    # ======================= Timer ==========================
    def set_timer(self):
        timer_window = tk.Toplevel(self.root)
        timer_window.title("Timer")
        timer_window.geometry("300x200")
        timer_window.configure(bg='#17153B')

        hour_var = tk.StringVar()
        minute_var = tk.StringVar()
        second_var = tk.StringVar()

        input_frame = tk.Frame(timer_window, bg='#17153B')
        input_frame.pack(pady=10)

        # Time input fields with labels
        tk.Label(input_frame, text="Hours", bg='#17153B', fg='#C8ACD6').grid(row=0, column=0, padx=5)
        hour_entry = ttk.Entry(input_frame, textvariable=hour_var, width=5)
        hour_entry.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Minutes", bg='#17153B', fg='#C8ACD6').grid(row=0, column=2, padx=5)
        minute_entry = ttk.Entry(input_frame, textvariable=minute_var, width=5)
        minute_entry.grid(row=0, column=3, padx=5)

        tk.Label(input_frame, text="Seconds", bg='#17153B', fg='#C8ACD6').grid(row=0, column=4, padx=5)
        second_entry = ttk.Entry(input_frame, textvariable=second_var, width=5)
        second_entry.grid(row=0, column=5, padx=5)

        buttons_frame = tk.Frame(timer_window, bg='#17153B')
        buttons_frame.pack(pady=10)

        running = False
        timer_time = 0

        def calculate_total_seconds():
            hours = int(hour_var.get() or 0)
            minutes = int(minute_var.get() or 0)
            seconds = int(second_var.get() or 0)
            return hours * 3600 + minutes * 60 + seconds

        def start_stop_timer():
            nonlocal running, timer_time
            if not running:
                timer_time = calculate_total_seconds()
                running = True
                start_stop_button.config(text="Stop")
                update_timer()
            else:
                running = False
                start_stop_button.config(text="Start")

        def update_timer():
            nonlocal timer_time, running
            if running and timer_time > 0:
                timer_time -= 1
                hour_var.set(f"{timer_time // 3600:02}")
                minute_var.set(f"{(timer_time % 3600) // 60:02}")
                second_var.set(f"{timer_time % 60:02}")
                timer_window.after(1000, update_timer)
            elif timer_time == 0 and running:
                running = False
                start_stop_button.config(text="Start")
                generate_tone()

        def generate_tone():
            # Generates a tone using sounddevice
            duration = 1.0  # seconds
            frequency = 440.0  # A4 note frequency in Hz
            sample_rate = 44100  # Sample rate in Hz

            t = np.linspace(0, duration, int(sample_rate * duration), False)  # Generate time array
            tone = 0.5 * np.sin(2 * np.pi * frequency * t)  # Generate sine wave at given frequency

            # Play tone using sounddevice
            sd.play(tone, samplerate=sample_rate)
            sd.wait()  # Wait until the tone finishes playing

        def close_timer_window(event=None):
            timer_window.destroy()

        # Bind q, Q, and Esc keys to quit the timer window
        timer_window.bind('<q>', close_timer_window)
        timer_window.bind('<Q>', close_timer_window)
        timer_window.bind('<Escape>', close_timer_window)

        start_stop_button = ttk.Button(buttons_frame, text="Start", command=start_stop_timer)
        start_stop_button.grid(row=0, column=0, padx=10, pady=10)

        cancel_button = ttk.Button(buttons_frame, text="Cancel", command=timer_window.destroy)
        cancel_button.grid(row=0, column=1, padx=10, pady=10)
    # ======================= Alarm ==========================
    def set_alarm(self):
        if not hasattr(self, 'alarm_window_open') or not self.alarm_window_open:
            # Set flag to prevent multiple alarm windows
            self.alarm_window_open = True
            display_alarm_tool(self)  # Pass 'self' to disable the button when the alarm window opens
        else:
            print("Alarm window is already open.")

    def bind_quit_keys(self):
        # Ensure the window has focus to receive key events
        self.root.focus_force()

        # Debug prints to confirm keypresses
        self.root.bind('<q>', self.quit_app)
        self.root.bind('<Q>', self.quit_app)
        self.root.bind('<Escape>', self.quit_app)

    def quit_app(self, event=None):
        print("Quitting app...")  
        self.root.quit()
        self.root.destroy()  

def display_clock_tool():
    root = tk.Tk()
    ClockApp(root)
    root.mainloop()
