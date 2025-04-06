"""
f_mode.py
Consolidates button logic for the f-mode in the HP-16C emulator, handling operations
like shifting, rotating, and masking.
Refactored to include type hints, detailed docstrings, and improved structure.
Author: GlobeyCode (original), refactored by ChatGPT
License: MIT
Date: 3/23/2025 (original), refactored 2025-04-01
Dependencies: Python 3.6+, HP-16C emulator modules (sys, os, buttons, stack, base_conversion, error, logging_config)
"""

from typing import Any, Dict, Callable
import sys
import os
import buttons
import stack
from error import HP16CError, IncorrectWordSizeError, NoValueToShiftError, ShiftExceedsWordSizeError, InvalidBitOperationError, StackUnderflowError, DivisionByZeroError, InvalidOperandError
from logging_config import logger, program_logger


# Setup paths for module resolution
CURRENT_DIR: str = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR: str = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PARENT_DIR)


# ======================================
# Bit Manipulation Functions (Row 1)
# ======================================

def action_shift_left(display_widget: Any, controller_obj: Any) -> None:
    """Shift Left (SL)."""
    controller_obj.shift_left()

def action_shift_right(display_widget: Any, controller_obj: Any) -> None:
    """Perform a right shift (SR)."""
    controller_obj.shift_right()

def action_rotate_left(display_widget: Any, controller_obj: Any) -> None:
    """Rotate Left (RL)."""
    controller_obj.rotate_left()

def action_rotate_right(display_widget: Any, controller_obj: Any) -> None:
    """Rotate right (RR)."""
    controller_obj.rotate_right()

def action_rotate_left_n(display_widget: Any, controller_obj: Any) -> None:
    """Rotate left with carry (RLn)."""
    controller_obj.rotate_left_carry()

def action_rotate_right_n(display_widget: Any, controller_obj: Any) -> None:
    """Rotate right with carry (RRn)."""
    controller_obj.rotate_right_carry()

def action_mask_left(display_widget: Any, controller_obj: Any) -> None:
    try:
        if len(controller_obj.stack._stack) < 1:
            raise StackUnderflowError("Need Y value for MASKL")
        controller_obj.stack.mask_left(controller_obj.stack.peek())
        top_val = controller_obj.stack.peek()
        display_widget.set_entry(
            controller_obj.stack.format_in_base(top_val, controller_obj.display.mode, pad=False)
        )
        controller_obj.update_stack_display()
        controller_obj.is_user_entry = False  # Explicitly reset
        controller_obj.display.raw_value = ""  # Clear stale raw_value
    except HP16CError as e:
        controller_obj.handle_error(e)

def action_mask_right(display_widget: Any, controller_obj: Any) -> None:
    try:
        if len(controller_obj.stack._stack) < 1:
            raise StackUnderflowError("Need Y value for MASKR")
        controller_obj.stack.mask_right(controller_obj.stack.peek())
        top_val = controller_obj.stack.peek()
        display_widget.set_entry(
            controller_obj.stack.format_in_base(top_val, controller_obj.display.mode, pad=False)
        )
        controller_obj.update_stack_display()
        controller_obj.is_user_entry = False
        controller_obj.display.raw_value = ""
        display_widget.clear_entry()  # Reset display state fully
    except HP16CError as e:
        controller_obj.handle_error(e)

def action_remainder(display_widget: Any, controller_obj: Any) -> None:
    """Retrieve the remainder from the last division (RMD)."""
    try:
        controller_obj.stack.remainder()
        top_val = controller_obj.stack.peek()
        controller_obj.display.set_entry(
            controller_obj.stack.format_in_base(top_val, controller_obj.display.mode, pad=False)
        )
        controller_obj.update_stack_display()
    except HP16CError as e:
        controller_obj.handle_error(e)

def action_bitwise_xor(display_widget: Any, controller_obj: Any) -> None:
    """Perform a logical XOR operation."""
    controller_obj.enter_operator("xor")


# ======================================
# Register & Display Functions (Row 2)
# ======================================

def action_exchange_x_indirect(display_widget: Any, controller_obj: Any) -> None:
    """Exchange X with I register (x><(i))."""
    controller_obj.exchange_x_with_i()

def action_exchange_x_index(display_widget: Any, controller_obj: Any) -> None:
    """Exchange X with I register (x><I)."""
    controller_obj.exchange_x_with_i()

def action_show(display_widget: Any, controller_obj: Any, mode: str) -> bool:
    """
    Temporarily change the display mode for 2 seconds and update the display value accordingly.

    Args:
        mode: The new mode to display (e.g., "HEX", "DEC", "OCT", "BIN").

    Returns:
        True if the mode toggle was handled.
    """
    # Store the original mode
    current_mode: str = controller_obj.display.mode
    
    # Get the current value from the stack
    current_value = controller_obj.stack.peek()
    
    # Set the temporary mode and update the display value
    display_widget.set_mode(mode)
    display_widget.hide_f_mode()
    temp_value_str = controller_obj.stack.format_in_base(current_value, mode, pad=False)
    display_widget.set_entry(temp_value_str, raw=True)

    # Revert all buttons (except special ones) to normal
    import buttons  # Avoid circular import issues
    for btn in controller_obj.buttons:
        if btn.get("command_name") not in ("yellow_f_function", "blue_g_function"):
            buttons.revert_to_normal(btn, controller_obj.buttons, display_widget, controller_obj)

    # After 2 seconds, revert to the original mode and restore the display value
    def revert_display() -> None:
        display_widget.set_mode(current_mode)
        original_value_str = controller_obj.stack.format_in_base(current_value, current_mode, pad=False)
        display_widget.set_entry(original_value_str, raw=True)
        controller_obj.f_mode_active = False

    display_widget.widget.after(2000, revert_display)
    return True

def action_set_bit(display_widget: Any, controller_obj: Any) -> None:
    """Set a specific bit (SB)."""
    try:
        if controller_obj.is_user_entry:
            bit_index = int(display_widget.raw_value or "0")
        else:
            bit_index = controller_obj.stack.peek()  # Use X if no new entry
        controller_obj.set_bit(bit_index)
    except ValueError:
        controller_obj.handle_error(InvalidBitOperationError("Invalid bit index"))

def action_clear_bit(display_widget: Any, controller_obj: Any) -> None:
    """Clear a specific bit (CB)."""
    try:
        bit_index: int = int(display_widget.raw_value or "0")
        controller_obj.set_bit(bit_index)  # Possibly should call clear_bit? Adjust as needed.
    except ValueError:
        controller_obj.handle_error(InvalidBitOperationError("Invalid bit index"))

def action_test_bit(display_widget: Any, controller_obj: Any) -> None:
    """Test if a specific bit is set (B?)."""
    try:
        bit_index: int = int(display_widget.raw_value or "0")
        result: int = controller_obj.test_bit(bit_index)
        display_widget.set_entry(str(result))
    except ValueError:
        controller_obj.handle_error(InvalidBitOperationError("Invalid bit index"))

def action_bitwise_and(display_widget: Any, controller_obj: Any) -> None:
    """Perform a logical AND operation."""
    controller_obj.enter_operator("and")


# ======================================
# Calculator Control Functions (Row 3)
# ======================================

def action_store_index_indirect(display_widget: Any, controller_obj: Any) -> None:
    """Store the current X register into the I register ((I))."""
    controller_obj.store_in_i()

def action_recall_index(display_widget: Any, controller_obj: Any) -> None:
    """Recall the I register value (I)."""
    controller_obj.recall_i()

def action_clear_program(display_widget: Any, controller_obj: Any) -> None:
    """
    Clear the program memory and reset the display (CLR PRGM).
    
    Only applicable in program mode.
    """
    if controller_obj.program_mode:
        controller_obj.program_memory = []
        display_widget.set_entry((0, ""), program_mode=True)
        logger.info("Program memory cleared")
        program_logger.info("PROGRAM CLEARED")
    else:
        logger.info("CLR PRGM ignored - not in program mode")

def action_clear_register(display_widget: Any, controller_obj: Any) -> bool:
    """
    Clear all data storage registers.
    
    Reverts buttons to normal mode, exits f-mode, and blinks the display.
    Returns True on success.
    """
    stack.clear_registers()
    logger.info("All data storage registers cleared to zero")
    for btn in controller_obj.buttons:
        if btn.get("command_name") not in ("yellow_f_function", "blue_g_function", "reload_program"):
            buttons.revert_to_normal(btn, controller_obj.buttons, display_widget, controller_obj)
    controller_obj.f_mode_active = False
    display_widget.hide_f_mode()
    current_value = stack.peek()
    formatted_value = format_in_current_base(current_value, display_widget.mode)
    display_widget.set_entry(formatted_value, blink=True)
    return True

def action_clear_prefix(display_widget: Any, controller_obj: Any) -> bool:
    """
    Clear any pending prefix operations (CLR PRFX).
    
    Resets mode states, hides indicators, reverts buttons, and refreshes the display.
    Returns True on success.
    """
    controller_obj.entry_mode = None
    controller_obj.f_mode_active = False
    controller_obj.g_mode_active = False
    display_widget.hide_f_mode()
    display_widget.hide_g_mode()
    for btn in controller_obj.buttons:
        if btn.get("command_name") not in ("yellow_f_function", "blue_g_function", "reload_program"):
            buttons.revert_to_normal(btn, controller_obj.buttons, display_widget, controller_obj)
    from base_conversion import format_in_current_base
    current_x = stack.peek()
    formatted_x = format_in_current_base(current_x, display_widget.mode)
    display_widget.set_entry(formatted_x)
    logger.info("Clear Prefix: Reset prefix states, reverted buttons, and refreshed display")
    return True

def action_set_window(display_widget: Any, controller_obj: Any) -> None:
    """Window function (not implemented)."""
    pass

def action_set_complement_1s(display_widget: Any, controller_obj: Any) -> None:
    """Set the complement mode to 1's (SC 1'S)."""
    controller_obj.set_complement_mode("1S")

def action_set_complement_2s(display_widget: Any, controller_obj: Any) -> None:
    """Set the complement mode to 2's (SC 2'S)."""
    controller_obj.set_complement_mode("2S")

def action_set_complement_unsigned(display_widget: Any, controller_obj: Any) -> None:
    """Set the complement mode to Unsigned (SC UNSGN)."""
    controller_obj.set_complement_mode("UNSIGNED")

def action_bitwise_not(display_widget: Any, controller_obj: Any) -> None:
    """Perform a logical NOT operation."""
    controller_obj.enter_operator("not")


# ============================================
# System & Configuration Functions (Row 4)
# ============================================

def action_set_word_size(display_widget: Any, controller_obj: Any) -> None:
    """Set the word size (WSIZE). Uses X as the bit count."""
    try:
        bits: int = controller_obj.stack.peek()
        controller_obj.set_word_size(bits)
        top_val = controller_obj.stack.peek()
        controller_obj.display.set_entry(
            controller_obj.stack.format_in_base(top_val, controller_obj.display.mode, pad=False)
        )
        controller_obj.update_stack_display()
    except HP16CError as e:
        controller_obj.handle_error(e)

def action_set_float_mode(display_widget: Any, controller_obj: Any) -> None:
    """
    Set the calculator to FLOAT mode and prepare to set decimal places.
    
    The entry mode is set to "set_decimal_places" and the display is reset.
    """
    controller_obj.entry_mode = "set_decimal_places"
    display_widget.set_entry("0", raw=True, blink=True)

def action_memory_status(display_widget: Any, controller_obj: Any) -> None:
    """Memory status (MEM) function (not implemented)."""
    pass

def action_show_status(display_widget: Any, controller_obj: Any) -> None:
    """
    Show the stack status (STATUS) for 5 seconds.
    
    Toggles the stack display and hides it after 5 seconds.
    """
    current_mode: str = controller_obj.display.mode
    display_widget.toggle_stack_display(current_mode)
    def hide_stack() -> None:
        display_widget.show_stack = False
        display_widget.stack_content.config(text="")
    display_widget.widget.after(5000, hide_stack)

def action_enter_exponent(display_widget: Any, controller_obj: Any) -> None:
    """
    Enter an exponent (EEx) in FLOAT mode.
    
    Appends 'E' to the raw value; otherwise, triggers an error.
    """
    if controller_obj.display.mode == "FLOAT":
        display_widget.raw_value += "E"
        display_widget.set_entry(display_widget.raw_value)
    else:
        controller_obj.handle_error(HP16CError("EEx only in FLOAT mode", "E108"))

def action_bitwise_or(display_widget: Any, controller_obj: Any) -> None:
    """Perform a logical OR operation."""
    controller_obj.enter_operator("or")


# ============================================
# f-mode Action Handler Dictionary & Function
# ============================================

F_FUNCTIONS: Dict[str, Callable[[Any, Any], None]] = {
    # Bit Manipulation Functions (Row 1)
    "SL": action_shift_left,
    "SR": action_shift_right,
    "RL": action_rotate_left,
    "RR": action_rotate_right,
    "RLN": action_rotate_left_n,
    "RRN": action_rotate_right_n,
    "MASKL": action_mask_left,
    "MASKR": action_mask_right,
    "RMD": action_remainder,
    "XOR": action_bitwise_xor,
    # Register & Display Functions (Row 2)
    "X><(I)": action_exchange_x_indirect,
    "X><I": action_exchange_x_index,
    "SHOW HEX": lambda dw, co: action_show(dw, co, "HEX"),
    "SHOW DEC": lambda dw, co: action_show(dw, co, "DEC"),
    "SHOW OCT": lambda dw, co: action_show(dw, co, "OCT"),
    "SHOW BIN": lambda dw, co: action_show(dw, co, "BIN"),
    "SB": action_set_bit,
    "CB": action_clear_bit,
    "B?": action_test_bit,
    "AND": action_bitwise_and,
    # Calculator Control Functions (Row 3)
    "(I)": action_store_index_indirect,
    "I": action_recall_index,
    "CLR PRGM": action_clear_program,
    "CLR REG": action_clear_register,
    "CLR PRFX": action_clear_prefix,
    "WINDOW": action_set_window,
    "SC 1'S": action_set_complement_1s,
    "SC 2'S": action_set_complement_2s,
    "SC UNSGN": action_set_complement_unsigned,
    "NOT": action_bitwise_not,
    # System & Configuration Functions (Row 4)
    "WSIZE": action_set_word_size,
    "FLOAT": action_set_float_mode,
    "MEM": action_memory_status,
    "STATUS": action_show_status,
    "EEX": action_enter_exponent,
    "OR": action_bitwise_or,
}


def f_action(button: Dict[str, Any], display_widget: Any, controller_obj: Any) -> bool:
    """
    Handle an f-mode action based on the button's original top text.
    
    If the top text (trimmed and uppercased) is found in F_FUNCTIONS,
    execute the corresponding action. After execution, reset f-mode.
    
    Returns:
        False indicating no further processing is required.
    """
    top_text: str = button.get("orig_top_text", "").strip().upper()
    logger.info(f"f-mode action: {top_text}")
    if top_text in F_FUNCTIONS:
        result = F_FUNCTIONS[top_text](display_widget, controller_obj)
        # If the result is not explicitly a boolean (for special cases), reset f-mode.
        if not isinstance(result, bool):
            controller_obj.toggle_mode("f")
        return result  # May return a boolean result.
    controller_obj.toggle_mode("f")
    return False
