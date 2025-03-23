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
from logging_config import logger

def action_sl(display_widget, controller_obj):
    """Shift Left (SL)."""
    controller_obj.shift_left()

def action_sr(display_widget, controller_obj):
    """Shift Right (SR)."""
    controller_obj.shift_right()

def action_rl(display_widget, controller_obj):
    """Rotate Left (RL)."""
    controller_obj.rotate_left()

def action_rr(display_widget, controller_obj):
    """Rotate Right (RR)."""
    controller_obj.rotate_right()

def action_rln(display_widget, controller_obj):
    """Rotate Left with Carry (RLn)."""
    controller_obj.rotate_left_carry()

def action_rrn(display_widget, controller_obj):
    """Rotate Right with Carry (RRn)."""
    controller_obj.rotate_right_carry()

def action_maskl(display_widget, controller_obj):
    """Mask Left (MASKL)."""
    try:
        bits = int(display_widget.raw_value or "0")
        controller_obj.mask_left(bits)
    except ValueError:
        controller_obj.handle_error(InvalidBitOperationError("Invalid bit count"))

def action_maskr(display_widget, controller_obj):
    """Mask Right (MASKR)."""
    try:
        bits = int(display_widget.raw_value or "0")
        controller_obj.mask_right(bits)
    except ValueError:
        controller_obj.handle_error(InvalidBitOperationError("Invalid bit count"))

def action_rmd(display_widget, controller_obj):
    """Double Remainder (RMD)."""
    controller_obj.double_remainder()

def action_logical_xor(display_widget, controller_obj):
    """Logical XOR."""
    controller_obj.enter_operator("xor")

def action_x_exchange_i(display_widget, controller_obj):
    """Exchange X with I register (x><(i))."""
    controller_obj.exchange_x_with_i()

def action_x_exchange_i_gto(display_widget, controller_obj):
    """Exchange X with I register (x><I)."""
    controller_obj.exchange_x_with_i()

def action_show(display_widget, controller_obj, mode):
    current_mode = controller_obj.display.mode
    display_widget.set_mode(mode)
    
    def revert_display():
        import buttons  # Import here to avoid circular import
        display_widget.set_mode(current_mode)
        controller_obj.f_mode_active = False
        for btn in controller_obj.buttons:
            if btn.get("command_name") not in ("yellow_f_function", "blue_g_function"):
                buttons.revert_to_normal(btn, controller_obj.buttons, display_widget, controller_obj)
    
    display_widget.widget.after(4000, revert_display)
    return True  # Indicate that mode toggle is handled

def action_sb(display_widget, controller_obj):
    """Set Bit (SB)."""
    try:
        bit_index = int(display_widget.raw_value or "0")
        controller_obj.set_bit(bit_index)
    except ValueError:
        controller_obj.handle_error(InvalidBitOperationError("Invalid bit index"))

def action_cb(display_widget, controller_obj):
    """Clear Bit (CB)."""
    try:
        bit_index = int(display_widget.raw_value or "0")
        controller_obj.set_bit(bit_index)
    except ValueError:
        controller_obj.handle_error(InvalidBitOperationError("Invalid bit index"))

def action_b_test(display_widget, controller_obj):
    """Test Bit (B?)."""
    try:
        bit_index = int(display_widget.raw_value or "0")
        result = controller_obj.test_bit(bit_index)
        display_widget.set_entry(str(result))
    except ValueError:
        controller_obj.handle_error(InvalidBitOperationError("Invalid bit index"))

def action_logical_and(display_widget, controller_obj):
    """Logical AND."""
    controller_obj.enter_operator("and")

def action_store_in_i(display_widget, controller_obj):
    """Store in I register ((i))."""
    controller_obj.store_in_i()

def action_recall_i(display_widget, controller_obj):
    """Recall from I register (I)."""
    controller_obj.recall_i()

def action_clr_prgm(display_widget, controller_obj):
    """Clear Program (CLR PRGM) - Not implemented."""
    pass

def action_clr_reg(display_widget, controller_obj):
    """Clear Registers (CLR REG)."""
    stack_state = stack.get_state()
    for i in range(len(stack_state)):
        stack.pop()
        stack.push(0, duplicate_x=False)
    display_widget.clear_entry()
    controller_obj.update_stack_display()

def action_clr_prfx(display_widget, controller_obj):
    """Clear Prefix (CLR PRFX) - Reset modes."""
    controller_obj.f_mode_active = False
    controller_obj.g_mode_active = False

def action_window(display_widget, controller_obj):
    """Window - Not implemented."""
    pass

def action_sc_1s(display_widget, controller_obj):
    """Set Complement Mode to 1's (SC 1'S)."""
    controller_obj.set_complement_mode("1S")

def action_sc_2s(display_widget, controller_obj):
    """Set Complement Mode to 2's (SC 2'S)."""
    controller_obj.set_complement_mode("2S")

def action_sc_unsign(display_widget, controller_obj):
    """Set Complement Mode to Unsigned (SC UNSGN)."""
    controller_obj.set_complement_mode("UNSIGNED")

def action_logical_not(display_widget, controller_obj):
    """Logical NOT."""
    controller_obj.enter_operator("not")

def action_wsize(display_widget, controller_obj):
    try:
        bits = int(display_widget.raw_value or "0")
        if bits == 0:
            bits = 64
        if controller_obj.set_word_size(bits):
            # No need to clear_entry() here; set_word_size handles display
            pass
    except ValueError:
        controller_obj.handle_error(IncorrectWordSizeError())

def action_float(display_widget, controller_obj):
    """Set Float Mode (FLOAT)."""
    controller_obj.display.mode = "FLOAT"
    current_val = float(display_widget.raw_value or "0")
    display_widget.set_entry(current_val)
    controller_obj.update_stack_display()

def action_mem(display_widget, controller_obj):
    """Memory Info (MEM) - Not implemented."""
    pass

def action_status(display_widget, controller_obj):
    """Show Stack Status (STATUS) for 5 seconds."""
    current_mode = controller_obj.display.mode
    display_widget.toggle_stack_display(current_mode)

    def hide_stack():
        display_widget.show_stack = False
        display_widget.stack_content.config(text="")

    display_widget.widget.after(5000, hide_stack)

def action_eex(display_widget, controller_obj):
    """Enter Exponent (EEx) in FLOAT mode."""
    if controller_obj.display.mode == "FLOAT":
        display_widget.raw_value += "E"
        display_widget.set_entry(display_widget.raw_value)
    else:
        controller_obj.handle_error(HP16CError("EEx only in FLOAT mode", "E108"))

def action_logical_or(display_widget, controller_obj):
    """Logical OR."""
    controller_obj.enter_operator("or")

F_FUNCTIONS = {
    "SL": action_sl, "SR": action_sr, "RL": action_rl, "RR": action_rr,
    "RLN": action_rln, "RRN": action_rrn, "MASKL": action_maskl, "MASKR": action_maskr,
    "RMD": action_rmd, "XOR": action_logical_xor, "X><(I)": action_x_exchange_i,
    "X><I": action_x_exchange_i_gto, "SHOW HEX": lambda dw, co: action_show(dw, co, "HEX"),
    "SHOW DEC": lambda dw, co: action_show(dw, co, "DEC"), "SHOW OCT": lambda dw, co: action_show(dw, co, "OCT"),
    "SHOW BIN": lambda dw, co: action_show(dw, co, "BIN"), "SB": action_sb, "CB": action_cb,
    "B?": action_b_test, "AND": action_logical_and, "(I)": action_store_in_i, "I": action_recall_i,
    "CLR PRGM": action_clr_prgm, "CLR REG": action_clr_reg, "CLR PRFX": action_clr_prfx,
    "WINDOW": action_window, "SC 1'S": action_sc_1s, "SC 2'S": action_sc_2s, "SC UNSGN": action_sc_unsign,
    "NOT": action_logical_not, "WSIZE": action_wsize, "FLOAT": action_float, "MEM": action_mem,
    "STATUS": action_status, "EEX": action_eex, "OR": action_logical_or,
}

def f_action(button, display_widget, controller_obj):
    top_text = button.get("orig_top_text", "").strip().upper()
    logger.info(f"f-mode action: {top_text}")
    if top_text in F_FUNCTIONS:
        return F_FUNCTIONS[top_text](display_widget, controller_obj)
    return False