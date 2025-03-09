import datetime

# Dictionary of error codes and descriptions
ERROR_CODES = {
    "E101": "Stack Underflow - Operation requires more values in the stack.",
    "E102": "Invalid Operand - Operation cannot be performed on this type.",
    "E103": "Division by Zero - Cannot divide by zero.",
    "E104": "Invalid Input - Entered value is not recognized.",
    "E105": "Memory Access Error - Invalid register or memory location.",
    "E106": "Mode Error - Function not allowed in the current mode.",
}

# Log an error to error.log with timestamp
def log_error(error_code):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_message = ERROR_CODES.get(error_code, "Unknown Error")
    with open("error.log", "a") as f:
        f.write(f"[{timestamp}] {error_code}: {error_message}\n")
    print(f"Error Logged: {error_code} - {error_message}")

# Display an error message in the emulator UI
def show_error(display_widget, error_code):
    message = ERROR_CODES.get(error_code, "Unknown Error")
    
    # Use set_entry() instead of delete/insert
    display_widget.set_entry(f"ERROR {error_code}: {message}")

    log_error(error_code)
