# src/utils/sudo_prompt.py

import tkinter as tk
from tkinter import simpledialog, messagebox, Label, ttk
import pam
import subprocess
import time

pam_auth = pam.pam()

def is_fprintd_installed():
    try:
        result = subprocess.run(['fprintd-verify', '--help'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except Exception:
        return False

def has_enrolled_fingers(username):
    try:
        result = subprocess.run(['fprintd-list', username], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return "no devices available" not in result.stdout.lower() and "Fingerprints for user" in result.stdout
    except Exception:
        return False

def prompt_fingerprint():
    prompt_window = tk.Tk()
    prompt_window.title("Fingerprint Authentication")
    prompt_label = Label(prompt_window, text="Please place your finger on the scanner.")
    prompt_label.pack(pady=20, padx=20)

    prompt_window.update()

    try:
        result = subprocess.run(['fprintd-verify'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        prompt_window.destroy()

        if result.returncode == 0:
            success_window = tk.Tk()
            success_window.title("Success")
            success_label = Label(success_window, text="Fingerprint recognized successfully!")
            success_label.pack(pady=20, padx=20)
            success_window.update()
            time.sleep(1)
            success_window.destroy()

            return True
        else:
            return False
    except Exception:
        prompt_window.destroy()
        return False

def prompt_sudo_password(action_name):
    username = subprocess.getoutput("whoami")

    if is_fprintd_installed() and has_enrolled_fingers(username):
        if prompt_fingerprint():
            return True
        else:
            print("Fingerprint authentication failed or was canceled. Falling back to password prompt.")

    max_attempts = 3
    attempts = 0

    root = tk.Tk()
    root.withdraw()

    while attempts < max_attempts:
        password = simpledialog.askstring("Sudo Password", f"Enter your sudo password to {action_name}:", show='*')

        if password is None:
            root.destroy()
            return False

        progress_window = tk.Toplevel(root)
        progress_window.title("Validating Password")
        progress_label = Label(progress_window, text="Validating password, please wait...")
        progress_label.pack(pady=10)

        progress_bar = ttk.Progressbar(progress_window, orient="horizontal", length=200, mode='determinate')
        progress_bar.pack(pady=10, padx=20)

        root.update()

        try:
            for i in range(15):
                if progress_window.winfo_exists():
                    progress_bar['value'] += 100 / 15
                    root.update()
                    time.sleep(1)
                else:
                    break

            valid = pam_auth.authenticate(username, password)

            if valid:
                progress_window.destroy()
                root.destroy()
                return True
            else:
                progress_window.destroy()
                attempts += 1
                if attempts < max_attempts:
                    messagebox.showerror("Error", "Incorrect password. Please try again.")
        except Exception:
            if progress_window.winfo_exists():
                progress_window.destroy()

    messagebox.showinfo("Canceled", "Maximum password attempts reached. Action canceled.")
    root.destroy()
    return False
