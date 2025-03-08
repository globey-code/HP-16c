# reload.py
import sys
import os
import subprocess

def reload_program():
    python = sys.executable
    # Launch a new instance of main.pyw
    subprocess.Popen([python, "main.pyw"])
    # Exit the current process so that only the new instance remains
    sys.exit(0)
