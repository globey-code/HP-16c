# buttons.py
# Consolidates button logic for the HP-16C emulator, including normal actions, f/g mode toggling, and button command binding.
# Author: GlobeyCode
# License: MIT
# Date: 3/23/2025
# Dependencies: Python 3.6+, HP-16C emulator modules (stack, base_conversion, f_mode, g_mode, error)

import stack
import base_conversion
import f_mode
import g_mode
from error import (
    HP16CError, IncorrectWordSizeError, NoValueToShiftError, 
    ShiftExceedsWordSizeError, InvalidBitOperationError, 
    StackUnderflowError, DivisionByZeroError, InvalidOperandError
)
from logging_config import logger, program_logger

VALID_CHARS = {
    "BIN": set("01"), 
    "OCT": set("01234567"), 
    "DEC": set("0123456789"), 
    "HEX": set("0123456789ABCDEF")
}

def normal_action_digit(digit, display_widget):
    """Handle digit entry for normal mode."""
    logger.info(f"Normal digit action: {digit}")
    if display_widget.get_entry() == "0":
        display_widget.set_entry("")
        display_widget.raw_value = ""
    display_widget.append_entry(digit)

def handle_normal_command_by_label(btn, display, controller_obj):
    """Execute normal mode commands based on button label."""
    main_label_widget = btn.get("main_label")
    if not main_label_widget:
        return
    
    label_text = main_label_widget.cget("text").replace("\n", "").strip().upper()
    logger.info(f"Handling normal command: {label_text}")

    if label_text == "GSB":
        controller_obj.gsb()
    elif label_text == "R↓":
        controller_obj.roll_down()
    elif label_text == "X><Y":
        controller_obj.swap_xy()
    elif label_text == "ENTER":
        controller_obj.enter_value()
    elif label_text.isdigit() or label_text in "ABCDEF":
        controller_obj.enter_digit(label_text)
    elif label_text in {"+", "-", "*", "/", "AND", "OR", "XOR", "NOT", "RMD", "."}:
        controller_obj.enter_operator(label_text)
    elif label_text == "BSP":
        handle_backspace(display, controller_obj)
    elif label_text in {"BIN", "OCT", "DEC", "HEX"}:
        controller_obj.enter_base_change(label_text)  # Route through controller
    elif label_text == "CHS":
        controller_obj.change_sign()
    elif label_text == "ON":
        controller_obj.reload_program()

def revert_to_normal(button, buttons=None, display=None, controller_obj=None):
    """Revert button to normal appearance and bindings."""
    frame = button.get("frame")
    if frame:
        orig_bg = button.get("orig_bg", "#1e1818")
        frame.config(bg=orig_bg)

    top_label = button.get("top_label")
    if top_label:
        orig_top_fg = button.get("orig_top_fg", "#e3af01")
        orig_bg = button.get("orig_bg", "#1e1818")
        top_label.config(fg=orig_top_fg, bg=orig_bg)
        top_label.place(relx=0.5, rely=0, anchor="n")

    main_label = button.get("main_label")
    if main_label:
        orig_fg = button.get("orig_fg", "white")
        orig_bg = button.get("orig_bg", "#1e1818")
        main_label.config(fg=orig_fg, bg=orig_bg)
        main_label.place(relx=0.5, rely=0.5, anchor="center")

    sub_label = button.get("sub_label")
    if sub_label:
        orig_sub_fg = button.get("orig_sub_fg", "#59b7d1")
        orig_bg = button.get("orig_bg", "#1e1818")
        sub_label.config(fg=orig_sub_fg, bg=orig_bg)
        sub_label.place(relx=0.5, rely=1, anchor="s")

    if buttons and display and controller_obj:
        cmd = button.get("command_name")
        if cmd not in ("yellow_f_function", "blue_g_function", "reload_program"):
            bind_normal_button(button, display, controller_obj)

def bind_normal_button(btn, display, controller_obj):
    """Bind normal command to button widgets."""
    def on_click(e):
        handle_normal_command_by_label(btn, display, controller_obj)
    for w in [btn["frame"], btn.get("top_label"), btn.get("main_label"), btn.get("sub_label")]:
        if w:
            w.unbind("<Button-1>")  # Clear previous bindings
            w.bind("<Button-1>", on_click)

def bind_buttons(buttons, display, controller_obj):
    """Bind actions to all buttons."""
    logger.info("Binding actions to all buttons")
    for btn in buttons:
        cmd_name = btn.get("command_name", "")
        bind_button_logic(btn, cmd_name, display, controller_obj)

def bind_button_logic(btn, cmd_name, display, controller_obj):
    """Bind specific logic to a button based on command name."""
    def on_click(e):
        handle_command(cmd_name, btn, display, controller_obj)
    for w in [btn["frame"], btn.get("top_label"), btn.get("main_label"), btn.get("sub_label")]:
        if w:
            w.bind("<Button-1>", on_click)

def handle_command(cmd_name, btn, display, controller_obj):
    """Handle button commands based on command name."""
    logger.info(f"Handling command: {cmd_name}")
    if cmd_name == "yellow_f_function":
        controller_obj.toggle_mode("f")
    elif cmd_name == "blue_g_function":
        controller_obj.toggle_mode("g")
    elif cmd_name == "reload_program":
        reload_program()
    else:
        handle_normal_command_by_label(btn, display, controller_obj)

def handle_backspace(display_widget, controller_obj):
    """Handle BSP: Backspace in normal mode, back step in program mode."""
    if controller_obj.program_mode:
        # In program mode, perform back step (BST-like behavior)
        if controller_obj.program_memory:
            removed_instruction = controller_obj.program_memory.pop()
            step = len(controller_obj.program_memory)
            program_logger.info(f"BSP: Removed step {step + 1:03d} - {removed_instruction}")
            logger.info(f"BSP executed: Removed '{removed_instruction}', new length={len(controller_obj.program_memory)}")
            
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
            logger.info("BSP: Program memory is already empty")
            display_widget.set_entry((0, ""), program_mode=True)
    else:
        # In normal mode, perform standard backspace on display entry
        logger.info("BSP: Performing backspace on display")
        old_val = display_widget.raw_value
        if old_val:
            new_val = old_val[:-1]
            display_widget.raw_value = new_val
            display_widget.set_entry(new_val or "0")
            # Update X register if user is entering a value
            if controller_obj.is_user_entry:
                val = base_conversion.interpret_in_base(new_val or "0", display_widget.mode)
                stack._x_register = val
                controller_obj.update_stack_display()
        else:
            logger.info("BSP: Display is already empty")

def reload_program():
    """Reload the emulator program."""
    logger.info("Reloading program")
    import subprocess, sys
    python_exe = sys.executable
    subprocess.Popen([python_exe, "main.pyw"])
    sys.exit(0)