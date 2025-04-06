"""
g_mode.py
Consolidates button logic for the g-mode in the HP-16C emulator,
handling operations such as left justification, reciprocal, and flag management.
Refactored to include type hints and clearer structure.
Author: GlobeyCode (original), refactored by ChatGPT
License: MIT
Date: 3/23/2025 (original), refactored 2025-04-01
Dependencies: Python 3.6+, tkinter (for types), and HP-16C emulator modules (sys, os, stack, base_conversion, buttons, error, logging_config)
"""

from typing import Any, Callable, Dict
import sys
import os
import stack

from error import HP16CError
from logging_config import logger, program_logger

# Set up paths
CURRENT_DIR: str = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR: str = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PARENT_DIR)


# ======================================
# Bit Manipulation Functions (Row 1)
# ======================================

def action_left_justify(display_widget: Any, controller_obj: Any) -> None:
    """Perform Left Justify (LJ)."""
    controller_obj.left_justify()

def action_arithmetic_shift_right(display_widget: Any, controller_obj: Any) -> None:
    """Arithmetic Shift Right (ASR). Placeholder implementation."""
    logger.info("ASR placeholder executed")

def action_rotate_left_through_carry(display_widget: Any, controller_obj: Any) -> None:
    """Rotate Left Through Carry (RLC). Placeholder implementation."""
    logger.info("RLC placeholder executed")

def action_rotate_right_through_carry(display_widget: Any, controller_obj: Any) -> None:
    """Rotate Right Through Carry (RRC). Placeholder implementation."""
    logger.info("RRC placeholder executed")

def action_rotate_left_through_carry_n(display_widget: Any, controller_obj: Any) -> None:
    """Rotate Left Through Carry n bits (RLCN). Placeholder implementation."""
    logger.info("RLCN placeholder executed")

def action_rotate_right_through_carry_n(display_widget: Any, controller_obj: Any) -> None:
    """Rotate Right Through Carry n bits (RRCN). Placeholder implementation."""
    logger.info("RRCN placeholder executed")

def action_count_bits(display_widget: Any, controller_obj: Any) -> None:
    """Count the number of 1 bits in X (#B)."""
    controller_obj.count_bits()

def action_absolute(display_widget: Any, controller_obj: Any) -> None:
    """Compute the absolute value (ABS)."""
    controller_obj.absolute()

def action_double_remainder(display_widget: Any, controller_obj: Any) -> None:
    """Double Remainder (DBLR). Placeholder implementation."""
    logger.info("DBLR placeholder executed")

def action_double_divide(display_widget: Any, controller_obj: Any) -> None:
    """Double Divide (DBL÷). Placeholder implementation."""
    logger.info("DBL÷ placeholder executed")


# ======================================
# Program and Control Flow (Row 2)
# ======================================

def action_return(display_widget: Any, controller_obj: Any) -> None:
    """
    Process a Return (RTN) command.
    In program mode, record the RTN instruction.
    """
    if controller_obj.program_mode:
        controller_obj.program_memory.append("RTN")
        controller_obj.display.set_entry(f"P {len(controller_obj.program_memory):03d}")
    else:
        # In run mode, implement subroutine return logic if needed.
        pass

def action_label(display_widget: Any, controller_obj: Any) -> None:
    """
    Process a Label (LBL) command.
    In program mode, set the entry mode to label.
    """
    if controller_obj.program_mode:
        controller_obj.entry_mode = "label"
    else:
        # For run mode, additional handling may be added.
        pass
    logger.info("LBL placeholder executed")

def action_decrement_skip_if_zero(display_widget: Any, controller_obj: Any) -> None:
    """Decrement and Skip if Zero (DSZ). Placeholder implementation."""
    logger.info("DSZ placeholder executed")

def action_increment_skip_if_zero(display_widget: Any, controller_obj: Any) -> None:
    """Increment and Skip if Zero (ISZ). Placeholder implementation."""
    logger.info("ISZ placeholder executed")

def action_square_root(display_widget: Any, controller_obj: Any) -> None:
    """Compute the square root (√x). Placeholder implementation."""
    logger.info("√x placeholder executed")

def action_reciprocal(display_widget: Any, controller_obj: Any) -> None:
    """
    Compute the reciprocal (1/X) of the top-of-stack.
    If division by zero occurs, an error is handled.
    """
    try:
        val = controller_obj.stack.peek()  # Use peek instead of pop to avoid modifying stack prematurely
        if val == 0:
            controller_obj.handle_error(HP16CError("Division by zero", "E02"))
            return
        result = 1 / val if controller_obj.display.mode == "FLOAT" else int(1 / val)
        controller_obj.stack._x_register = result  # Update X directly
        new_str = controller_obj.stack.format_in_base(result, controller_obj.display.mode, pad=False)
        display_widget.set_entry(new_str)
        display_widget.raw_value = new_str
        controller_obj.update_stack_display()
    except HP16CError as e:
        controller_obj.handle_error(e)

def action_set_flag(display_widget: Any, controller_obj: Any) -> None:
    """Initiate setting a flag (SF). Waits for digit input (0-5)."""
    controller_obj.entry_mode = "set_flag"
    logger.info("Entered set_flag mode awaiting flag number (0-5)")

def action_clear_flag(display_widget: Any, controller_obj: Any) -> None:
    """Initiate clearing a flag (CF). Waits for digit input (0-5)."""
    controller_obj.entry_mode = "clear_flag"
    logger.info("Entered clear_flag mode awaiting flag number (0-5)")

def action_test_flag(display_widget: Any, controller_obj: Any) -> None:
    """Initiate testing a flag (F?). Waits for digit input (0-5)."""
    controller_obj.entry_mode = "test_flag"
    logger.info("Entered test_flag mode awaiting flag number (0-5)")

def action_double_multiply(display_widget: Any, controller_obj: Any) -> None:
    """Double Multiply (DBL×). Placeholder implementation."""
    logger.info("DBL× placeholder executed")


# ======================================
# Calculator Control Functions (Row 3)
# ======================================

def action_toggle_program_run(display_widget: Any, controller_obj: Any) -> None:
    """
    Toggle program mode on/off.
    
    In program mode, record program instructions and update the display.
    In run mode, update the display to show the current X register.
    """
    controller_obj.program_mode = not controller_obj.program_mode
    if controller_obj.program_mode:
        program_logger.info("PROGRAM MODE START")
        if not controller_obj.program_memory:
            display_widget.set_entry((0, ""), program_mode=True)
        else:
            last_step = len(controller_obj.program_memory) - 1
            if last_step >= 0 and controller_obj.program_memory:
                last_instruction = controller_obj.program_memory[last_step]
                op_map = {"/": "10", "*": "20", "-": "30", "+": "40", ".": "48", "ENTER": "36"}
                base_map = {"HEX": "23", "DEC": "24", "OCT": "25", "BIN": "26"}
                if isinstance(last_instruction, str):
                    if last_instruction in op_map:
                        display_code = op_map[last_instruction]
                    elif last_instruction in base_map:
                        display_code = base_map[last_instruction]
                    elif last_instruction.startswith("LBL "):
                        display_code = last_instruction.split()[1]
                    elif last_instruction in "0123456789ABCDEFabcdef":
                        display_code = last_instruction.upper()
                    else:
                        display_code = str(last_instruction)
                else:
                    display_code = str(last_instruction)
                display_widget.set_entry((last_step + 1, display_code), program_mode=True)
            else:
                display_widget.set_entry((0, ""), program_mode=True)
    else:
        program_logger.info("PROGRAM MODE END")
        display_widget.set_entry(stack.peek(), program_mode=False)
    logger.info(f"Program mode: {controller_obj.program_mode}")

def action_back_step(display_widget: Any, controller_obj: Any) -> None:
    """
    Back Step (BST): Remove the last instruction in program mode and update the display.
    """
    if not controller_obj.program_mode:
        logger.info("BST ignored: Not in program mode")
        return

    if controller_obj.program_memory:
        removed_instruction = controller_obj.program_memory.pop()
        step = len(controller_obj.program_memory)
        program_logger.info(f"BST: Removed step {step + 1:03d} - {removed_instruction}")
        logger.info(f"BST executed: Removed '{removed_instruction}', new length={len(controller_obj.program_memory)}")
        if controller_obj.program_memory:
            last_instruction = controller_obj.program_memory[-1]
            op_map = {"/": "10", "*": "20", "-": "30", "+": "40", ".": "48", "ENTER": "36"}
            base_map = {"HEX": "23", "DEC": "24", "OCT": "25", "BIN": "26"}
            if isinstance(last_instruction, str):
                if last_instruction in op_map:
                    display_code = op_map[last_instruction]
                elif last_instruction in base_map:
                    display_code = base_map[last_instruction]
                elif last_instruction.startswith("LBL "):
                    display_code = last_instruction.split()[1]
                elif last_instruction in "0123456789ABCDEFabcdef":
                    display_code = last_instruction.upper()
                else:
                    display_code = str(last_instruction)
            else:
                display_code = str(last_instruction)
            display_widget.set_entry((step, display_code), program_mode=True)
        else:
            display_widget.set_entry((0, ""), program_mode=True)
    else:
        logger.info("BST: Program memory is already empty")
        display_widget.set_entry((0, ""), program_mode=True)

def action_roll_up(display_widget: Any, controller_obj: Any) -> None:
    logger.info(f"R↑ entry: is_user_entry={controller_obj.is_user_entry}, raw_value={controller_obj.display.raw_value}")
    if controller_obj.is_user_entry and controller_obj.display.raw_value:
        entry = controller_obj.display.raw_value
        val = controller_obj.stack.interpret_in_base(entry, controller_obj.display.mode)
        controller_obj.stack._x_register = val
        controller_obj.is_user_entry = False
    controller_obj.stack.roll_up()
    top_val = controller_obj.stack.peek()
    logger.info(f"R↑ result: X={top_val}, stack={controller_obj.stack._stack}")
    display_widget.set_entry(controller_obj.stack.format_in_base(top_val, display_widget.mode, pad=False))
    controller_obj.update_stack_display()
    controller_obj.stack_lift_enabled = True
    controller_obj.result_displayed = True
    logger.info("Performed R↑: stack rotated up")

def action_pause(display_widget: Any, controller_obj: Any) -> None:
    """Pause (PSE). Placeholder implementation."""
    logger.info("PSE placeholder executed")

def action_clx(display_widget: Any, controller_obj: Any) -> None:
    """Clear X register (CLX)."""
    controller_obj.clear_x()

def action_x_less_equal_y(display_widget: Any, controller_obj: Any) -> None:
    """X less or equal to Y (X≤Y). Placeholder implementation."""
    logger.info("X≤Y placeholder executed")

def action_x_less_than_zero(display_widget: Any, controller_obj: Any) -> None:
    """X less than zero (X<0). Placeholder implementation."""
    logger.info("X<0 placeholder executed")

def action_x_greater_than_y(display_widget: Any, controller_obj: Any) -> None:
    """X greater than Y (X>Y). Placeholder implementation."""
    logger.info("X>Y placeholder executed")

def action_x_greater_than_zero(display_widget: Any, controller_obj: Any) -> None:
    """X greater than zero (X>0). Placeholder implementation."""
    logger.info("X>0 placeholder executed")


# ======================================
# Conditional & Stack Functions (Row 4)
# ======================================

def action_scroll_left(display_widget: Any, controller_obj: Any) -> None:
    """Scroll the display one character to the left (⯇)."""
    display_widget.scroll_left()
    logger.info("Scrolled display left")

def action_scroll_right(display_widget: Any, controller_obj: Any) -> None:
    """Scroll the display one character to the right (⯈)."""
    display_widget.scroll_right()
    logger.info("Scrolled display right")

def action_last_x(display_widget: Any, controller_obj: Any) -> None:
    """Recall the last X value (LST X) into the X register."""
    last_x_value = controller_obj.stack.last_x()
    controller_obj.stack.push(last_x_value)
    formatted_value = controller_obj.stack.format_in_base(last_x_value, display_widget.mode, pad=False)
    display_widget.set_entry(formatted_value)
    controller_obj.update_stack_display()
    controller_obj.stack_lift_enabled = False  # Mimics HP-16C: no stack lift after recall
    logger.info(f"Recalled last X value into X register: {formatted_value}")

def action_x_not_equal_y(display_widget: Any, controller_obj: Any) -> None:
    """X not equal Y (X≠Y). Placeholder implementation."""
    logger.info("X≠Y placeholder executed")

def action_x_not_equal_zero(display_widget: Any, controller_obj: Any) -> None:
    """X not equal zero (X≠0). Placeholder implementation."""
    logger.info("X≠0 placeholder executed")

def action_x_equal_y(display_widget: Any, controller_obj: Any) -> None:
    """X equal Y (X=Y). Placeholder implementation."""
    logger.info("X=Y placeholder executed")

def action_x_equal_zero(display_widget: Any, controller_obj: Any) -> None:
    """X equal zero (X=0). Placeholder implementation."""
    logger.info("X=0 placeholder executed")


# ============================================
# g-mode Action Handler Dictionary & Function
# ============================================

# Mapping of g-mode sub-commands to their handler functions.
G_FUNCTIONS: Dict[str, Callable[[Any, Any], None]] = {
    # Bit Manipulation Functions (Row 1)
    "LJ": action_left_justify,
    "ASR": action_arithmetic_shift_right,
    "RLC": action_rotate_left_through_carry,
    "RRC": action_rotate_right_through_carry,
    "RLCN": action_rotate_left_through_carry_n,
    "RRCN": action_rotate_right_through_carry_n,
    "#B": action_count_bits,
    "ABS": action_absolute,
    "DBLR": action_double_remainder,
    "DBL÷": action_double_divide,
    # Program and Control Flow (Row 2)
    "RTN": action_return,
    "LBL": action_label,
    "DSZ": action_decrement_skip_if_zero,
    "ISZ": action_increment_skip_if_zero,
    "√X": action_square_root,
    "1/X": action_reciprocal,
    "SF": action_set_flag,
    "CF": action_clear_flag,
    "F?": action_test_flag,
    "DBL×": action_double_multiply,
    # Calculator Control Functions (Row 3)
    "P/R": action_toggle_program_run,
    "BST": action_back_step,
    "R↑": action_roll_up,
    "PSE": action_pause,
    "CLX": action_clx,
    "X≤Y": action_x_less_equal_y,
    "X<0": action_x_less_than_zero,
    "X>Y": action_x_greater_than_y,
    "X>0": action_x_greater_than_zero,
    # Conditional & Stack Functions (Row 4)
    "⯇": action_scroll_left,
    "⯈": action_scroll_right,
    "LST X": action_last_x,
    "X≠Y": action_x_not_equal_y,
    "X≠0": action_x_not_equal_zero,
    "X=Y": action_x_equal_y,
    "X=0": action_x_equal_zero,
}


def g_action(button: Dict[str, Any], display_widget: Any, controller_obj: Any) -> bool:
    """
    Handle a g-mode action based on the button's original sub-text.
    
    If the sub-text matches a key in G_FUNCTIONS, call the corresponding function,
    then reset the g-mode.
    
    Returns:
        False (indicating that further processing is not needed).
    """
    sub_text: str = button.get("orig_sub_text", "").strip().upper()
    logger.info(f"g-mode action: {sub_text}")
    if sub_text in G_FUNCTIONS:
        G_FUNCTIONS[sub_text](display_widget, controller_obj)
        controller_obj.toggle_mode("g")  # Reset mode to normal after action.
    else:
        controller_obj.toggle_mode("g")  # Reset mode if no action matched.
    return False
