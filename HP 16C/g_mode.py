"""
g_mode.py

Consolidated button logic for HP-16C emulator:
- g_mode_active, toggle_g_mode
"""

import sys
import os
import stack
import base_conversion
import buttons
import threading
from error import HP16CError  # For error handling

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PARENT_DIR)

# g-mode action functions
def action_lj(display_widget, controller_obj):
    try:
        controller_obj.left_justify()
        display_widget.set_entry(format_in_current_base(stack.peek(), controller_obj.display.mode))
        print("Left Justify executed")
    except HP16CError as e:
        controller_obj.handle_error(e)

def action_reciprocal(display_widget, controller_obj):
    val = stack.pop()
    if val == 0:
        controller_obj.handle_error(HP16CError("Division by zero", "E02"))
        return
    result = 1 / val if base_conversion.current_base == "DEC" else int(1 / val)
    stack.push(result)
    new_str = format_in_current_base(result, controller_obj.display.mode)
    display_widget.set_entry(new_str)
    display_widget.raw_value = new_str
    controller_obj.update_stack_display()
    print(f"Reciprocal: 1/{val} = {result}")

def action_last_x(display_widget, controller_obj):
    last_x_value = stack.last_x()
    print(f"[DEBUG] LST X pressed; last_x: {last_x_value}")
    display_widget.set_entry(last_x_value)
    # Reset to zero or previous entry after 3 seconds
    display_widget.widget.after(3000, lambda: display_widget.set_entry(0))

def action_abs(display_widget, controller_obj):
    controller_obj.absolute()
    display_widget.set_entry(format_in_current_base(stack.peek(), controller_obj.display.mode))
    print("Absolute value executed")

def action_count_bits(display_widget, controller_obj):
    controller_obj.count_bits()
    display_widget.set_entry(str(stack.peek()))
    print(f"Count bits: {stack.peek()}")

def action_set_flag(display_widget, controller_obj):
    controller_obj.set_flag("CF")
    print("Set Carry Flag")

def action_clear_flag(display_widget, controller_obj):
    controller_obj.clear_flag("CF")
    print("Clear Carry Flag")

def action_test_flag(display_widget, controller_obj):
    result = controller_obj.test_flag("CF")
    print(f"Test Carry Flag: {result}")

# g_mode_active: Global flag for g-mode
G_FUNCTIONS = {
    "LJ": lambda dw, cobj: action_lj(dw, cobj),
    "1/X": lambda dw, cobj: action_reciprocal(dw, cobj),
    "LST X": action_last_x,
    "ABS": lambda dw, cobj: action_abs(dw, cobj),
    "#B": lambda dw, cobj: action_count_bits(dw, cobj),
    "SF": lambda dw, cobj: action_set_flag(dw, cobj),
    "CF": lambda dw, cobj: action_clear_flag(dw, cobj),
    "F?": lambda dw, cobj: action_test_flag(dw, cobj),
}

# g_action: Handle g-mode button actions
def g_action(button, display_widget, controller_obj):
    sub_text = button.get("orig_sub_text", "").strip().upper()
    if sub_text in G_FUNCTIONS:
        G_FUNCTIONS[sub_text](display_widget, controller_obj)
    else:
        print(f"No g function for sub label: {sub_text}")