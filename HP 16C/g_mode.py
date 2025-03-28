# g_mode.py
# Consolidates button logic for the g-mode in the HP-16C emulator, handling operations like left justification, reciprocal, and flag management.
# Author: GlobeyCode
# License: MIT
# Date: 3/23/2025
# Dependencies: Python 3.6+, HP-16C emulator modules (sys, os, stack, base_conversion, buttons, error, logging_config)

import sys
import os
import stack
import base_conversion
import buttons
from error import (
    HP16CError, IncorrectWordSizeError, NoValueToShiftError, 
    ShiftExceedsWordSizeError, InvalidBitOperationError, 
    StackUnderflowError, DivisionByZeroError, InvalidOperandError
)
from logging_config import logger, program_logger

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PARENT_DIR)


# ======================================
# Bit Manipulation Functions (Row 1)
# ======================================

def action_left_justify(display_widget, controller_obj):
    """Left Justify (LJ)."""
    controller_obj.left_justify()

def action_arithmetic_shift_right(display_widget, controller_obj):
    """Arithmetic Shift Right (ASR). Placeholder."""
    logger.info("ASR placeholder executed")

def action_rotate_left_through_carry(display_widget, controller_obj):
    """Rotate Left Through Carry (RLC). Placeholder."""
    logger.info("RLC placeholder executed")

def action_rotate_right_through_carry(display_widget, controller_obj):
    """Rotate Right Through Carry (RRC). Placeholder."""
    logger.info("RRC placeholder executed")

def action_rotate_left_through_carry_n(display_widget, controller_obj):
    """Rotate Left Through Carry n bits (RLCN). Placeholder."""
    logger.info("RLCN placeholder executed")

def action_rotate_right_through_carry_n(display_widget, controller_obj):
    """Rotate Right Through Carry n bits (RRCN). Placeholder."""
    logger.info("RRCN placeholder executed")

def action_count_bits(display_widget, controller_obj):
    """Count Bits (#B)."""
    controller_obj.count_bits()

def action_absolute(display_widget, controller_obj):
    """Absolute Value (ABS)."""
    controller_obj.absolute()

def action_double_remainder(display_widget, controller_obj):
    """Double Remainder (DBLR). Placeholder."""
    logger.info("DBLR placeholder executed")

def action_double_divide(display_widget, controller_obj):
    """Double Divide (DBL/). Placeholder."""
    logger.info("DBL/ placeholder executed")

# ======================================
# Program and Control Flow (Row 2)
# ======================================

def action_return(display_widget, controller_obj):
    if controller_obj.program_mode:
        # Record RTN instruction in program memory
        controller_obj.program_memory.append("RTN")
        controller_obj.display.set_entry(f"P {len(controller_obj.program_memory):03d}")
    else:
        # In run mode, return from subroutine (implementation depends on your stack/program logic)
        pass  # Add logic to return to the calling point

def action_label(display_widget, controller_obj):
    if controller_obj.program_mode:
        controller_obj.entry_mode = "label"
    else:
        # Ignore or handle as needed in run mode
        pass
    logger.info("LBL placeholder executed")

def action_decrement_skip_if_zero(display_widget, controller_obj):
    """Decrement, Skip if Zero (DSZ). Placeholder."""
    logger.info("DSZ placeholder executed")

def action_increment_skip_if_zero(display_widget, controller_obj):
    """Increment, Skip if Zero (ISZ). Placeholder."""
    logger.info("ISZ placeholder executed")

def action_square_root(display_widget, controller_obj):
    """Square Root (√x). Placeholder."""
    logger.info("√x placeholder executed")

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

def action_set_flag(display_widget, controller_obj):
    """Initiate setting a flag (SF)."""
    if controller_obj.program_mode:
        # Handle program mode: record SF instruction and wait for digit
        controller_obj.program_memory.append("SF")
        step = len(controller_obj.program_memory)
        program_logger.info(f"{step:03d} - SF (awaiting flag number)")
        controller_obj.display.set_entry((step, "SF"), program_mode=True)
        controller_obj.entry_mode = "set_flag"
    else:
        # In run mode, enter set_flag mode to wait for digit input
        controller_obj.entry_mode = "set_flag"
    logger.info("Entered set_flag mode")

def action_clear_flag(display_widget, controller_obj):
    """Initiate clearing a flag (CF)."""
    if controller_obj.program_mode:
        # Handle program mode if needed
        pass
    else:
        controller_obj.entry_mode = "clear_flag"
    logger.info("Entered clear_flag mode")

def action_test_flag(display_widget, controller_obj):
    """Test a flag (0-5 or CF) after entering flag number."""
    controller_obj.entry_mode = "test_flag"  # Set mode to wait for flag number
    logger.info("Entered test_flag mode awaiting flag number")

def action_double_multiply(display_widget, controller_obj):
    """Double Multiply (DBL*). Placeholder."""
    logger.info("DBL* placeholder executed")

# ======================================
# Calculator Control Functions (Row 3)
# ======================================

def action_toggle_program_run(display_widget, controller_obj):
    controller_obj.program_mode = not controller_obj.program_mode
    if controller_obj.program_mode:
        program_logger.info("PROGRAM MODE START")
        controller_obj.program_memory = []
        display_widget.set_entry((0, ""), program_mode=True)
    else:
        program_logger.info("PROGRAM MODE END")
        display_widget.set_entry(stack.peek(), program_mode=False)
    logger.info(f"Program mode: {controller_obj.program_mode}")

def action_back_step(display_widget, controller_obj):
    """Back Step (BST): Move back one step in program mode by removing the last instruction."""
    if not controller_obj.program_mode:
        logger.info("BST ignored: Not in program mode")
        return

    if controller_obj.program_memory:
        # Remove the last instruction from program memory
        removed_instruction = controller_obj.program_memory.pop()
        step = len(controller_obj.program_memory)  # New step number after removal
        
        # Log the back step action
        program_logger.info(f"BST: Removed step {step + 1:03d} - {removed_instruction}")
        logger.info(f"BST executed: Removed '{removed_instruction}', new length={len(controller_obj.program_memory)}")
        
        # Update display to show the previous step or initial state
        if controller_obj.program_memory:
            last_instruction = controller_obj.program_memory[-1]
            # Inline display code mapping
            op_map = {"/": "10", "*": "20", "-": "30", "+": "40", ".": "48", "ENTER": "36"}
            base_map = {"HEX": "23", "DEC": "24", "OCT": "25", "BIN": "26"}
            if isinstance(last_instruction, str):
                if last_instruction in op_map:
                    display_code = op_map[last_instruction]
                elif last_instruction in base_map:
                    display_code = base_map[last_instruction]
                elif last_instruction.startswith("LBL "):
                    display_code = last_instruction.split()[1]  # Label digit/letter
                elif last_instruction in "0123456789ABCDEFabcdef":
                    display_code = last_instruction.upper()
                else:
                    display_code = str(last_instruction)
            else:
                display_code = str(last_instruction)
            display_widget.set_entry((step, display_code), program_mode=True)
        else:
            # If program memory is now empty, show step 0
            display_widget.set_entry((0, ""), program_mode=True)
    else:
        # Handle empty program memory
        logger.info("BST: Program memory is already empty")
        display_widget.set_entry((0, ""), program_mode=True)

def action_roll_up(display_widget, controller_obj):
    """Rotate stack upward (R↑)."""
    if controller_obj.is_user_entry:
        entry = controller_obj.display.raw_value
        val = base_conversion.interpret_in_base(entry, controller_obj.display.mode)
        stack._x_register = val
        controller_obj.is_user_entry = False

    stack.roll_up()

    top_val = stack.peek()
    display_widget.set_entry(base_conversion.format_in_current_base(top_val, display_widget.mode))
    controller_obj.update_stack_display()

    controller_obj.stack_lift_enabled = True
    controller_obj.result_displayed = True
    logger.info("Performed R↑: stack rotated up")

def action_pause(display_widget, controller_obj):
    """Pause (PSE). Placeholder."""
    logger.info("PSE placeholder executed")

def action_clx(display_widget, controller_obj):
    """Clear X register (CLX)."""
    controller_obj.clear_x()

def action_x_less_equal_y(display_widget, controller_obj):
    """X less or equal to Y (X≤Y). Placeholder."""
    logger.info("X≤Y placeholder executed")

def action_x_less_than_zero(display_widget, controller_obj):
    """X less than zero (X<0). Placeholder."""
    logger.info("X<0 placeholder executed")

def action_x_greater_than_y(display_widget, controller_obj):
    """X greater than Y (X>Y). Placeholder."""
    logger.info("X>Y placeholder executed")

def action_x_greater_than_zero(display_widget, controller_obj):
    """X greater than zero (X>0). Placeholder."""
    logger.info("X>0 placeholder executed")

# ======================================
# Conditional & Stack Functions (Row 4)
# ======================================

def action_scroll_left(display_widget, controller_obj):
    """Scroll display one character to the left (⯇)."""
    display_widget.scroll_left()
    logger.info("Scrolled display left")

def action_scroll_right(display_widget, controller_obj):
    """Scroll display one character to the right (⯈)."""
    display_widget.scroll_right()
    logger.info("Scrolled display right")

def action_last_x(display_widget, controller_obj):
    """Last X (LST X)."""
    last_x_value = stack.last_x()
    display_widget.set_entry(last_x_value)
    display_widget.widget.after(3000, lambda: display_widget.set_entry(0))

def action_x_not_equal_y(display_widget, controller_obj):
    """X not equal Y (X≠Y). Placeholder."""
    logger.info("X≠Y placeholder executed")

def action_x_not_equal_zero(display_widget, controller_obj):
    """X not equal zero (X≠0). Placeholder."""
    logger.info("X≠0 placeholder executed")

def action_x_equal_y(display_widget, controller_obj):
    """X equal Y (X=Y). Placeholder."""
    logger.info("X=Y placeholder executed")

def action_x_equal_zero(display_widget, controller_obj):
    """X equal zero (X=0). Placeholder."""
    logger.info("X=0 placeholder executed")


G_FUNCTIONS = {

# ======================================
# Bit Manipulation Functions (Row 1)
# ======================================

    "LJ": action_left_justify,
    "ASR": action_arithmetic_shift_right,
    "RLC": action_rotate_left_through_carry,
    "RRC": action_rotate_right_through_carry,
    "RLCN": action_rotate_left_through_carry_n,
    "RRCN": action_rotate_right_through_carry_n,
    "#B": action_count_bits,
    "ABS": action_absolute,
    "DBLR": action_double_remainder,
    "DBL/": action_double_divide,

# ======================================
# Program and Control Flow (Row 2)
# ======================================

    "RTN": action_return,
    "LBL": action_label,
    "DSZ": action_decrement_skip_if_zero,
    "ISZ": action_increment_skip_if_zero,
    "√x": action_square_root,
    "1/X": action_reciprocal,
    "SF": action_set_flag,
    "CF": action_clear_flag,
    "F?": action_test_flag,
    "DBL*": action_double_multiply,

# ======================================
# Calculator Control Functions (Row 3)
# ======================================

    "P/R": action_toggle_program_run,
    "BST": action_back_step,
    "R↑": action_roll_up,
    "PSE": action_pause,
    "CLX": action_clx,
    "X≤Y": action_x_less_equal_y,
    "X<0": action_x_less_than_zero,
    "X>Y": action_x_greater_than_y,
    "X>0": action_x_greater_than_zero,

# ======================================
# Conditional & Stack Functions (Row 4)
# ======================================

    "⯇": action_scroll_left,
    "⯈": action_scroll_right,
    "LST X": action_last_x,
    "X≠Y": action_x_not_equal_y,
    "X≠0": action_x_not_equal_zero,
    "X=Y": action_x_equal_y,
    "X=0": action_x_equal_zero,
    
}

# ============================================
# g-mode Action Handler
# ============================================

def g_action(button, display_widget, controller_obj):
    sub_text = button.get("orig_sub_text", "").strip().upper()
    logger.info(f"g-mode action: {sub_text}")
    if sub_text in G_FUNCTIONS:
        G_FUNCTIONS[sub_text](display_widget, controller_obj)
        controller_obj.toggle_mode("g")  # Reset to normal
    else:
        controller_obj.toggle_mode("g")  # Reset if no action matched
    return False  # No need to return True anymore