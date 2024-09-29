import tkinter as tk
from tkinter import messagebox
import subprocess
import re 

# Global variables to track the initial and current states
initial_orientation = None
initial_resolution = None
initial_position = None
connected_displays = []  # To track currently connected displays
main_display = None

# Global variables to manage the countdown timer window
current_timer_window = None
current_countdown_label = None
timer_canceled = False

def run_xrandr_command(commands):
    try:
        result = subprocess.run(['xrandr'] + commands, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode().strip()
        print(f"Executed: {' '.join(commands)}")
        return output
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute {' '.join(commands)}: {e}")
        return None

def get_main_display():
    try:
        result = subprocess.run(['xrandr'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode().strip()
        lines = output.splitlines()
        for line in lines:
            if " connected primary" in line:
                return line.split()[0]
            elif " connected" in line and "primary" not in line:
                return line.split()[0]  # Fallback if primary not found
        return None
    except subprocess.CalledProcessError as e:
        print(f"Failed to get main display: {e}")
        return None

def get_external_displays(main_display):
    try:
        result = subprocess.run(['xrandr'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode().strip()
        lines = output.splitlines()
        displays = []
        for line in lines:
            if " connected" in line:
                display_name = line.split()[0]
                if display_name != main_display:
                    displays.append(display_name)
        return displays
    except subprocess.CalledProcessError as e:
        print(f"Failed to get external displays: {e}")
        return []

def determine_display_positions():
    def run_xrandr():
        result = subprocess.run(['xrandr'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode().strip()

    def parse_xrandr_output(xrandr_output):
        displays = {}
        lines = xrandr_output.splitlines()
        for line in lines:
            if " connected" in line:
                parts = line.split()
                display_name = parts[0]
                resolution_part = None
                position_part = None
                for part in parts:
                    if "+" in part and "x" in part:
                        resolution_part = part.split("+")[0]
                        position_part = part.split("+")[1:]
                        break
                if resolution_part and position_part:
                    resolution = tuple(map(int, resolution_part.split("x")))
                    position = tuple(map(int, position_part))
                    displays[display_name] = {"resolution": resolution, "position": position}
        return displays

    def determine_relative_position(primary_info, secondary_info):
        primary_x, primary_y = primary_info["position"]
        primary_width, primary_height = primary_info["resolution"]
        secondary_x, secondary_y = secondary_info["position"]
        secondary_width, secondary_height = secondary_info["resolution"]

        if secondary_x >= primary_x + primary_width:
            return "right-of"
        elif secondary_x + secondary_width <= primary_x:
            return "left-of"
        elif secondary_y + secondary_height <= primary_y:
            return "above"
        elif secondary_y >= primary_y + primary_height:
            return "below"
        elif secondary_x == primary_x and secondary_y == primary_y:
            return "same-as"
        else:
            return "unknown"

    # Use existing functions to get main and external displays
    main_display = get_main_display()
    external_displays = get_external_displays(main_display)
    
    if main_display:
        xrandr_output = run_xrandr()
        displays = parse_xrandr_output(xrandr_output)
        positions = {}

        main_info = displays.get(main_display)
        if main_info:
            for display in external_displays:
                info = displays.get(display)
                if info:
                    position = determine_relative_position(main_info, info)
                    positions[display] = position
        return main_display, positions
    else:
        print("Main display not found")
        return None, None

def get_display_resolution(display):
    try:
        result = subprocess.run(['xrandr'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode().strip()
        lines = output.splitlines()
        found_display = False
        
        for line in lines:
            if display in line and "connected" in line:
                found_display = True  # Start capturing after the display is found
                continue
            
            if found_display:
                if "*" in line:
                    resolution = line.split()[0]
                    return resolution
                elif "connected" in line:
                    break  # Stop if the next display is found

        return "Resolution not found."
    except subprocess.CalledProcessError as e:
        print(f"Failed to get display resolution: {e}")
        return None

def get_available_resolutions(display):
    try:
        result = subprocess.run(['xrandr'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode().strip()
        lines = output.splitlines()
        resolutions = []
        capture = False
        for line in lines:
            if line.startswith(display):
                capture = True
                continue
            if capture:
                if "connected" in line:
                    break  # Stop capturing when the next display is found
                res_parts = line.split()
                if res_parts and res_parts[0].replace('x', '').isdigit():  # Ensure it's a valid resolution
                    resolutions.append(res_parts[0])
        return resolutions
    except subprocess.CalledProcessError as e:
        print(f"Failed to get available resolutions for {display}: {e}")
        return []

def store_initial_values(orientation_var, position_var, resolution_var):
    global initial_orientation, initial_position, initial_resolution
    
    # Get the main display
    main_display = get_main_display()
    
    # Capture the initial orientation using the main display
    initial_orientation = capture_current_orientation(main_display)
    
    # Capture the initial resolution using the main display
    initial_resolution = get_display_resolution(main_display)
    
    # Determine the position of the connected display relative to the main display
    _, positions = determine_display_positions()
    
    # Set the initial position using the determined position, assuming the first connected display
    if positions:
        initial_position = list(positions.values())[0]
    else:
        initial_position = "same-as"  # Default if no positions are found
    
    print(f"Debug: Initial Orientation: {initial_orientation}, Initial Position: {initial_position}, Initial Resolution: {initial_resolution}")

def has_changed(orientation_var, position_var, resolution_var):
    return (orientation_var.get() != initial_orientation or
            position_var.get() != initial_position or
            resolution_var.get() != initial_resolution)

def apply_settings(main_display, display_var, position_var, resolution_var, root, orientation_var=None):
    global initial_position, initial_resolution

    # Automatically detect which display is being interacted with
    target_display = display_var.get() if display_var.get() else main_display

    if has_changed(orientation_var, position_var, resolution_var):
        # Run the --auto command first
        run_xrandr_command(['--output', target_display, '--auto'])

        if position_var.get() == "same-as":
            run_xrandr_command(['--output', target_display, '--same-as', main_display])
        elif target_display != main_display:
            # Ensure the scaling is correct regardless of position
            run_xrandr_command(['--output', target_display, '--auto', f'--{position_var.get()}', main_display])

        if resolution_var.get() != initial_resolution:
            run_xrandr_command(['--output', target_display, '--mode', resolution_var.get()])

        new_orientation = orientation_var.get()

        # Apply orientation change directly to the main display only
        change_orientation(main_display, new_orientation, root, orientation_var)

        # Update the stored initial values for position and resolution, but not for orientation
        initial_position = position_var.get()
        initial_resolution = resolution_var.get()

def change_orientation(display, new_orientation, root, orientation_var, prompt_window=None):
    global initial_orientation
    try:
        if initial_orientation is None:
            initial_orientation = capture_current_orientation(display)
            print(f"Stored initial orientation as: {initial_orientation}")
        
        command = ['--output', display, '--rotate', new_orientation]
        result = run_xrandr_command(command)
        if result is not None:
            if new_orientation != "normal" and new_orientation != initial_orientation:
                start_revert_timer(display, root, new_orientation, orientation_var)  # Corrected to pass orientation_var
            else:
                initial_orientation = new_orientation  # Update the initial orientation
                print(f"Orientation saved as: {initial_orientation}")
            if prompt_window:
                prompt_window.destroy()  # Close prompt window if orientation is "normal"
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while changing orientation: {str(e)}")

def capture_current_orientation(display):
    try:
        result = subprocess.run(['xrandr', '--verbose'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode().strip()
        lines = output.splitlines()

        for line in lines:
            if line.startswith(display) and "connected" in line:
                # Remove everything in parentheses
                line_without_parentheses = re.sub(r'\(.*?\)', '', line)

                # Check for specific orientation keywords
                if "right" in line_without_parentheses:
                    return "right"
                elif "left" in line_without_parentheses:
                    return "left"
                elif "inverted" in line_without_parentheses:
                    return "inverted"
                else:
                    return "normal"  # Default to normal if none of the keywords are found

        return "normal"  # Default to normal if no valid line is found
    except subprocess.CalledProcessError as e:
        print(f"Failed to capture current orientation for {display}: {e}")
        return "normal"

def start_revert_timer(display, root, new_orientation, orientation_var):
    global current_timer_window, current_countdown_label, timer_canceled

    # If there is an existing timer window, close it and stop the previous timer
    if current_timer_window is not None:
        current_timer_window.destroy()
        timer_canceled = True  # Cancel the previous timer

    countdown = 10
    timer_canceled = False

    def revert_orientation():
        if not timer_canceled:
            print(f"Reverting orientation to {initial_orientation}")
            run_xrandr_command(['--output', display, '--rotate', initial_orientation])
            notify_user(f"Orientation reverted to {initial_orientation}.")
            orientation_var.set(initial_orientation)  # Reset the dropdown to the initial display

    def update_timer():
        nonlocal countdown
        if countdown > 0:
            try:
                current_countdown_label.config(text=f"Orientation changed to {new_orientation}... Reverting in {countdown} seconds.")
            except tk.TclError:
                # If the window is destroyed, just continue the countdown in the background
                pass
            countdown -= 1
            root.after(1000, update_timer)
        else:
            revert_orientation()
            if current_timer_window.winfo_exists():
                current_timer_window.destroy()

    def confirm_change():
        nonlocal countdown
        countdown = 0  # Stop the countdown
        global initial_orientation, timer_canceled
        timer_canceled = True
        initial_orientation = new_orientation  # Update the original orientation to the new one only after confirmation
        if current_timer_window.winfo_exists():
            current_timer_window.destroy()  # Close the confirmation window
        print(f"Orientation saved as: {initial_orientation}")
        notify_user(f"Orientation set to {new_orientation} permanently.")

    # Create the new timer window
    current_timer_window = tk.Toplevel(root)
    current_timer_window.title("Confirm Orientation Change")
    current_timer_window.geometry("300x100")

    current_countdown_label = tk.Label(current_timer_window, text=f"Orientation changed to {new_orientation}... Reverting in {countdown} seconds.")
    current_countdown_label.pack(pady=10)

    confirm_button = tk.Button(current_timer_window, text="Confirm", command=confirm_change)
    confirm_button.pack(pady=10)

    # Start the countdown timer
    update_timer()

def notify_user(message):
    print(message)

def reset_to_main_display_layout(root, display_var, position_var, resolution_var, resolution_menu, position_menu, resolution_label, external_resolution_label):
    # Reset the layout to the main display configuration
    display_var.set("")
    position_var.set("")
    resolution_var.set("")
    resolution_menu.pack_forget()
    position_menu.pack_forget()
    external_resolution_label.config(text="")
    resolution_label.config(text=f"Main Display Resolution: {get_display_resolution(get_main_display())}")
    orientation_menu.pack(pady=10)

def update_displays(main_display, display_var, resolution_var, resolution_label, external_resolution_label, position_menu, position_var, resolution_menu, root):
    global connected_displays
    new_displays = get_external_displays(main_display)

    # Detect disconnected displays and run xrandr --output {device} --off
    for old_display in connected_displays:
        if old_display not in new_displays:
            run_xrandr_command(['--output', old_display, '--off'])
            print(f"Display {old_display} disconnected and turned off.")
            # Revert to default layout if HDMI disconnected
            reset_to_main_display_layout(root, display_var, position_var, resolution_var, resolution_menu, position_menu, resolution_label, external_resolution_label)

    if new_displays != connected_displays:
        connected_displays = new_displays
        if connected_displays:
            display_var.set(connected_displays[0])
            external_resolution_label.config(text=f"External Display Resolution: {get_display_resolution(display_var.get())}")
            run_xrandr_command(['--output', connected_displays[0], '--auto'])
            available_resolutions = get_available_resolutions(display_var.get())
            if available_resolutions:
                resolution_var.set(available_resolutions[0])
                resolution_menu['menu'].delete(0, 'end')
                for resolution in available_resolutions:
                    resolution_menu['menu'].add_command(label=resolution, command=tk._setit(resolution_var, resolution))
            position_menu.pack(pady=10)
            resolution_menu.pack(pady=10)
            if len(connected_displays) == 1:
                display_info_label = tk.Label(root, text=f"Display: {connected_displays[0]}")
                display_info_label.pack(pady=10)
            else:
                display_menu = tk.OptionMenu(root, display_var, *connected_displays)
                display_menu.pack(pady=10)
                display_var.trace("w", lambda *args: external_resolution_label.config(text=f"External Display Resolution: {get_display_resolution(display_var.get())}"))
        else:
            reset_to_main_display_layout(root, display_var, position_var, resolution_var, resolution_menu, position_menu, resolution_label, external_resolution_label)

    root.after(2000, update_displays, main_display, display_var, resolution_var, resolution_label, external_resolution_label, position_menu, position_var, resolution_menu, root)

def show_xrandr_control():
    global initial_orientation, connected_displays
    root = tk.Tk()
    root.title("xrandr Control")
    root.geometry("450x400")  # Increased window size

    main_display = get_main_display()
    if not main_display:
        messagebox.showerror("Error", "Could not detect the main display.")
        root.destroy()
        return
    
    initial_orientation = capture_current_orientation(main_display)

    connected_displays = get_external_displays(main_display)

    display_label = tk.Label(root, text=f"Main Display: {main_display}")
    display_label.pack(pady=10)

    resolution_label = tk.Label(root, text=f"Main Display Resolution: {get_display_resolution(main_display)}")
    resolution_label.pack(pady=10)

    display_var = tk.StringVar(root)
    
    external_resolution_label = tk.Label(root, text="")
    external_resolution_label.pack(pady=10)

    resolution_var = tk.StringVar(root)

    position_var = tk.StringVar(root)
    position_var.set("right-of")
    position_menu = tk.OptionMenu(root, position_var, "right-of", "left-of", "above", "below", "same-as")

    resolution_menu = tk.OptionMenu(root, resolution_var, "")  # Initialize empty resolution menu

    if connected_displays:
        display_var.set(connected_displays[0])
        external_resolution_label.config(text=f"External Display Resolution: {get_display_resolution(display_var.get())}")
        run_xrandr_command(['--output', connected_displays[0], '--auto'])
        available_resolutions = get_available_resolutions(display_var.get())
        if available_resolutions:
            resolution_var.set(available_resolutions[0])
            resolution_menu = tk.OptionMenu(root, resolution_var, *available_resolutions)
            resolution_menu.pack(pady=10)
        if len(connected_displays) == 1:
            display_info_label = tk.Label(root, text=f"Display: {connected_displays[0]}")
            display_info_label.pack(pady=10)
        else:
            display_menu = tk.OptionMenu(root, display_var, *connected_displays)
            display_menu.pack(pady=10)
            display_var.trace("w", lambda *args: external_resolution_label.config(text=f"External Display Resolution: {get_display_resolution(display_var.get())}"))
        position_menu.pack(pady=10)
        resolution_menu.pack(pady=10)
    else:
        external_resolution_label.config(text="No external displays found.")

    orientation_var = tk.StringVar(root)
    orientation_var.set(initial_orientation)
    orientation_menu = tk.OptionMenu(root, orientation_var, "normal", "left", "right", "inverted")
    orientation_menu.pack(pady=10)

    # Store initial dropdown values
    store_initial_values(orientation_var, position_var, resolution_var)

    apply_button = tk.Button(root, text="Apply Settings", command=lambda: apply_settings(main_display=get_main_display(), display_var=display_var, position_var=position_var, resolution_var=resolution_var, root=root, orientation_var=orientation_var))
    apply_button.pack(side=tk.BOTTOM, pady=20)

    root.after(2000, update_displays, main_display, display_var, resolution_var, resolution_label, external_resolution_label, position_menu, position_var, resolution_menu, root)

    root.bind('<Escape>', lambda event: root.destroy())
    root.bind('<q>', lambda event: root.destroy())

    root.mainloop()
