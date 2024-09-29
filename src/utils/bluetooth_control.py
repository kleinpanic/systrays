import tkinter as tk
from tkinter import messagebox, simpledialog
import subprocess
import os
import signal

terminal_pid = None  # Global variable to track the terminal session PID
is_window_open = True  # Flag to indicate if the window is open

def run_bluetoothctl_command(commands):
    try:
        result = subprocess.run(['bluetoothctl'] + commands, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode().strip()
        print(f"Executed: {' '.join(commands)}")
        return output
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute {' '.join(commands)}: {e}")
        return None

def update_device_list(device_listbox):
    device_listbox.delete(0, tk.END)
    try:
        result = subprocess.run(['bluetoothctl', 'devices'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode().strip()
        devices = output.splitlines()
        for device in devices:
            device_serial = device.split()[1]
            trust_status = run_bluetoothctl_command(['info', device_serial])
            is_trusted = "Trusted: yes" in trust_status if trust_status else False

            device_text = f"{device.strip()} {'[Trusted]' if is_trusted else ''}"
            device_listbox.insert(tk.END, device_text)

    except subprocess.CalledProcessError as e:
        print(f"Failed to update device list: {e}")

def update_connected_device_label(connected_device_label):
    connected_device = get_connected_device()
    if connected_device:
        connected_device_label.config(text=f"Currently Connected Device: {connected_device}")
    else:
        connected_device_label.config(text="Currently Connected Device: None")

def get_connected_device():
    try:
        result = subprocess.run(['bluetoothctl', 'info'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode().strip()
        if "Connected: yes" in output:
            for line in output.splitlines():
                if line.startswith("Device"):
                    return line.split()[1]  # Return the device serial number
        return None
    except subprocess.CalledProcessError as e:
        print(f"Failed to get connected device: {e}")
        return None

def connect_device(device_serial, connected_device_label, device_listbox):
    if device_serial:
        try:
            # Attempt to pair the device
            pair_output = run_bluetoothctl_command(['pair', device_serial])
            if not pair_output or "Failed" in pair_output:
                print(f"Pairing failed for device {device_serial}. Proceeding to connect...")

            # Attempt to connect the device regardless of pairing success
            connect_output = run_bluetoothctl_command(['connect', device_serial])
            if not connect_output or "Failed" in connect_output:
                raise Exception(f"Connection failed for device {device_serial}")

            # Update the connected device label if successful
            update_connected_device_label(connected_device_label)

            # Check if the device is already trusted
            trust_status = run_bluetoothctl_command(['info', device_serial])
            is_trusted = "Trusted: yes" in trust_status if trust_status else False

            if not is_trusted:
                should_trust = messagebox.askyesno("Trust Device", "Do you want to trust this device?")
                if should_trust:
                    run_bluetoothctl_command(['trust', device_serial])
                    update_device_list(device_listbox)  # Update the list to reflect the new trust status
            
            messagebox.showinfo("Connection", f"Successfully connected to device {device_serial}.")
        except Exception as e:
            messagebox.showerror("Connection Failed", f"Could not connect to device {device_serial}. Error: {str(e)}")

def disconnect_device(device_serial, connected_device_label):
    if device_serial:
        try:
            if get_connected_device() != device_serial:
                messagebox.showinfo("Not Connected", "This device is not currently connected.")
                return
            
            disconnect_output = run_bluetoothctl_command(['disconnect', device_serial])
            if "Failed" in disconnect_output or disconnect_output is None:
                raise Exception(f"Disconnection failed for device {device_serial}")
            
            update_connected_device_label(connected_device_label)
            messagebox.showinfo("Disconnection", f"Successfully disconnected from device {device_serial}.")
        except Exception as e:
            messagebox.showerror("Disconnection Failed", f"Could not disconnect from device {device_serial}. Error: {str(e)}")

def toggle_trust_device(device_serial, device_listbox):
    if device_serial:
        try:
            trust_status = run_bluetoothctl_command(['info', device_serial])
            is_trusted = "Trusted: yes" in trust_status if trust_status else False

            if is_trusted:
                run_bluetoothctl_command(['untrust', device_serial])
                messagebox.showinfo("Trust Status", f"Device {device_serial} is now untrusted.")
            else:
                run_bluetoothctl_command(['trust', device_serial])
                messagebox.showinfo("Trust Status", f"Device {device_serial} is now trusted.")

            update_device_list(device_listbox)
        except Exception as e:
            messagebox.showerror("Trust Toggle Failed", f"Could not toggle trust status for device {device_serial}. Error: {str(e)}")

def on_connect_button_click(device_listbox, connected_device_label):
    selected_device = device_listbox.get(tk.ACTIVE)
    if selected_device:
        device_serial = selected_device.split()[1]
        if get_connected_device() and device_serial in get_connected_device():
            messagebox.showinfo("Already Connected", "This device is already connected.")
        else:
            connect_device(device_serial, connected_device_label, device_listbox)
    else:
        device_serial = simpledialog.askstring("Connect Device", "Enter the device serial number:")
        connect_device(device_serial, connected_device_label, device_listbox)

def on_disconnect_button_click(device_listbox, connected_device_label):
    selected_device = device_listbox.get(tk.ACTIVE)
    if selected_device:
        device_serial = selected_device.split()[1]
        disconnect_device(device_serial, connected_device_label)
    else:
        device_serial = simpledialog.askstring("Disconnect Device", "Enter the device serial number:")
        disconnect_device(device_serial, connected_device_label)

def open_bluetooth_terminal():
    global terminal_pid

    if terminal_pid is None:
        try:
            terminal_emulator = subprocess.getoutput('echo $TERM')
            if terminal_emulator:
                proc = subprocess.Popen([terminal_emulator, '-e', 'bluetoothctl'])
            else:
                proc = subprocess.Popen(['xterm', '-e', 'bluetoothctl'])

            terminal_pid = proc.pid  # Store the PID of the terminal session
            print(f"Terminal opened with PID: {terminal_pid}")
        except Exception as e:
            print(f"Failed to open terminal: {e}")
            messagebox.showerror("Terminal Error", "Failed to open Bluetooth terminal.")
    else:
        try:
            os.kill(terminal_pid, signal.SIGTERM)  # Terminate the terminal session
            print(f"Terminal with PID {terminal_pid} terminated.")
            terminal_pid = None  # Reset the PID tracking variable
        except Exception as e:
            print(f"Failed to terminate terminal: {e}")
            messagebox.showerror("Terminal Error", "Failed to terminate Bluetooth terminal.")
            terminal_pid = None  # Reset the PID tracking variable just in case

def periodic_update_connected_device_label(connected_device_label):
    global is_window_open
    if is_window_open:
        update_connected_device_label(connected_device_label)
        connected_device_label.after(5000, periodic_update_connected_device_label, connected_device_label)

def show_bluetooth_control():
    global terminal_pid, is_window_open
    root = tk.Tk()
    root.title("Bluetooth Control")
    
    # Increase the window size to ensure everything fits
    root.geometry("400x400")

    # Connected device label
    connected_device_label = tk.Label(root, text="Currently Connected Device: None")
    connected_device_label.pack(pady=10)

    # Start periodic updates to check connection status
    periodic_update_connected_device_label(connected_device_label)

    # Device listbox
    device_listbox = tk.Listbox(root, selectmode=tk.SINGLE)
    device_listbox.pack(pady=10, fill=tk.BOTH, expand=True)

    update_device_list(device_listbox)

    # Connect button
    connect_button = tk.Button(root, text="Connect to Selected Device", command=lambda: on_connect_button_click(device_listbox, connected_device_label))
    connect_button.pack(pady=5)

    # Disconnect button
    disconnect_button = tk.Button(root, text="Disconnect from Selected Device", command=lambda: on_disconnect_button_click(device_listbox, connected_device_label))
    disconnect_button.pack(pady=5)

    # Toggle terminal button
    open_terminal_button = tk.Button(root, text="Toggle Bluetooth Terminal", command=open_bluetooth_terminal)
    open_terminal_button.pack(pady=5)

    # Adding Q and ESC keybindings to close the window
    def close_window():
        global is_window_open
        is_window_open = False
        if terminal_pid is not None:
            try:
                os.kill(terminal_pid, signal.SIGTERM)
                print(f"Terminal with PID {terminal_pid} terminated.")
            except Exception as e:
                print(f"Failed to terminate terminal: {e}")
        root.destroy()

    root.bind('<Escape>', lambda event: close_window())
    root.bind('<q>', lambda event: close_window())
    root.bind('<Control-t>', lambda event: toggle_trust_device(device_listbox.get(tk.ACTIVE).split()[1], device_listbox))

    root.mainloop()
