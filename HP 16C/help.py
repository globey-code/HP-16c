import tkinter as tk
from logging_config import logger

# Global variable to track the help window
help_window = None

def show_user_guide():
    """Open the user guide in a single help window with a scrollbar."""
    global help_window
    if help_window is None or not help_window.winfo_exists():
        logger.info("Opening user guide")
        help_window = tk.Toplevel()
        help_window.title("User Guide")
        help_window.geometry("400x300")
        help_window.resizable(False, False)
        
        label = tk.Label(help_window, text="User Guide", font=("Helvetica", 16))
        label.pack(pady=10)
        
        # Frame for text and scrollbar
        text_frame = tk.Frame(help_window)
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Text widget with scrollbar
        text = tk.Text(text_frame, wrap="word", height=15, width=50)
        scrollbar = tk.Scrollbar(text_frame, command=text.yview)
        text.config(yscrollcommand=scrollbar.set)
        text.insert("1.0", "Welcome to the HP-16C Emulator User Guide!\n\n"
                          "Features:\n"
                          "- Switch between DEC and FLOAT modes\n"
                          "- Perform arithmetic operations\n"
                          "- Use the stack display (F2 to toggle)\n"
                          "Press F1 to reopen this guide.")
        text.config(state="disabled")
        text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
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