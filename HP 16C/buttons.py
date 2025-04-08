"""
buttons.py
Handles button bindings and normal-mode actions for the HP-16C emulator, including digit entry and operator processing.
Author: GlobeyCode
License: MIT
Created: 3/23/2025
Last Modified: 4/06/2025
Dependencies: Python 3.6+, stack, logging_config
"""

from typing import Any, Dict, List, Callable
import stack
from logging_config import logger, program_logger

# Define valid characters for different bases.
VALID_CHARS: Dict[str, set] = {
    "BIN": set("01"),
    "OCT": set("01234567"),
    "DEC": set("0123456789"),
    "HEX": set("0123456789ABCDEF"),
    "FLOAT": set("0123456789.")
}


def normal_action_digit(digit: str, display_widget: Any) -> None:
    """
    Handle digit entry for normal mode.
    
    If the current display entry is "0", clears it before appending.
    """
    logger.info(f"Normal digit action: {digit}")
    if display_widget.get_entry() == "0":
        display_widget.set_entry("")
        display_widget.raw_value = ""
    display_widget.append_entry(digit)


def handle_normal_command_by_label(btn: Dict[str, Any], display: Any, controller_obj: Any) -> None:
    """
    Handle normal command based on the main label of the button.
    
    Depending on the text of the main label, delegates actions to the controller.
    """
    main_label_widget = btn.get("main_label")
    if not main_label_widget:
        return

    label_text: str = main_label_widget.cget("text").replace("\n", "").strip().upper()
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
    elif label_text in {"+", "-", "×", "÷", "AND", "OR", "XOR", "NOT", "RMD"}:
        controller_obj.enter_operator(label_text)
    elif label_text == ".":
        if display.mode == "FLOAT":
            controller_obj.enter_digit(label_text)  # In FLOAT mode, treat '.' as a digit.
        else:
            controller_obj.enter_operator(label_text)
    elif label_text == "BSP":
        handle_backspace(display, controller_obj)
    elif label_text in {"BIN", "OCT", "DEC", "HEX"}:
        controller_obj.enter_base_change(label_text)
    elif label_text == "CHS":
        controller_obj.change_sign()
    elif label_text == "STO":
        controller_obj.entry_mode = "sto"
        logger.info("Entered STO mode, waiting for register number")
    elif label_text == "RCL":
        controller_obj.entry_mode = "rcl"
        logger.info("Entered RCL mode, waiting for register number")
    elif label_text == "ON":
        controller_obj.reload_program()


def revert_to_normal(button: Dict[str, Any], buttons: List[Dict[str, Any]] = None,
                     display: Any = None, controller_obj: Any = None) -> None:
    """
    Revert a button to its normal appearance and bindings.
    
    Resets background and label colors using stored original values.
    If additional parameters are provided, rebinds the normal button action.
    """
    frame = button.get("frame")
    if frame:
        orig_bg: str = button.get("orig_bg", "#1e1818")
        frame.config(bg=orig_bg)

    top_label = button.get("top_label")
    if top_label:
        orig_top_fg: str = button.get("orig_top_fg", "#e3af01")
        orig_bg = button.get("orig_bg", "#1e1818")
        top_label.config(fg=orig_top_fg, bg=orig_bg)
        top_label.place(relx=0.5, rely=0, anchor="n")

    main_label = button.get("main_label")
    if main_label:
        orig_fg: str = button.get("orig_fg", "white")
        orig_bg = button.get("orig_bg", "#1e1818")
        main_label.config(fg=orig_fg, bg=orig_bg)
        main_label.place(relx=0.5, rely=0.5, anchor="center")

    sub_label = button.get("sub_label")
    if sub_label:
        orig_sub_fg: str = button.get("orig_sub_fg", "#59b7d1")
        orig_bg = button.get("orig_bg", "#1e1818")
        sub_label.config(fg=orig_sub_fg, bg=orig_bg)
        sub_label.place(relx=0.5, rely=1, anchor="s")

    if buttons is not None and display is not None and controller_obj is not None:
        cmd = button.get("command_name")
        if cmd not in ("yellow_f_function", "blue_g_function", "reload_program"):
            bind_normal_button(button, display, controller_obj)


def bind_normal_button(btn: Dict[str, Any], display: Any, controller_obj: Any) -> None:
    """
    Bind a normal command action to the button's widgets.
    
    Uses the handle_normal_command_by_label function.
    """
    def on_click(e: Any) -> None:
        handle_normal_command_by_label(btn, display, controller_obj)
    for w in [btn.get("frame"), btn.get("top_label"), btn.get("main_label"), btn.get("sub_label")]:
        if w:
            w.unbind("<Button-1>")
            w.bind("<Button-1>", on_click)


def bind_buttons(buttons: List[Dict[str, Any]], display: Any, controller_obj: Any) -> None:
    """
    Bind actions to all buttons.
    
    Iterates over a list of button configuration dictionaries and binds their respective commands.
    """
    logger.info("Binding actions to all buttons")
    for btn in buttons:
        cmd_name: str = btn.get("command_name", "")
        bind_button_logic(btn, cmd_name, display, controller_obj)


def bind_button_logic(btn: Dict[str, Any], cmd_name: str, display: Any, controller_obj: Any) -> None:
    """
    Bind specific logic to a button based on its command name.
    """
    def on_click(e: Any) -> None:
        handle_command(cmd_name, btn, display, controller_obj)
    for w in [btn.get("frame"), btn.get("top_label"), btn.get("main_label"), btn.get("sub_label")]:
        if w:
            w.bind("<Button-1>", on_click)


def handle_command(cmd_name: str, btn: Dict[str, Any], display: Any, controller_obj: Any) -> None:
    logger.info(f"Handling command: {cmd_name}")
    if cmd_name == "yellow_f_function":
        controller_obj.toggle_mode("f")
    elif cmd_name == "blue_g_function":
        controller_obj.toggle_mode("g")
    elif cmd_name == "reload_program":
        reload_program()
    else:
        handle_normal_command_by_label(btn, display, controller_obj)


def handle_backspace(display_widget: Any, controller_obj: Any) -> None:
    if controller_obj.program_mode:
        # Program mode logic unchanged
        if controller_obj.program_memory:
            removed_instruction = controller_obj.program_memory.pop()
            step = len(controller_obj.program_memory)
            program_logger.info(f"BSP: Removed step {step + 1:03d} - {removed_instruction}")
            logger.info(f"BSP executed: Removed '{removed_instruction}', new length={len(controller_obj.program_memory)}")
            if controller_obj.program_memory:
                last_instruction = controller_obj.program_memory[-1]
                op_map = {"÷": "10", "×": "20", "-": "30", "+": "40", ".": "48", "ENTER": "36"}
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
        if controller_obj.is_user_entry:
            logger.info("BSP: Deleting last digit during user entry")
            controller_obj.delete_digit()
        else:
            logger.info("BSP: Clearing X register (not in user entry mode)")
            controller_obj.clear_x()


def reload_program() -> None:
    """
    Reload the emulator program by spawning a new process and exiting the current one.
    """
    logger.info("Reloading program")
    import subprocess, sys
    python_exe = sys.executable
    subprocess.Popen([python_exe, "main.pyw"])
    sys.exit(0)
