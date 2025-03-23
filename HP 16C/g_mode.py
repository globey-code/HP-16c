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
from error import HP16CError
from logging_config import logger

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PARENT_DIR)

def action_lj(display_widget, controller_obj):
    """Left Justify (LJ)."""
    controller_obj.left_justify()

def action_reciprocal(display_widget, controller_obj):
    """Reciprocal (1/X)."""
    try:
        val = stack.pop()
        if val == 0:
            controller_obj.handle_error(HP16CError("Division by zero", "E02"))
            return
        result = 1 / val if base_conversion.current_base == "DEC" else int(1 / val)
        stack.push(result)
        new_str = base_conversion.format_in_current_base(result, controller_obj.display.mode)
        display_widget.set_entry(new_str)
        display_widget.raw_value = new_str
        controller_obj.update_stack_display()
    except HP16CError as e:
        controller_obj.handle_error(e)

def action_last_x(display_widget, controller_obj):
    """Last X (LST X)."""
    last_x_value = stack.last_x()
    display_widget.set_entry(last_x_value)
    display_widget.widget.after(3000, lambda: display_widget.set_entry(0))

def action_abs(display_widget, controller_obj):
    """Absolute Value (ABS)."""
    controller_obj.absolute()

def action_count_bits(display_widget, controller_obj):
    """Count Bits (#B)."""
    controller_obj.count_bits()

def action_set_flag(display_widget, controller_obj):
    """Set Carry Flag (SF)."""
    controller_obj.set_flag("CF")

def action_clear_flag(display_widget, controller_obj):
    """Clear Carry Flag (CF)."""
    controller_obj.clear_flag("CF")

def action_test_flag(display_widget, controller_obj):
    """Test Carry Flag (F?)."""
    result = controller_obj.test_flag("CF")
    display_widget.set_entry(str(result))

def action_r_up(display_widget, controller_obj):
    """Rotate stack upward (R↑) to match real HP-16C behavior."""
    if controller_obj.is_user_entry:
        # Commit the pending entry to X without lifting the stack
        entry = controller_obj.display.raw_value
        val = base_conversion.interpret_in_base(entry, controller_obj.display.mode)
        stack._x_register = val  # Set X to the entered value
        controller_obj.is_user_entry = False
    
    # Perform the roll-up operation
    stack.roll_up()
    
    # Update the display with the new X value
    top_val = stack.peek()
    display_widget.set_entry(base_conversion.format_in_current_base(top_val, display_widget.mode))
    controller_obj.update_stack_display()
    
    # Enable stack lift after R↑
    controller_obj.stack_lift_enabled = True  # R↑ enables stack lift
    controller_obj.result_displayed = True
    logger.info("Performed R↑: stack rotated up")

G_FUNCTIONS = {
    "LJ": action_lj,
    "1/X": action_reciprocal,
    "LST X": action_last_x,
    "ABS": action_abs,
    "#B": action_count_bits,
    "SF": action_set_flag,
    "CF": action_clear_flag,
    "F?": action_test_flag,
    "R↑": action_r_up,
}

def g_action(button, display_widget, controller_obj):
    """Execute the g-mode function for a given button."""
    sub_text = button.get("orig_sub_text", "").strip().upper()
    logger.info(f"g-mode action: {sub_text}")
    if sub_text in G_FUNCTIONS:
        G_FUNCTIONS[sub_text](display_widget, controller_obj)