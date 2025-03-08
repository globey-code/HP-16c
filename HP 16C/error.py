# error.py
#
# Provides a simple error-handling function for the HP 16C Emulator.

# Display an error message in the provided Tkinter text widget.
# Also prints a log message to the console.
def show_error(display_widget, message, log_message=""):
    display_widget.delete("1.0", "end")
    display_widget.insert("end", message)
    if log_message:
        print("Error:", log_message)
