"""
buttons.py

Consolidated button logic for HP-16C emulator:
- f_mode_active, g_mode_active
- toggle_f_mode, toggle_g_mode
- normal_action_digit/operator/special
- revert_to_normal
- bind_buttons, handle_command
"""

import sys
import os
import stack
import base_conversion
from error import HP16CError  # For error handling

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PARENT_DIR)

VALID_CHARS = {
    "BIN": set("01"),
    "OCT": set("01234567"),
    "DEC": set("0123456789"),
    "HEX": set("0123456789ABCDEF")
}

##############################################################################
# Global flags
##############################################################################
f_mode_active = False
g_mode_active = False

##############################################################################
# f-mode functions
##############################################################################

def action_sl(display_widget, controller_obj):
    controller_obj.shift_left()
    display_widget.set_entry(format_in_current_base(stack.peek(), controller_obj.display.mode))
    print("Shift Left executed")

def action_sr(display_widget, controller_obj):
    controller_obj.shift_right()
    display_widget.set_entry(format_in_current_base(stack.peek(), controller_obj.display.mode))
    print("Shift Right executed")

def action_rl(display_widget, controller_obj):
    controller_obj.rotate_left()
    display_widget.set_entry(format_in_current_base(stack.peek(), controller_obj.display.mode))
    print("Rotate Left executed")

def action_rr(display_widget, controller_obj):
    controller_obj.rotate_right()
    display_widget.set_entry(format_in_current_base(stack.peek(), controller_obj.display.mode))
    print("Rotate Right executed")

def action_rlc(display_widget, controller_obj):
    controller_obj.rotate_left_carry()
    display_widget.set_entry(format_in_current_base(stack.peek(), controller_obj.display.mode))
    print("Rotate Left Carry executed")

def action_rrc(display_widget, controller_obj):
    controller_obj.rotate_right_carry()
    display_widget.set_entry(format_in_current_base(stack.peek(), controller_obj.display.mode))
    print("Rotate Right Carry executed")

def action_maskr(display_widget, controller_obj):
    bits = int(display_widget.raw_value or "0")
    controller_obj.mask_right(bits)
    display_widget.set_entry(format_in_current_base(stack.peek(), controller_obj.display.mode))
    display_widget.raw_value = str(stack.peek())
    print(f"Mask Right {bits} bits")

def action_maskl(display_widget, controller_obj):
    bits = int(display_widget.raw_value or "0")
    controller_obj.mask_left(bits)
    display_widget.set_entry(format_in_current_base(stack.peek(), controller_obj.display.mode))
    display_widget.raw_value = str(stack.peek())
    print(f"Mask Left {bits} bits")

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

def action_wsize(display_widget, controller_obj):
    bits = int(display_widget.raw_value or "0")
    controller_obj.set_word_size(bits)
    display_widget.clear_entry()
    display_widget.word_size_label.config(text=f"WS: {bits} bits")
    print(f"Word size set to {bits} bits")

def action_sc_1s(display_widget, controller_obj):
    controller_obj.set_complement_mode("1S")
    print("Set complement mode to 1's")

def action_sc_2s(display_widget, controller_obj):
    controller_obj.set_complement_mode("2S")
    print("Set complement mode to 2's")

def action_sc_unsign(display_widget, controller_obj):
    controller_obj.set_complement_mode("UNSIGNED")
    print("Set complement mode to Unsigned")

def action_dbl_multiply(display_widget, controller_obj):
    controller_obj.double_multiply()
    display_widget.set_entry(format_in_current_base(stack.peek(), controller_obj.display.mode))
    print("Double Multiply executed")

def action_dbl_divide(display_widget, controller_obj):
    controller_obj.double_divide()
    display_widget.set_entry(format_in_current_base(stack.peek(), controller_obj.display.mode))
    print("Double Divide executed")

def action_dbl_remainder(display_widget, controller_obj):
    controller_obj.double_remainder()
    display_widget.set_entry(format_in_current_base(stack.peek(), controller_obj.display.mode))
    print("Double Remainder executed")

def action_show(display_widget, controller_obj, mode):
    if mode == "BIN":
        display_widget.stack_content.config(text=f"Stack: {stack.get_state()}")
    elif mode == "OCT":
        display_widget.stack_content.config(text=f"Stack: {[oct(int(x)) for x in stack.get_state()]}")
    elif mode == "DEC":
        display_widget.stack_content.config(text=f"Stack: {stack.get_state()}")
    elif mode == "HEX":
        display_widget.stack_content.config(text=f"Stack: {[hex(int(x)) for x in stack.get_state()]}")
    print(f"Show {mode} stack")

def action_float(display_widget, controller_obj):
    controller_obj.display.mode = "FLOAT"  # Placeholder
    controller_obj.display.set_entry(float(controller_obj.display.raw_value or 0))
    print("Float mode activated")

##############################################################################
# f-mode dictionary
##############################################################################

F_FUNCTIONS = {
    "SL": lambda dw, cobj: action_sl(dw, cobj),
    "SR": lambda dw, cobj: action_sr(dw, cobj),
    "RL": lambda dw, cobj: action_rl(dw, cobj),
    "RR": lambda dw, cobj: action_rr(dw, cobj),
    "RLCn": lambda dw, cobj: action_rlc(dw, cobj),
    "RRCn": lambda dw, cobj: action_rrc(dw, cobj),
    "MASKR": lambda dw, cobj: action_maskr(dw, cobj),
    "MASKL": lambda dw, cobj: action_maskl(dw, cobj),
    "SB": lambda dw, cobj: action_sb(dw, cobj),
    "CB": lambda dw, cobj: action_cb(dw, cobj),
    "B?": lambda dw, cobj: action_b_test(dw, cobj),
    "WSIZE": lambda dw, cobj: action_wsize(dw, cobj),
    "SC 1'S": lambda dw, cobj: action_sc_1s(dw, cobj),
    "SC 2'S": lambda dw, cobj: action_sc_2s(dw, cobj),
    "SC UNSGN": lambda dw, cobj: action_sc_unsign(dw, cobj),
    "DBL*": lambda dw, cobj: action_dbl_multiply(dw, cobj),  # Changed × to *
    "DBL/": lambda dw, cobj: action_dbl_divide(dw, cobj),    # Changed ÷ to /
    "DBLR": lambda dw, cobj: action_dbl_remainder(dw, cobj),
    "FLOAT": lambda dw, cobj: action_float(dw, cobj),
}

##############################################################################
# f-mode toggling
##############################################################################

def toggle_f_mode(buttons, display, controller_obj):
    global f_mode_active
    if f_mode_active:
        for btn in buttons:
            if btn.get("command_name") in ("yellow_f_function", "blue_g_function"):
                continue
            revert_to_normal(btn, buttons, display, controller_obj)
        f_mode_active = False
        return

    f_mode_active = True
    for btn in buttons:
        if btn.get("command_name") in ("yellow_f_function", "blue_g_function"):
            continue
        revert_to_normal(btn, buttons, display, controller_obj)
        frame = btn["frame"]
        top_label = btn.get("top_label")
        main_label = btn.get("main_label")
        sub_label = btn.get("sub_label")

        if top_label:
            frame.config(bg="#e3af01")
            top_label.config(bg="#e3af01", fg="black")
            top_label.place(relx=0.5, rely=0.5, anchor="center")
            if main_label:
                main_label.place_forget()
            if sub_label:
                sub_label.place_forget()
            bind_widgets_to_f_action(btn, buttons, display, controller_obj)

def bind_widgets_to_f_action(btn, buttons, display, controller_obj):
    def on_click(e, b=btn):
        f_action(b, display, controller_obj)
        toggle_f_mode(buttons, display, controller_obj)
    for w in [btn["frame"], btn.get("top_label"), btn.get("main_label"), btn.get("sub_label")]:
        if w:
            w.bind("<Button-1>", on_click)

def f_action(button, display_widget, controller_obj):
    top_text = button.get("orig_top_text", "").strip().upper()
    if top_text in F_FUNCTIONS:
        F_FUNCTIONS[top_text](display_widget, controller_obj)
    else:
        print(f"No f function defined for top label: {top_text}")

##############################################################################
# g-mode functions
##############################################################################

def action_lj(display_widget, controller_obj):
    controller_obj.left_justify()
    display_widget.set_entry(format_in_current_base(stack.peek(), controller_obj.display.mode))
    print("Left Justify executed")

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
    controller_obj.last_x()
    print(f"Last X retrieved: {stack.peek()}")

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

##############################################################################
# g-mode dictionary
##############################################################################

G_FUNCTIONS = {
    "LJ": lambda dw, cobj: action_lj(dw, cobj),
    "1/x": lambda dw, cobj: action_reciprocal(dw, cobj),
    "LST X": lambda dw, cobj: action_last_x(dw, cobj),
    "ABS": lambda dw, cobj: action_abs(dw, cobj),
    "#B": lambda dw, cobj: action_count_bits(dw, cobj),
    "SF": lambda dw, cobj: action_set_flag(dw, cobj),
    "CF": lambda dw, cobj: action_clear_flag(dw, cobj),
    "F?": lambda dw, cobj: action_test_flag(dw, cobj),
}

##############################################################################
# g-mode toggling
##############################################################################

def toggle_g_mode(buttons, display, controller_obj):
    global g_mode_active
    if g_mode_active:
        for btn in buttons:
            if btn.get("command_name") in ("blue_g_function", "yellow_f_function"):
                continue
            revert_to_normal(btn, buttons, display, controller_obj)
        g_mode_active = False
        return

    g_mode_active = True
    for btn in buttons:
        if btn.get("command_name") in ("blue_g_function", "yellow_f_function"):
            continue
        revert_to_normal(btn, buttons, display, controller_obj)
        frame = btn["frame"]
        sub_label = btn.get("sub_label")
        main_label = btn.get("main_label")
        top_label = btn.get("top_label")

        if sub_label:
            frame.config(bg="#59b7d1")
            sub_label.config(bg="#59b7d1", fg="black")
            sub_label.place(relx=0.5, rely=0.5, anchor="center")
            if top_label:
                top_label.place_forget()
            if main_label:
                main_label.place_forget()
            bind_widgets_to_g_action(btn, buttons, display, controller_obj)

def bind_widgets_to_g_action(btn, buttons, display, controller_obj):
    def on_click(e, b=btn):
        g_action(b, display, controller_obj)
        toggle_g_mode(buttons, display, controller_obj)
    for w in [btn["frame"], btn.get("sub_label"), btn.get("main_label"), btn.get("top_label")]:
        if w:
            w.bind("<Button-1>", on_click)

def g_action(button, display_widget, controller_obj):
    sub_text = button.get("orig_sub_text", "").strip().upper()
    if sub_text in G_FUNCTIONS:
        G_FUNCTIONS[sub_text](display_widget, controller_obj)
    else:
        print(f"No g function for sub label: {sub_text}")

##############################################################################
# Normal (non-f/g) Logic
##############################################################################

def normal_action_digit(digit, display_widget):
    if display_widget.get_entry() == "0":
        display_widget.set_entry("")
        display_widget.raw_value = ""
    display_widget.append_entry(digit)

def handle_normal_command_by_label(btn, display, controller_obj):
    main_label_widget = btn.get("main_label")
    if not main_label_widget:
        return
    # Remove newlines and whitespace, then uppercase
    label_text = main_label_widget.cget("text").replace("\n", "").strip().upper()

    if label_text == "ENTER":
        controller_obj.enter_value()
    elif label_text.isdigit() or label_text in "ABCDEF":
        controller_obj.enter_digit(label_text)
    elif label_text in {"+", "-", "*", "/", "AND", "OR", "XOR", "NOT", "RMD"}:
        controller_obj.enter_operator(label_text)
    elif label_text == "BSP":
        do_backspace(display)
    elif label_text in {"BIN", "OCT", "DEC", "HEX"}:
        base_conversion.set_base(label_text, display)
        print(f"[NORMAL] Base changed to {label_text}")
    else:
        print(f"[NORMAL] Unhandled command: {label_text}")

##############################################################################
# Revert to Normal
##############################################################################

def revert_to_normal(button, buttons=None, display=None, controller_obj=None):
    frame = button.get("frame")
    if frame:
        frame.config(bg=button.get("orig_bg", "#1e1818"))

    top_label = button.get("top_label")
    if top_label:
        top_label.config(fg=button.get("orig_top_fg", "#e3af01"), bg=button.get("orig_bg", "#1e1818"))
        top_label.place(relx=0.5, rely=0, anchor="n")

    main_label = button.get("main_label")
    if main_label:
        main_label.config(fg=button.get("orig_fg", "white"), bg=button.get("orig_bg", "#1e1818"))
        main_label.place(relx=0.5, rely=0.5, anchor="center")

    sub_label = button.get("sub_label")
    if sub_label:
        sub_label.config(fg=button.get("orig_sub_fg", "#59b7d1"), bg=button.get("orig_bg", "#1e1818"))
        sub_label.place(relx=0.5, rely=1, anchor="s")

    if buttons and display and controller_obj:
        cmd = button.get("command_name")
        if cmd not in ("yellow_f_function", "blue_g_function", "reload_program"):
            bind_normal_button(button, display, controller_obj)

##############################################################################
# Binding Buttons
##############################################################################

def bind_normal_button(btn, display, controller_obj):
    def on_click(e):
        handle_normal_command_by_label(btn, display, controller_obj)
    for w in [btn["frame"], btn.get("top_label"), btn.get("main_label"), btn.get("sub_label")]:
        if w:
            w.bind("<Button-1>", on_click)

def bind_buttons(buttons, display, controller_obj):
    for btn in buttons:
        cmd_name = btn.get("command_name", "")
        bind_button_logic(btn, cmd_name, display, controller_obj)

def bind_button_logic(btn, cmd_name, display, controller_obj):
    def on_click(e):
        handle_command(cmd_name, btn, display, controller_obj)
    for w in [btn["frame"], btn.get("top_label"), btn.get("main_label"), btn.get("sub_label")]:
        if w:
            w.bind("<Button-1>", on_click)

def handle_command(cmd_name, btn, display, controller_obj):
    if cmd_name == "yellow_f_function":
        toggle_f_mode(controller_obj.buttons, display, controller_obj)
    elif cmd_name == "blue_g_function":
        toggle_g_mode(controller_obj.buttons, display, controller_obj)
    elif cmd_name == "reload_program":
        reload_program()
    else:
        handle_normal_command_by_label(btn, display, controller_obj)

def do_backspace(display_widget):
    old_val = display_widget.raw_value
    if old_val:
        new_val = old_val[:-1]
        display_widget.raw_value = new_val
        display_widget.set_entry(new_val or "0")

def reload_program():
    import subprocess
    python = sys.executable
    subprocess.Popen([python, "main.pyw"])
    sys.exit(0)