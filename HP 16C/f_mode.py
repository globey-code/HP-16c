# f_mode.py
# Consolidates button logic for the f-mode in the HP-16C emulator, handling operations like shifting, rotating, and masking.
# Author: GlobeyCode
# License: MIT
# Date: 3/23/2025
# Dependencies: Python 3.6+, HP-16C emulator modules (sys, os, buttons, stack, base_conversion, error, logging_config)

import sys
import os
import buttons
import stack
from base_conversion import format_in_current_base, interpret_in_base
from error import (
    HP16CError, IncorrectWordSizeError, NoValueToShiftError, 
    ShiftExceedsWordSizeError, InvalidBitOperationError
)
from logging_config import logger, program_logger

# ======================================
# Bit Manipulation Functions (Row 1)
# ======================================

def action_shift_left(display_widget, controller_obj):
    """Shift Left (SL)."""
    controller_obj.shift_left()

def action_shift_right(display_widget, controller_obj):
    """Shift Right (SR)."""
    controller_obj.shift_right()

def action_rotate_left(display_widget, controller_obj):
    """Rotate Left (RL)."""
    controller_obj.rotate_left()

def action_rotate_right(display_widget, controller_obj):
    """Rotate Right (RR)."""
    controller_obj.rotate_right()

def action_rotate_left_n(display_widget, controller_obj):
    """Rotate Left with Carry (RLn)."""
    controller_obj.rotate_left_carry()

def action_rotate_right_n(display_widget, controller_obj):
    """Rotate Right with Carry (RRn)."""
    controller_obj.rotate_right_carry()

def action_mask_left(display_widget, controller_obj):
    """Mask Left (MASKL)."""
    try:
        bits = int(display_widget.raw_value or "0")
        controller_obj.mask_left(bits)
    except ValueError:
        controller_obj.handle_error(InvalidBitOperationError("Invalid bit count"))

def action_mask_right(display_widget, controller_obj):
    """Mask Right (MASKR)."""
    try:
        bits = int(display_widget.raw_value or "0")
        controller_obj.mask_right(bits)
    except ValueError:
        controller_obj.handle_error(InvalidBitOperationError("Invalid bit count"))

def action_remainder(display_widget, controller_obj):
    """Double Remainder (RMD)."""
    controller_obj.double_remainder()

def action_bitwise_xor(display_widget, controller_obj):
    """Logical XOR."""
    controller_obj.enter_operator("xor")

# ========================================
# Register & Display Functions (Row 2)
# ========================================

def action_exchange_x_indirect(display_widget, controller_obj):
    """Exchange X with I register (x><(i))."""
    controller_obj.exchange_x_with_i()

def action_exchange_x_index(display_widget, controller_obj):
    """Exchange X with I register (x><I)."""
    controller_obj.exchange_x_with_i()

def action_show(display_widget, controller_obj, mode):
    current_mode = controller_obj.display.mode
    
    # Set the new mode for 4 seconds
    display_widget.set_mode(mode)
    
    # Immediately revert buttons to normal (except for specific functions)
    import buttons  # Import here to avoid circular import
    for btn in controller_obj.buttons:
        if btn.get("command_name") not in ("yellow_f_function", "blue_g_function"):
            buttons.revert_to_normal(btn, controller_obj.buttons, display_widget, controller_obj)
    
    # After 4 seconds, revert display to base mode and finalize state
    def revert_display():
        display_widget.set_mode(current_mode)
        controller_obj.f_mode_active = False
    
    display_widget.widget.after(2000, revert_display)
    return True  # Indicate that mode toggle is handled

def action_set_bit(display_widget, controller_obj):
    """Set Bit (SB)."""
    try:
        bit_index = int(display_widget.raw_value or "0")
        controller_obj.set_bit(bit_index)
    except ValueError:
        controller_obj.handle_error(InvalidBitOperationError("Invalid bit index"))

def action_clear_bit(display_widget, controller_obj):
    """Clear Bit (CB)."""
    try:
        bit_index = int(display_widget.raw_value or "0")
        controller_obj.set_bit(bit_index)
    except ValueError:
        controller_obj.handle_error(InvalidBitOperationError("Invalid bit index"))

def action_test_bit(display_widget, controller_obj):
    """Test Bit (B?)."""
    try:
        bit_index = int(display_widget.raw_value or "0")
        result = controller_obj.test_bit(bit_index)
        display_widget.set_entry(str(result))
    except ValueError:
        controller_obj.handle_error(InvalidBitOperationError("Invalid bit index"))

def action_bitwise_and(display_widget, controller_obj):
    """Logical AND."""
    controller_obj.enter_operator("and")

# ========================================
# Calculator Control Functions (Row 3)
# ========================================

def action_store_index_indirect(display_widget, controller_obj):
    """Store in I register ((i))."""
    controller_obj.store_in_i()

def action_recall_index(display_widget, controller_obj):
    """Recall from I register (I)."""
    controller_obj.recall_i()

def action_clear_program(display_widget, controller_obj):
    """Clear Program (CLR PRGM) - Reset program memory and display to 000- in program mode."""
    if controller_obj.program_mode:
        controller_obj.program_memory = []  # Clear program memory
        display_widget.set_entry((0, ""), program_mode=True)  # Reset display to "000- "
        logger.info("Program memory cleared")
        program_logger.info("PROGRAM CLEARED")  # Log to program.log
    else:
        logger.info("CLR PRGM ignored - not in program mode")

def action_clear_registers(display_widget, controller_obj):
    """Clear Registers (CLR REG)."""
    stack_state = stack.get_state()
    for i in range(len(stack_state)):
        stack.pop()
        stack.push(0, duplicate_x=False)
    display_widget.clear_entry()
    controller_obj.update_stack_display()

def action_clear_prefix(display_widget, controller_obj):
    """Clear Prefix (CLR PRFX) - Reset modes."""
    controller_obj.f_mode_active = False
    controller_obj.g_mode_active = False

def action_set_window(display_widget, controller_obj):
    """Window - Not implemented."""
    pass

def action_set_complement_1s(display_widget, controller_obj):
    """Set Complement Mode to 1's (SC 1'S)."""
    controller_obj.set_complement_mode("1S")

def action_set_complement_2s(display_widget, controller_obj):
    """Set Complement Mode to 2's (SC 2'S)."""
    controller_obj.set_complement_mode("2S")

def action_set_complement_unsigned(display_widget, controller_obj):
    """Set Complement Mode to Unsigned (SC UNSGN)."""
    controller_obj.set_complement_mode("UNSIGNED")

def action_bitwise_not(display_widget, controller_obj):
    """Logical NOT."""
    controller_obj.enter_operator("not")

# ============================================
# System & Configuration Functions (Row 4)
# ============================================

def action_set_word_size(display_widget, controller_obj):
    try:
        # Get the raw value (default to "0" if empty)
        raw_value = display_widget.raw_value or "0"
        
        # Determine the current mode and convert to decimal accordingly
        current_mode = controller_obj.display.mode
        if current_mode == "HEX":
            bits = int(raw_value, 16)  # Convert from hexadecimal to decimal
        elif current_mode == "OCT":
            bits = int(raw_value, 8)   # Convert from octal to decimal
        elif current_mode == "BIN":
            bits = int(raw_value, 2)   # Convert from binary to decimal
        else:  # Assume DEC or other modes are already in decimal
            bits = int(raw_value)      # Direct conversion from string to decimal
        
        # Default to 64 if the value is 0
        if bits == 0:
            bits = 64
        
        # Set the word size (assumes set_word_size handles display updates)
        if controller_obj.set_word_size(bits):
            pass  # No need to clear_entry() here
    except ValueError:
        controller_obj.handle_error(IncorrectWordSizeError())

def action_set_float_mode(display_widget, controller_obj):
    """Set Float Mode (FLOAT)."""
    controller_obj.display.mode = "FLOAT"
    current_val = float(display_widget.raw_value or "0")
    display_widget.set_entry(current_val)
    controller_obj.update_stack_display()

def action_memory_status(display_widget, controller_obj):
    """Memory Info (MEM) - Not implemented."""
    pass

def action_show_status(display_widget, controller_obj):
    """Show Stack Status (STATUS) for 5 seconds."""
    current_mode = controller_obj.display.mode
    display_widget.toggle_stack_display(current_mode)

    def hide_stack():
        display_widget.show_stack = False
        display_widget.stack_content.config(text="")

    display_widget.widget.after(5000, hide_stack)

def action_enter_exponent(display_widget, controller_obj):
    """Enter Exponent (EEx) in FLOAT mode."""
    if controller_obj.display.mode == "FLOAT":
        display_widget.raw_value += "E"
        display_widget.set_entry(display_widget.raw_value)
    else:
        controller_obj.handle_error(HP16CError("EEx only in FLOAT mode", "E108"))

def action_bitwise_or(display_widget, controller_obj):
    """Logical OR."""
    controller_obj.enter_operator("or")

F_FUNCTIONS = {

# ======================================
# Bit Manipulation Functions (Row 1)
# ======================================
   
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
    
# ========================================
# Register & Display Functions (Row 2)
# ========================================

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
    
# ========================================
# Calculator Control Functions (Row 3)
# ========================================

    "(I)": action_store_index_indirect, 
    "I": action_recall_index,
    "CLR PRGM": action_clear_program, 
    "CLR REG": action_clear_registers, 
    "CLR PRFX": action_clear_prefix,
    "WINDOW": action_set_window, 
    "SC 1'S": action_set_complement_1s, 
    "SC 2'S": action_set_complement_2s, 
    "SC UNSGN": action_set_complement_unsigned,
    "NOT": action_bitwise_not, 

# ============================================
# System & Configuration Functions (Row 4)
# ============================================    

    "WSIZE": action_set_word_size, 
    "FLOAT": action_set_float_mode, 
    "MEM": action_memory_status,
    "STATUS": action_show_status, 
    "EEX": action_enter_exponent, 
    "OR": action_bitwise_or,
}

# ============================================
# f-mode Action Handler
# ============================================

def f_action(button, display_widget, controller_obj):
    top_text = button.get("orig_top_text", "").strip().upper()
    logger.info(f"f-mode action: {top_text}")
    if top_text in F_FUNCTIONS:
        result = F_FUNCTIONS[top_text](display_widget, controller_obj)
        if not isinstance(result, bool):  # Only reset if not a special case (e.g., SHOW)
            controller_obj.toggle_mode("f")  # Reset to normal
        return result
    controller_obj.toggle_mode("f")  # Reset if no action matched
    return False