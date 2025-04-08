"""
user_guide.py
Provides a comprehensive user guide interface for the HP-16C emulator, displaying instructions in a scrollable window.
Author: GlobeyCode
License: MIT
Created: 3/23/2025
Last Modified: 4/06/2025
Dependencies: Python 3.6+, tkinter, logging_config
"""

import tkinter as tk
from logging_config import logger

# Global variable to track the help window
help_window = None

def show_user_guide():
    """Display a comprehensive user guide for the HP-16C emulator in a scrollable window."""
    global help_window
    if help_window is None or not help_window.winfo_exists():
        logger.info("Opening user guide")
        help_window = tk.Toplevel()
        help_window.title("HP-16C Emulator User Guide")
        help_window.geometry("600x400")
        help_window.resizable(True, True)

        # Title
        title_label = tk.Label(help_window, text="HP-16C Emulator User Guide", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)

        # Frame for text and scrollbar
        text_frame = tk.Frame(help_window)
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Text widget with scrollbar
        text = tk.Text(text_frame, wrap="word", height=20, width=70, font=("Courier", 10))
        scrollbar = tk.Scrollbar(text_frame, command=text.yview)
        text.config(yscrollcommand=scrollbar.set)

        # Comprehensive guide content
        guide_content = (
            "Welcome to the HP-16C Emulator!\n\n"
            "This emulator replicates the Hewlett-Packard 16C calculator, a tool for programmers with RPN (Reverse Polish Notation), "
            "multiple number bases, and bit manipulation features.\n\n"
            
            "1. Getting Started\n"
            "   - Press digits (0-9, A-F) to enter numbers.\n"
            "   - Use ENTER to push a value onto the stack.\n"
            "   - Press F1 to reopen this guide, F2 to toggle stack display.\n\n"
            
            "2. Number Bases\n"
            "   - Switch modes: HEX, DEC, OCT, BIN, FLOAT (buttons in row 2).\n"
            "   - Example: In DEC, press 5 ENTER 3 + to get 8.\n"
            "   - In HEX, press A ENTER 5 + to get F.\n\n"
            
            "3. Arithmetic Operations\n"
            "   - +, -, *, /: Perform operations on X and Y registers.\n"
            "   - Example: 10 ENTER 3 / displays 3 (remainder in LAST X).\n\n"
            
            "4. Stack Operations\n"
            "   - R↓ (roll down), X<>Y (swap X and Y), CLX (clear X).\n"
            "   - Stack display (F2) shows X, Y, Z, T registers.\n\n"
            
            "5. f-Mode (Yellow Key)\n"
            "   - Press 'f' then a key for operations like:\n"
            "     - SL/SR: Shift left/right.\n"
            "     - RL/RR: Rotate left/right.\n"
            "     - MASKL/MASKR: Mask bits from Y.\n"
            "     - WSIZE: Set word size (1-64 bits).\n\n"
            
            "6. g-Mode (Blue Key)\n"
            "   - Press 'g' then a key for operations like:\n"
            "     - LJ: Left justify X.\n"
            "     - 1/X: Reciprocal of X.\n"
            "     - P/R: Toggle program/run mode.\n"
            "     - LST X: Recall last X value.\n\n"
            
            "7. Programming\n"
            "   - Enter program mode (g P/R), input instructions, exit with g P/R.\n"
            "   - Use LBL (label), GSB (go subroutine), RTN (return).\n"
            "   - Example: 'LBL A 5 ENTER 3 + RTN' adds 5 and 3 when GSB A is run.\n\n"
            
            "8. Tips\n"
            "   - CHS: Change sign of X.\n"
            "   - BSP: Backspace during entry or clear X.\n"
            "   - Logs are saved in the 'logs' directory for debugging.\n"
        )
        text.insert("1.0", guide_content)
        text.config(state="disabled")
        text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Close button
        close_button = tk.Button(help_window, text="Close", command=lambda: close_help_window(help_window))
        close_button.pack(pady=5)

        help_window.protocol("WM_DELETE_WINDOW", lambda: close_help_window(help_window))
    else:
        logger.info("User guide already open")
        help_window.deiconify()
        help_window.lift()

def close_help_window(window):
    """Handle the closure of the help window."""
    global help_window
    window.destroy()
    help_window = None
    logger.info("User guide closed")