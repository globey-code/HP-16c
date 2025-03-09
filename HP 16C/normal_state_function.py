# normal_state_function.py

# Global variable for the display.
display = None

import sys
import os
import subprocess
import stack
from mode_manager import set_mode

def set_display(d):
    """Set the global display reference."""
    global display
    display = d

def get_display():
    """Return the current display instance."""
    global display
    return display
    return display_widget

def convert_entry(raw_value, mode):
    """
    Convert the raw_value (assumed to be a decimal number in string form)
    into the specified mode: HEX, OCT, BIN, or DEC.
    For non-integer values, only the integer part is converted.
    """
    try:
        # If raw_value contains a decimal point, convert only its integer part.
        if "." in raw_value:
            num = int(float(raw_value))  # Truncate fractional part.
        else:
            num = int(raw_value)
    except ValueError:
        return raw_value  # If conversion fails, return raw_value unchanged.
    
    if mode.upper() == "HEX":
        return hex(num)[2:].upper()  # e.g., 740 -> "2E4"
    elif mode.upper() == "OCT":
        return oct(num)[2:]           # e.g., 740 -> "1334"
    elif mode.upper() == "BIN":
        return bin(num)[2:]           # e.g., 740 -> "1011100100"
    elif mode.upper() == "DEC":
        return str(num)
    else:
        return raw_value

def normal_action_digit(digit):
    print(f"Normal digit action: {digit}")
    if display:
        display.append_entry(digit)

def normal_action_operator(operator):
    print(f"Normal operator action: {operator}")
    if display:
        try:
            # For an RPN calculator, use the top two values on the stack.
            operand2 = stack.pop()  # Divisor (last entered)
            operand1 = stack.pop()  # Dividend (one below)
            
            if operator == "/":
                result = operand1 / operand2
            elif operator == "*":
                result = operand1 * operand2
            elif operator == "+":
                result = operand1 + operand2
            elif operator == "-":
                result = operand1 - operand2
            else:
                raise ValueError("Unsupported operator")
            
            stack.push(result)
            print(f"Pushed value: {result}. New stack state: {stack.get_state()}")
            # Update both the visible entry and the raw_value.
            display.set_entry(str(result))
            display.raw_value = str(result)
        except Exception as e:
            display.show_error("Error", str(e))

def normal_action_special(label, buttons, display):
    # Handle mode buttons: BIN, OCT, DEC, HEX.
    if label.upper() in {"BIN", "OCT", "DEC", "HEX"}:
        set_mode(label, display)  # Updates the mode label and display.mode.
        if display:
            # Always convert from the raw_value (which is in decimal).
            new_entry = convert_entry(display.raw_value, label)
            display.set_entry(new_entry)
    # Handle the ENTER key: push the current (raw) value onto the stack.
    elif label.upper() == "ENTER":
        if display:
            current = display.raw_value
            try:
                if "." in current:
                    num = float(current)
                else:
                    num = int(current)
            except ValueError:
                num = 0  # Or handle the error as appropriate.
            stack.push(num)
            print(f"Pushed value: {num}. New stack state: {stack.get_state()}")
            display.clear_entry()
    else:
        print(f"Normal action for: {label}")
    
    if display:
        if label == "BSP":
            # Backspace: remove the last character.
            if display.current_entry:
                new_entry = display.current_entry[:-1]
                display.set_entry(new_entry)
                display.raw_value = display.raw_value[:-1]
        elif label == "CHS":
            # Change sign: toggle the sign.
            if display.current_entry:
                if display.current_entry.startswith("-"):
                    new_entry = display.current_entry[1:]
                    if display.raw_value.startswith("-"):
                        display.raw_value = display.raw_value[1:]
                else:
                    new_entry = "-" + display.current_entry
                    display.raw_value = "-" + display.raw_value
                display.set_entry(new_entry)
        elif label.upper() == "ON":
            print("HP 16c Restart...")
            python = sys.executable
            subprocess.Popen([python, "main.pyw"])
            sys.exit(0)
