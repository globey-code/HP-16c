"""
buttons.py

Consolidated button logic:
- f_mode_active, g_mode_active
- toggle_f_mode, toggle_g_mode
- normal_action_digit/operator/special
- revert_to_normal
- bind_buttons, handle_command
"""

import sys
import os

# If base_conversion.py, controller.py, etc. are in the parent folder:
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PARENT_DIR)

import stack
import controller
import base_conversion
from error import InvalidOperandError
from word_size import set_word_size_from_input

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
    val = controller_obj.pop_value()
    if val is None:
        return

    # Convert 'val' to a string in the current base:
    old_str = base_conversion.format_in_current_base(val)

    # SHIFT LEFT
    shifted = stack.apply_word_size(val << 1)
    stack.push(shifted)

    # Convert 'shifted' to a string in the current base:
    new_str = base_conversion.format_in_current_base(shifted)
    display_widget.set_entry(new_str)
    display_widget.raw_value = new_str
    controller_obj.update_stack_display()

    print(f"Shift Left: {val} -> {shifted}")

def action_wsize(display_widget):
    """
    Sets the word size from the current display.raw_value.
    Typically, the user types a decimal integer (like "16") in DEC mode,
    presses f, then presses WSIZE.
    """
    typed_str = display_widget.raw_value  # e.g. "16"
    if not typed_str:
        print("No input for word size.")
        return

    try:
        # For HP-16C, word size is usually typed in decimal. So we do int(...)
        new_size = int(typed_str)
        stack.set_word_size(new_size)
        # Clear the display
        display_widget.clear_entry()
        display_widget.raw_value = ""
        # Optionally show something like "WS: 16 bits"
        display_widget.word_size_label.config(text=f"WS: {new_size} bits")
        print(f"Word size set to {new_size} bits")
    except ValueError:
        print(f"Invalid input '{typed_str}' for word size.")
    except Exception as e:
        print(f"Error setting word size: {e}")

def action_sc_1s(display_widget):
    stack.set_complement_mode("1S")
    # optionally clear display or show "1'S" somewhere

def action_sc_2s(display_widget):
    stack.set_complement_mode("2S")

def action_sc_unsign(display_widget):
    stack.set_complement_mode("UNSIGNED")


##############################################################################
# f-mode dictionary
##############################################################################

F_FUNCTIONS = {
    "SL": lambda dw, cobj: action_sl(dw, cobj),
    "WSIZE": lambda dw, cobj: action_wsize(dw),
    "SC 1'S": lambda dw, cobj: action_sc_1s(dw),
    "SC 2'S": lambda dw, cobj: action_sc_2s(dw),
    "SC UNSGN": lambda dw, cobj: action_sc_unsign(dw),
    # Add more: "SR": action_sr, "MASKR": action_maskr, etc.
}

##############################################################################
# f-mode toggling
##############################################################################

def toggle_f_mode(buttons, display, controller_obj):
    global f_mode_active
    if f_mode_active:
        # Cancel f-mode
        for btn in buttons:
            if btn.get("command_name") in ("yellow_f_function", "blue_g_function"):
                continue
            revert_to_normal(btn, buttons, display, controller_obj)
        f_mode_active = False
        return

    # Activate f-mode
    f_mode_active = True
    for btn in buttons:
        if btn.get("command_name") in ("yellow_f_function", "blue_g_function"):
            continue
        # Revert to normal first
        revert_to_normal(btn, buttons, display, controller_obj)

        frame = btn["frame"]
        top_label = btn.get("top_label")
        main_label = btn.get("main_label")
        sub_label = btn.get("sub_label")

        if top_label:
            # Highlight
            frame.config(bg="#e3af01")
            top_label.config(bg="#e3af01", fg="black")
            # Center top_label
            top_label.place(relx=0.5, rely=0.5, anchor="center")
            # Hide main_label/sub_label
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
    top_label_widget = button.get("top_label")
    top_text = top_label_widget.cget("text").replace("\n","").strip().upper() if top_label_widget else ""

    if top_text in F_FUNCTIONS:
        # Pass display_widget to the function
        F_FUNCTIONS[top_text](display_widget, controller_obj)
    else:
        print(f"No f function defined for top label: {top_text}")


##############################################################################
# g-mode
##############################################################################

def toggle_g_mode(buttons, display, controller_obj):
    global g_mode_active
    if g_mode_active:
        # Cancel g-mode
        for btn in buttons:
            if btn.get("command_name") in ("blue_g_function", "yellow_f_function"):
                continue
            revert_to_normal(btn, buttons, display, controller_obj)
        g_mode_active = False
        return

    # Activate g-mode
    g_mode_active = True
    for btn in buttons:
        if btn.get("command_name") in ("blue_g_function", "yellow_f_function"):
            continue
        revert_to_normal(btn, buttons, display, controller_obj)

        frame = btn["frame"]
        top_label = btn.get("top_label")
        main_label = btn.get("main_label")
        sub_label = btn.get("sub_label")

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
        g_action(b, display)
        toggle_g_mode(buttons, display, controller_obj)

    for w in [btn["frame"], btn.get("sub_label"), btn.get("main_label"), btn.get("top_label")]:
        if w:
            w.bind("<Button-1>", on_click)

def g_action(button, display_widget):
    sub_text = button.get("orig_sub_text", "").strip()
    if sub_text == "LJ":
        action_lj(display_widget)
    else:
        print("No g function for sub label:", sub_text)

def action_lj(display_widget):
    val = stack.pop()
    stack.push(val)
    display_widget.set_entry(str(val))
    controller.update_stack_display(display_widget)
    print("Left justify executed:", val)

##############################################################################
# Normal (non-f/g) Logic
##############################################################################

def normal_action_digit(digit, display_widget):
    if display_widget.get_entry() == "0":
        display_widget.set_entry("")
        display_widget.raw_value = ""
    display_widget.append_entry(digit)

def normal_action_operator(operator, display_widget):
    controller.perform_operator(operator, display_widget)

def normal_action_special(label, buttons, display_widget):
    if label.upper() == "ENTER":
        val_str = display_widget.raw_value

        try:
            # interpret_in_current_base uses the current_base from base_conversion.py
            numeric_val = base_conversion.interpret_in_current_base(val_str)
        except ValueError:
            numeric_val = 0

        # Push numeric_val onto the stack
        stack.push(numeric_val)

        # Clear the display
        display_widget.clear_entry()
        display_widget.update_stack_content()
        print(f"Pushed {numeric_val} (from '{val_str}') in {base_conversion.current_base} mode")

    elif label.upper() in {"BIN", "OCT", "DEC", "HEX"}:
        # Switch base
        print(f"Set base to {label.upper()}")
        base_conversion.set_base(label.upper(), display_widget)

##############################################################################
# Revert to Normal
##############################################################################

def revert_to_normal(button, buttons=None, display=None, controller_obj=None):
    frame = button.get("frame")
    if frame:
        frame.config(bg=button.get("orig_bg", "#1e1818"))

    top_label = button.get("top_label")
    if top_label:
        top_label.config(
            fg=button.get("orig_top_fg", "#e3af01"),
            bg=button.get("orig_bg", "#1e1818"),
            text=button.get("orig_top_text", top_label.cget("text"))
        )
        top_label.place(relx=0.5, rely=0, anchor="n")

    main_label = button.get("main_label")
    if main_label:
        main_label.config(
            fg=button.get("orig_fg", "white"),
            bg=button.get("orig_bg", "#1e1818"),
            text=button.get("orig_main_text", main_label.cget("text"))
        )
        main_label.place(relx=0.5, rely=0.5, anchor="center")

    sub_label = button.get("sub_label")
    if sub_label:
        sub_label.config(
            fg=button.get("orig_sub_fg", "#59b7d1"),
            bg=button.get("orig_bg", "#1e1818"),
            text=button.get("orig_sub_text", sub_label.cget("text"))
        )
        sub_label.place(relx=0.5, rely=1, anchor="s")

    # Rebind normal if we have everything
    if buttons is not None and display is not None and controller_obj is not None:
        cmd = button.get("command_name")
        if cmd not in ("yellow_f_function", "blue_g_function", "reload_program"):
            bind_normal_button(button, display, controller_obj)

##############################################################################
# Binding Buttons
##############################################################################

def bind_normal_button(btn, display, controller_obj):
    """
    Rebind the button to normal label-based logic.
    """
    def on_click(e):
        handle_normal_command_by_label(btn, display, controller_obj)
    for w in [btn["frame"], btn.get("top_label"), btn.get("main_label"), btn.get("sub_label")]:
        if w:
            w.bind("<Button-1>", on_click)

def handle_normal_command_by_label(btn, display, controller_obj):
    main_label_widget = btn.get("main_label")
    if not main_label_widget:
        return
    label_text = main_label_widget.cget("text").strip()

    # Remove newlines
    label_text = label_text.replace("\n", "")
    label_text = label_text.strip().upper()

    if label_text == "ENTER":
        # call your ENTER logic
        normal_action_special("ENTER", None, display)

    # 1) If label_text is a digit or A-F
    if label_text.isdigit() or label_text.upper() in {"A","B","C","D","E","F"}:
        allowed = VALID_CHARS.get(base_conversion.current_base, VALID_CHARS["DEC"])
        if label_text.upper() not in allowed:
            print(f"[ERROR] '{label_text}' not allowed in {base_conversion.current_base} mode.")
            return

        if display.get_entry() == "0":
            display.set_entry("")
            display.raw_value = ""

        display.raw_value += label_text.upper()
        display.set_entry(display.raw_value)
        print(f"[NORMAL] Typed '{label_text}' in {base_conversion.current_base} mode -> {display.raw_value}")

    elif label_text in {"+", "-", "*", "/"}:
        controller_obj.enter_operator(label_text)

    elif label_text.upper() == "BSP":
        print("Backspace pressed")
        do_backspace(display)

    elif label_text.upper() in {"BIN", "OCT", "DEC", "HEX"}:
        base_conversion.set_base(label_text.upper(), display)
        print(f"[NORMAL] Base changed to {label_text.upper()}")



    else:
        print(f"[NORMAL] Button '{label_text}' clicked - do normal logic here")

def append_char_and_remove_zero(char, display_widget):
    if display_widget.get_entry() == "0":
        display_widget.set_entry("")
        display_widget.raw_value = ""
    display_widget.append_entry(char)

def bind_buttons(buttons, display, controller_obj):
    """
    Main entry point to bind all buttons.
    """
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
    """
    If cmd_name is 'yellow_f_function', 'blue_g_function', or 'reload_program', do those.
    Otherwise, do label-based normal logic.
    """
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
        display_widget.set_entry(new_val)

def reload_program():
    import sys
    import subprocess
    python = sys.executable
    subprocess.Popen([python, "main.pyw"])
    sys.exit(0)
