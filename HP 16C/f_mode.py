"""
f_mode.py

Consolidated button logic for HP-16C emulator:
- f_mode_active, toggle_f_mode
"""

import sys
import os
import buttons
import stack
from base_conversion import format_in_current_base
from error import HP16CError, IncorrectWordSizeError, NoValueToShiftError, ShiftExceedsWordSizeError, InvalidBitOperationError

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PARENT_DIR)

# f-mode action functions
# ROW 1
# ROW 1
def action_sl(display_widget, controller_obj):
    try:
        controller_obj.shift_left()
        display_widget.set_entry(format_in_current_base(stack.peek(), controller_obj.display.mode))
        print("Shift Left executed")
        print(f"[DEBUG] Display value: {display_widget.current_entry}")  # Add this
    except HP16CError as e:
        controller_obj.handle_error(e)

def action_sr(display_widget, controller_obj):
    try:
        controller_obj.shift_right()
        display_widget.set_entry(format_in_current_base(stack.peek(), controller_obj.display.mode))
        print("Shift Right executed")
        print(f"[DEBUG] Display value: {display_widget.current_entry}")  # Add this
    except HP16CError as e:
        controller_obj.handle_error(e)

def action_rl(display_widget, controller_obj):
    try:
        controller_obj.rotate_left()
        display_widget.set_entry(format_in_current_base(stack.peek(), controller_obj.display.mode))
        print("Rotate Left executed")
        print(f"[DEBUG] Display value: {display_widget.current_entry}")  # Add this
    except HP16CError as e:
        controller_obj.handle_error(e)

def action_rr(display_widget, controller_obj):
    try:
        controller_obj.rotate_right()
        display_widget.set_entry(format_in_current_base(stack.peek(), controller_obj.display.mode))
        print("Rotate Right executed")
        print(f"[DEBUG] Display value: {display_widget.current_entry}")  # Add this
    except HP16CError as e:
        controller_obj.handle_error(e)

def action_rln(display_widget, controller_obj):
    try:
        controller_obj.rotate_left_carry()
        display_widget.set_entry(format_in_current_base(stack.peek(), controller_obj.display.mode))
        print("Rotate Left Carry executed")
        print(f"[DEBUG] Display value: {display_widget.current_entry}")  # Add this
    except HP16CError as e:
        controller_obj.handle_error(e)

def action_rrn(display_widget, controller_obj):
    try:
        controller_obj.rotate_right_carry()
        display_widget.set_entry(format_in_current_base(stack.peek(), controller_obj.display.mode))
        print("Rotate Right Carry executed")
        print(f"[DEBUG] Display value: {display_widget.current_entry}")  # Add this
    except HP16CError as e:
        controller_obj.handle_error(e)

def action_maskl(display_widget, controller_obj):
    try:
        bits = int(display_widget.raw_value or "0")
        controller_obj.mask_left(bits)
        display_widget.set_entry(format_in_current_base(stack.peek(), controller_obj.display.mode))
        display_widget.raw_value = str(stack.peek())
        print(f"Mask Left {bits} bits")
        print(f"[DEBUG] Display value: {display_widget.current_entry}")
    except HP16CError as e:
        controller_obj.handle_error(e)

def action_maskr(display_widget, controller_obj):
    try:
        bits = int(display_widget.raw_value or "0")
        controller_obj.mask_right(bits)
        display_widget.set_entry(format_in_current_base(stack.peek(), controller_obj.display.mode))
        display_widget.raw_value = str(stack.peek())
        print(f"Mask Right {bits} bits")
        print(f"[DEBUG] Display value: {display_widget.current_entry}")  # Add this
    except HP16CError as e:
        controller_obj.handle_error(e)

def action_rmd(display_widget, controller_obj):
    try:
        print(f"[DEBUG] Calling double_remainder on {controller_obj}")
        controller_obj.double_remainder()
        display_widget.set_entry(format_in_current_base(stack.peek(), controller_obj.display.mode))
        print("Remainder (RMD) executed")
        print(f"[DEBUG] Display value: {display_widget.current_entry}")
    except HP16CError as e:
        controller_obj.handle_error(e)

def action_logical_xor(display_widget, controller_obj, op="xor"):
    print(f"[DEBUG] Calling enter_operator with op='{op}'")
    controller_obj.enter_operator(op)
    print(f"Logical operation {op.upper()} executed")
    print(f"[DEBUG] Display value: {display_widget.current_entry}")

# ROW 2
def action_x_exchange_i(display_widget, controller_obj):
    controller_obj.exchange_x_with_i()
    print("x><(i) executed")

def action_x_exchange_i_gto(display_widget, controller_obj):
    controller_obj.exchange_x_with_i()
    print("x><I executed")

def action_show_hex(display_widget, controller_obj, mode):
    display_widget.toggle_stack_display(mode)
    print(f"Show {mode} stack")
    display_widget.widget.after(3000, lambda: display_widget.toggle_stack_display(None))  # Reset after 3s

def action_show_dec(display_widget, controller_obj, mode):
    display_widget.toggle_stack_display(mode)
    print(f"Show {mode} stack")
    display_widget.widget.after(3000, lambda: display_widget.toggle_stack_display(None))  # Reset after 3s

def action_show_oct(display_widget, controller_obj, mode):
    display_widget.toggle_stack_display(mode)
    print(f"Show {mode} stack")
    display_widget.widget.after(3000, lambda: display_widget.toggle_stack_display(None))  # Reset after 3s

def action_show_bin(display_widget, controller_obj, mode):
    display_widget.toggle_stack_display(mode)
    print(f"Show {mode} stack")
    display_widget.widget.after(3000, lambda: display_widget.toggle_stack_display(None))  # Reset after 3s

def action_sb(display_widget, controller_obj):
    bit_index = int(display_widget.raw_value or "0")
    controller_obj.set_bit(bit_index)
    display_widget.set_entry(format_in_current_base(stack.peek(), controller_obj.display.mode))
    print(f"Set Bit {bit_index}")

def action_cb(display_widget, controller_obj):
    bit_index = int(display_widget.raw_value or "0")
    controller_obj.clear_bit(bit_index)
    display_widget.set_entry(format_in_current_base(stack.peek(), controller_obj.display.mode))
    print(f"Clear Bit {bit_index}")

def action_b_test(display_widget, controller_obj):
    bit_index = int(display_widget.raw_value or "0")
    controller_obj.test_bit(bit_index)
    display_widget.set_entry(format_in_current_base(stack.peek(), controller_obj.display.mode))
    print(f"Test Bit {bit_index}, Carry={stack.get_carry_flag()}")

def action_logical_and(display_widget, controller_obj, op="and"):
    print(f"[DEBUG] Calling enter_operator with op='{op}'")
    controller_obj.enter_operator(op)
    print(f"Logical operation {op.upper()} executed")
    print(f"[DEBUG] Display value: {display_widget.current_entry}")

# ROW 3
def action_store_in_i(display_widget, controller_obj):
    controller_obj.store_in_i()
    print("(i) executed")

def action_recall_i(display_widget, controller_obj):
    controller_obj.recall_i()
    print("I (recall) executed")

def action_clr_prgm(display_widget, controller_obj):
    print("Clear Program executed (not implemented)")

def action_clr_reg(display_widget, controller_obj):
    print("Clear Registers executed (not implemented)")

def action_clr_prfx(display_widget, controller_obj):
    print("Clear Prefix executed (not implemented)")

def action_window(display_widget, controller_obj):
    print("Window executed (not implemented)")

def action_sc_1s(display_widget, controller_obj):
    controller_obj.set_complement_mode("1S")
    display_widget.update_stack_content()
    print("Set complement mode to 1's")

def action_sc_2s(display_widget, controller_obj):
    controller_obj.set_complement_mode("2S")
    display_widget.update_stack_content()
    print("Set complement mode to 2's")

def action_sc_unsign(display_widget, controller_obj):
    controller_obj.set_complement_mode("UNSIGNED")
    display_widget.update_stack_content()
    print("Set complement mode to Unsigned")

def action_logical_not(display_widget, controller_obj, op="not"):
    print(f"[DEBUG] Calling enter_operator with op='{op}'")
    controller_obj.enter_operator(op)
    print(f"Logical operation {op.upper()} executed")
    print(f"[DEBUG] Display value: {display_widget.current_entry}")

# ROW 4
def action_wsize(display_widget, controller_obj):
    try:
        bits = int(display_widget.raw_value or "0")
        controller_obj.set_word_size(bits)
        display_widget.clear_entry()
        display_widget.update_stack_content()
        print(f"Word size set to {bits} bits")
    except ValueError:
        error = IncorrectWordSizeError()
        controller_obj.handle_error(error)
        display_widget.set_entry(error.display_message, raw=True)
        print("Incorrect WSIZE error displayed")

def action_float(display_widget, controller_obj):
    controller_obj.display.mode = "FLOAT"
    controller_obj.display.set_entry(float(controller_obj.display.raw_value or 0))
    print("Float mode activated")

def action_mem(display_widget, controller_obj):
    print("Memory operation executed (not implemented)")

def action_status(display_widget, controller_obj):
    print("Status operation executed (not implemented)")

def action_eex(display_widget, controller_obj):
    if controller_obj.display.mode == "FLOAT":
        controller_obj.display.raw_value += "E"  # Append exponent indicator
        controller_obj.display.set_entry(controller_obj.display.raw_value)
        print("EEx activated for exponent entry")
    else:
        print("EEx only available in FLOAT mode")

def action_logical_or(display_widget, controller_obj, op="or"):
    print(f"[DEBUG] Calling enter_operator with op='{op}'")
    controller_obj.enter_operator(op)
    print(f"Logical operation {op.upper()} executed")
    print(f"[DEBUG] Display value: {display_widget.current_entry}")

# f_mode_active: Global flag for f-mode
F_FUNCTIONS = {
    # ROW 1
    "SL": lambda dw, cobj: action_sl(dw, cobj),
    "SR": lambda dw, cobj: action_sr(dw, cobj),
    "RL": lambda dw, cobj: action_rl(dw, cobj),
    "RR": lambda dw, cobj: action_rr(dw, cobj),
    "RLN": lambda dw, cobj: action_rln(dw, cobj),
    "RRN": lambda dw, cobj: action_rrn(dw, cobj),
    "MASKL": lambda dw, cobj: action_maskl(dw, cobj),
    "MASKR": lambda dw, cobj: action_maskr(dw, cobj),
    "RMD": lambda dw, cobj: action_rmd(dw, cobj),
    "XOR": lambda dw, cobj: action_logical_xor(dw, cobj),

    # ROW 2
    "X><(I)": lambda dw, cobj: action_x_exchange_i(dw, cobj),
    "X><I": lambda dw, cobj: action_x_exchange_i_gto(dw, cobj),
    "SHOW HEX": lambda dw, cobj: action_show_hex(dw, cobj),
    "SHOW DEC": lambda dw, cobj: action_show_dec(dw, cobj),
    "SHOW OCT": lambda dw, cobj: action_show_oct(dw, cobj),
    "SHOW BIN": lambda dw, cobj: action_show_bin(dw, cobj),
    "SB": lambda dw, cobj: action_sb(dw, cobj),
    "CB": lambda dw, cobj: action_cb(dw, cobj),
    "B?": lambda dw, cobj: action_b_test(dw, cobj),
    "AND": lambda dw, cobj: action_logical_and(dw, cobj),

    # ROW3
    "(I)": lambda dw, cobj: action_store_in_i(dw, cobj),
    "I": lambda dw, cobj: action_recall_i(dw, cobj),
    "CLR PRGM": lambda dw, cobj: action_clr_prgm(dw, cobj),
    "CLR REG": lambda dw, cobj: action_clr_reg(dw, cobj),
    "CLR PRFX": lambda dw, cobj: action_clr_prfx(dw, cobj),
    "WINDOW": lambda dw, cobj: action_window(dw, cobj),
    "SC 1'S": lambda dw, cobj: action_sc_1s(dw, cobj),
    "SC 2'S": lambda dw, cobj: action_sc_2s(dw, cobj),
    "SC UNSGN": lambda dw, cobj: action_sc_unsign(dw, cobj),
    "NOT": lambda dw, cobj: action_logical_not(dw, cobj),

    # ROW 4
    "WSIZE": lambda dw, cobj: action_wsize(dw, cobj),
    "FLOAT": lambda dw, cobj: action_float(dw, cobj),
    "MEM": lambda dw, cobj: action_mem(dw, cobj),
    "STATUS": lambda dw, cobj: action_status(dw, cobj),
    "EEX": lambda dw, cobj: action_eex(dw, cobj),
    "OR": lambda dw, cobj: action_logical_or(dw, cobj),
 }

# f_action: Handle f-mode button actions
def f_action(button, display_widget, controller_obj):
    top_text = button.get("orig_top_text", "").strip().upper()
    print(f"[DEBUG] Top label (orig_top_text): {button.get('orig_top_text', '')}")  # Add this
    print(f"[DEBUG] Top label (uppercased): {top_text}")  # Add this
    if top_text in F_FUNCTIONS:
        F_FUNCTIONS[top_text](display_widget, controller_obj)
    else:
        print(f"No f function for top label: {top_text}")