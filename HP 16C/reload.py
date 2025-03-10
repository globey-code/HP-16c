"""
reload.py

Provides a function to relaunch the emulator (ON button).
"""

import sys
import subprocess

def reload_program():
    python = sys.executable
    subprocess.Popen([python, "main.pyw"])
    sys.exit(0)
