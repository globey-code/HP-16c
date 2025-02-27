import base_conversion
import stack
import error
import reload
from base_conversion import format_in_current_base
from stack import peek

def get_command_map(disp, memory_ref, button_widgets=None, f_labels=None):
    """
    Build and return a command map dictionary that maps command names to functions.
    disp: an instance of your Display class.
    memory_ref: a mutable object for the memory register.
    button_widgets: list of button widget dictionaries (from main.pyw).
    f_labels: list of f-label dictionaries (returned by create_labels).
    """

    # Track the toggle states for blue (g) and yellow (f).
    blue_toggled = False
    yellow_toggled = False

    # ----------------------------------------------------
    # Helper functions to revert or activate BLUE (g) mode
    # ----------------------------------------------------
    def revert_blue():
        """Revert compound buttons from blue mode to original appearance."""
        nonlocal blue_toggled
        if not blue_toggled or button_widgets is None:
            return
        for btn in button_widgets:
            if btn["type"] == "compound":
                btn["frame"].config(bg=btn["orig_bg"])
                btn["main_label"].config(bg=btn["orig_bg"],
                                         fg=btn["orig_fg"],
                                         text=btn["orig_main_text"])
                btn["sub_label"].config(bg=btn["orig_bg"],
                                         fg=btn["orig_sub_fg"],
                                         text=btn["orig_sub_text"])
        blue_toggled = False
        print("Blue mode deactivated.")

    def activate_blue():
        """Turn compound buttons to blue mode (subtext on main label, etc.)."""
        nonlocal blue_toggled
        if button_widgets is None:
            print("No button widgets registered.")
            return
        for btn in button_widgets:
            if btn["type"] == "compound":
                blue_color = "#59b7d1"
                btn["frame"].config(bg=blue_color)
                # Replace main text with subtext, hide subtext
                btn["main_label"].config(bg=blue_color, fg="black", text=btn["orig_sub_text"])
                btn["sub_label"].config(bg=blue_color, fg="black", text="")
        blue_toggled = True
        print("Blue mode activated: Compound buttons updated.")

    # ------------------------------------------------------
    # Helper functions to revert or activate YELLOW (f) mode
    # ------------------------------------------------------
    def revert_yellow():
        """Revert f-labels that are associated with a button to original appearance."""
        nonlocal yellow_toggled
        if not yellow_toggled or f_labels is None:
            return
        for label in f_labels:
            if label.get("associated_button") is not None:
                label["widget"].config(bg=label["orig_bg"],
                                       fg=label["orig_fg"],
                                       text=label["orig_text"])
        yellow_toggled = False
        print("Yellow f mode deactivated: f_labels reverted.")

    def activate_yellow():
        """Turn on f-labels (those associated with a button) to yellow with black text."""
        nonlocal yellow_toggled
        if f_labels is None:
            print("No f_labels registered.")
            return
        for label in f_labels:
            if label.get("associated_button") is not None:
                label["widget"].config(bg="yellow", fg="black")
        yellow_toggled = True
        print("Yellow f mode activated: f_labels updated.")

    # ------------------------------------------------------
    # Toggle commands for the blue g button and the yellow f button
    # ------------------------------------------------------
    def blue_g_function():
        nonlocal blue_toggled, yellow_toggled
        if blue_toggled:
            # If blue is already on, turn it off
            revert_blue()
        else:
            # If yellow is on, revert it first
            if yellow_toggled:
                revert_yellow()
            # Then activate blue
            activate_blue()

    def yellow_f_function():
        nonlocal blue_toggled, yellow_toggled
        if yellow_toggled:
            # If yellow is already on, turn it off
            revert_yellow()
        else:
            # If blue is on, revert it first
            if blue_toggled:
                revert_blue()
            # Then activate yellow
            activate_yellow()

    # ------------------------------------------------------
    # Standard functions remain unchanged, except for perform_operator
    # ------------------------------------------------------
    def reload_program():
        reload.reload_program()

    def add_input(ch):
        disp.append_entry(ch)

    def change_sign():
        if disp.current_entry:
            try:
                num = base_conversion.interpret_in_current_base(disp.current_entry)
                num = -num
                disp.set_entry(base_conversion.format_in_current_base(num))
            except ValueError as ve:
                disp.show_error("INVALID SIGN CHANGE", str(ve))

    def push_entry_to_stack():
        if disp.current_entry:
            try:
                value = base_conversion.interpret_in_current_base(disp.current_entry)
                stack.push(value)
            except ValueError as ve:
                disp.show_error("INVALID ENTRY", str(ve))
            disp.clear_entry()

    def press_equals():
        # RPN logic: just push the current entry to the stack
        push_entry_to_stack()

    def perform_operator(op):
        # 1. Push whatever is in the entry
        push_entry_to_stack()
        try:
            # 2. Perform the operation
            result = stack.perform_operation(op)
            # 3. Show the top of the stack in the display
            top_value = peek()  # top of the RPN stack
            disp.set_entry(format_in_current_base(top_value))
        except Exception as ex:
            disp.show_error("OPERATION ERROR", str(ex))
        disp.update()

    def set_operator_add():
        perform_operator("+")
    def set_operator_sub():
        perform_operator("-")
    def set_operator_mul():
        perform_operator("*")
    def set_operator_div():
        perform_operator("/")

    def set_base(new_base):
        if disp.current_entry:
            try:
                num = base_conversion.interpret_in_current_base(disp.current_entry)
                disp.set_entry(base_conversion.format_in_current_base(num, new_base))
            except ValueError as ve:
                disp.show_error("BASE CONVERSION ERROR", str(ve))
                disp.clear_entry()
        base_conversion.current_base = new_base
        disp.update()

    def set_base_bin():
        set_base("BIN")
    def set_base_oct():
        set_base("OCT")
    def set_base_dec():
        set_base("DEC")
    def set_base_hex():
        set_base("HEX")

    def mem_recall():
        disp.set_entry(base_conversion.format_in_current_base(memory_ref["value"]))
    def mem_clear():
        memory_ref["value"] = 0.0
        disp.update()

    def add_input_0(): add_input("0")
    def add_input_1(): add_input("1")
    def add_input_2(): add_input("2")
    def add_input_3(): add_input("3")
    def add_input_4(): add_input("4")
    def add_input_5(): add_input("5")
    def add_input_6(): add_input("6")
    def add_input_7(): add_input("7")
    def add_input_8(): add_input("8")
    def add_input_9(): add_input("9")
    def add_input_dot(): add_input(".")

    def add_input_a(): add_input("A")
    def add_input_b(): add_input("B")
    def add_input_c(): add_input("C")
    def add_input_d(): add_input("D")
    def add_input_e(): add_input("E")
    def add_input_f(): add_input("F")
    def add_input_g(): add_input("G")
    def add_input_h(): add_input("H")
    def add_input_i(): add_input("I")
    def add_input_j(): add_input("J")
    def add_input_k(): add_input("K")
    def add_input_l(): add_input("L")
    def add_input_m(): add_input("M")
    def add_input_n(): add_input("N")
    def add_input_o(): add_input("O")
    def add_input_p(): add_input("P")

    # ------------------------------------------------------
    # Build the command map
    # ------------------------------------------------------
    command_map = {
        "add_input_0": add_input_0,
        "add_input_1": add_input_1,
        "add_input_2": add_input_2,
        "add_input_3": add_input_3,
        "add_input_4": add_input_4,
        "add_input_5": add_input_5,
        "add_input_6": add_input_6,
        "add_input_7": add_input_7,
        "add_input_8": add_input_8,
        "add_input_9": add_input_9,
        "add_input_dot": add_input_dot,
        "add_input_a": add_input_a,
        "add_input_b": add_input_b,
        "add_input_c": add_input_c,
        "add_input_d": add_input_d,
        "add_input_e": add_input_e,
        "add_input_f": add_input_f,
        "add_input_g": add_input_g,
        "add_input_h": add_input_h,
        "add_input_i": add_input_i,
        "add_input_j": add_input_j,
        "add_input_k": add_input_k,
        "add_input_l": add_input_l,
        "add_input_m": add_input_m,
        "add_input_n": add_input_n,
        "add_input_o": add_input_o,
        "add_input_p": add_input_p,
        "change_sign": change_sign,
        "set_operator_add": set_operator_add,
        "set_operator_sub": set_operator_sub,
        "set_operator_mul": set_operator_mul,
        "set_operator_div": set_operator_div,
        "press_equals": press_equals,
        "set_base_bin": set_base_bin,
        "set_base_oct": set_base_oct,
        "set_base_dec": set_base_dec,
        "set_base_hex": set_base_hex,
        "mem_recall": mem_recall,
        "mem_clear": mem_clear,
        "reload_program": reload_program,
        "blue_g_function": blue_g_function,
        "yellow_f_function": yellow_f_function,
    }

    # Wrap commands so each button press prints a debug message.
    def wrap_command_map(cmd_map):
        wrapped_map = {}
        for key, func in cmd_map.items():
            def wrapped_func(*args, _func=func, _key=key, **kwargs):
                print("Button pressed:", _key)
                return _func(*args, **kwargs)
            wrapped_map[key] = wrapped_func
        return wrapped_map

    return wrap_command_map(command_map)
