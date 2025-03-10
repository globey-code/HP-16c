"""
normal_state_function.py

Example of how the UI might call the controller. This file used to do direct
stack calls; now it calls 'controller' methods.

Reason for change:
- We push/pull from the stack via the controller layer, so we can catch errors in one place.
"""

import controller
import stack
from normal_state_function import display  # If you keep a global display reference
# (Alternatively, pass 'display' around as needed.)

def normal_action_digit(digit):
    """User pressed a digit in normal mode."""
    if display:
        # Append the digit to the display's raw_value
        display.append_entry(digit)

def normal_action_operator(operator):
    """User pressed +, -, *, or / in normal mode."""
    if display:
        controller.perform_operator(operator, display)

def normal_action_special(label, buttons, disp):
    """Handle special keys like ENTER, CHS, BIN/OCT/DEC/HEX, etc."""
    if label.upper() == "ENTER":
        # Push the current display value to stack
        val_str = disp.raw_value
        try:
            val = float(val_str) if "." in val_str else int(val_str)
        except ValueError:
            val = 0
        controller.push_value(val, disp)
        disp.clear_entry()
    elif label.upper() in {"BIN", "OCT", "DEC", "HEX"}:
        # Example: set base, or do something else
        pass
    # etc...
