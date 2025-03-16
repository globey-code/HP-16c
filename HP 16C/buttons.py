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
import f_mode
import g_mode
from error import HP16CError  # For error handling

VALID_CHARS = {
    "BIN": set("01"),
    "OCT": set("01234567"),
    "DEC": set("0123456789"),
    "HEX": set("0123456789ABCDEF")
}

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
        controller_obj.toggle_mode("f")
    elif cmd_name == "blue_g_function":
        controller_obj.toggle_mode("g")
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