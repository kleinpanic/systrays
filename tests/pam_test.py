# test_pam_auth.py

import pam
import subprocess

pam_auth = pam.pam()

username = subprocess.getoutput("whoami")

password = input("Enter your sudo password: ")

if pam_auth.authenticate(username, password):
    print("Password validated successfully.")
else:
    print("Password validation failed.")
