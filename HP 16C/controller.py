"""
controller.py
Coordinates stack operations and display updates for the HP-16C emulator,
implementing RPN behavior.
Refactored to use dependency injection and integrate base conversion into Stack and Display.
Author: GlobeyCode (original), refactored by ChatGPT
License: MIT
Date: 3/23/2025 (original), refactored 2025-04-01, fixed 2025-04-05
Dependencies: Python 3.6+, refactored modules: stack, buttons, f_mode, g_mode, error, logging_config
"""

from typing import Any, List, Optional, Tuple, Union
from buttons import VALID_CHARS, revert_to_normal
from f_mode import f_action
from g_mode import g_action
from error import HP16CError
from logging_config import logger, program_logger
from stack import Stack

print("Loading controller.py from this file")

class HP16CController:
    """
    Controller for the HP-16C emulator.

    Coordinates user input, stack operations, and display updates.

    Attributes:
        display: The Display object for UI updates.
        buttons: List of button configuration dictionaries.
        stack_display: Widget for displaying the stack.
        stack: Instance of the Stack class for RPN operations.
        is_user_entry: True if a user entry is in progress.
        result_displayed: True if the result is currently displayed.
        stack_lift_enabled: Flag for stack lift behavior.
        post_enter: Flag for post-enter operations.
        f_mode_active: True if f-mode is active.
        g_mode_active: True if g-mode is active.
        program_mode: True if in program mode.
        entry_mode: Current entry mode (e.g., "sto", "rcl", "set_decimal_places", "gsb_label").
        program_memory: List of instructions for programming mode.
        last_program_step: Last step number in program memory.
        current_line: Current line pointer for running programs.
        labels: Dictionary mapping label names to line numbers.
        return_stack: Stack of return addresses for subroutine calls.
        decimal_entered: True if a decimal point has been entered.
        pre_entry_x: Store X before user entry begins.
    """
    def __init__(self, stack: Stack, display: Any, buttons: List[dict], stack_display: Any) -> None:
        logger.info("Initializing HP16CController")
        print("set_word_size in HP16CController:", hasattr(self, 'set_word_size'))
        self.stack = stack
        self.stack.set_word_size(8)  # Set default word size to 8 bits
        logger.info("Default word size set to 8 bits")
        self.display = display
        self.buttons = buttons
        self.stack_display = stack_display
        self.is_user_entry: bool = False
        self.result_displayed: bool = True
        self.stack_lift_enabled: bool = True
        self.post_enter: bool = False
        self.f_mode_active: bool = False
        self.g_mode_active: bool = False
        self.program_mode: bool = False
        self.entry_mode: Optional[str] = None
        self.program_memory: List[Union[str, Tuple[int, str]]] = []
        self.last_program_step: int = 0
        self.current_line: int = 0
        self.labels: dict = {}
        self.return_stack: List[int] = []
        self.decimal_entered: bool = False
        self.pre_entry_x: int = 0  # Store X before user entry

    def initialize(self) -> None:
        """Initialize the controller by setting the stack mode to DEC and updating the display."""
        self.display.set_mode("DEC")
        if self.display:
            self.display.set_entry("0")
        logger.info("Stack mode initialized to DEC")

    def get_max_digits(self, mode: str) -> int:
        """Calculate the maximum number of digits allowed based on mode and word size."""
        word_size = self.stack.word_size
        if mode == "BIN":
            return word_size
        elif mode == "HEX":
            return (word_size + 3) // 4
        elif mode == "OCT":
            return (word_size + 2) // 3
        elif mode == "DEC":
            if self.stack.complement_mode in ["1S", "2S"]:
                max_value = 2 ** (word_size - 1) - 1
            else:
                max_value = 2 ** word_size - 1
            return len(str(max_value))
        elif mode == "FLOAT":
            return float('inf')
        else:
            raise ValueError(f"Invalid mode: {mode}")

    def enter_digit(self, digit: str) -> None:
        """Process a digit or decimal point entry, handling flags and limits."""
        logger.info(f"Entering digit: {digit}")
        # Handle flag modes (SF, CF, F?)
        if self.entry_mode == "set_flag":
            try:
                flag_num = int(digit)
                if 0 <= flag_num <= 5:
                    self.stack.set_flag(flag_num)
                    self.entry_mode = None
                    self.is_user_entry = False
                    top_val = self.stack.peek()
                    self.display.set_entry(self.stack.format_in_base(top_val, self.display.mode), blink=True)
                    self.update_stack_display()
                    logger.info(f"Set flag {flag_num} to 1")
                else:
                    self.handle_error(HP16CError("Invalid flag number (0-5)", "E01"))
            except ValueError:
                self.handle_error(HP16CError("Invalid input for flag", "E02"))
            return

        if self.entry_mode == "clear_flag":
            try:
                flag_num = int(digit)
                if 0 <= flag_num <= 5:
                    self.stack.clear_flag(flag_num)
                    self.entry_mode = None
                    self.is_user_entry = False
                    top_val = self.stack.peek()
                    self.display.set_entry(self.stack.format_in_base(top_val, self.display.mode), blink=True)
                    self.update_stack_display()
                    logger.info(f"Cleared flag {flag_num} to 0")
                else:
                    self.handle_error(HP16CError("Invalid flag number (0-5)", "E01"))
            except ValueError:
                self.handle_error(HP16CError("Invalid input for flag", "E02"))
            return

        if self.entry_mode == "test_flag":
            try:
                flag_num = int(digit)
                if 0 <= flag_num <= 5:
                    result = self.stack.test_flag(flag_num)
                    self.entry_mode = None
                    self.is_user_entry = False
                    original_x = self.stack.peek()
                    original_str = self.stack.format_in_base(original_x, self.display.mode, pad=False)
                    self.display.set_entry("1" if result else "0", raw=False, blink=True)
                    logger.info(f"Tested flag {flag_num}: {'1' if result else '0'}")
                    self.display.master.after(1000, lambda: self.display.set_entry(original_str, raw=False, blink=False))
                    self.stack_lift_enabled = False
                    self.update_stack_display()
                else:
                    self.handle_error(HP16CError("Invalid flag number (0-5)", "E01"))
            except ValueError:
                self.handle_error(HP16CError("Invalid input for flag", "E02"))
            return

        if self.entry_mode == "set_decimal_places":
            if digit in "0123456789":
                decimal_places = int(digit)
                self.display.decimal_places = None if decimal_places == 0 else decimal_places
                self.display.set_mode("FLOAT")
                self.entry_mode = None
                current_value = self.stack.peek()
                formatted_value = self.stack.format_in_base(current_value, "FLOAT")
                self.display.set_entry(formatted_value, blink=True)
                logger.info(f"Set decimal places to {decimal_places if decimal_places else 'floating'}")
            return

        if self.entry_mode == "sto":
            try:
                reg_num = int(digit)
                if 0 <= reg_num <= 9:
                    self.stack._data_registers[reg_num] = self.stack.peek() & ((1 << self.stack.word_size) - 1)
                    self.entry_mode = None
                    self.is_user_entry = False
                    self.display.set_entry(self.stack.format_in_base(self.stack.peek(), self.display.mode), blink=True)
                    logger.info(f"Stored X={self.stack.peek()} into R{reg_num}")
                else:
                    self.handle_error(HP16CError("Invalid register number", "E01"))
            except ValueError:
                self.handle_error(HP16CError("Invalid input for register", "E02"))
            return

        if self.entry_mode == "rcl":
            try:
                reg_num = int(digit)
                if 0 <= reg_num <= 9:
                    value = self.stack._data_registers[reg_num]
                    self.stack.push(value)
                    self.display.set_entry(self.stack.format_in_base(value, self.display.mode), blink=True)
                    self.entry_mode = None
                    self.is_user_entry = False
                    self.stack_lift_enabled = False
                    self.update_stack_display()
                    logger.info(f"Recalled R{reg_num}={value} into X")
                else:
                    self.handle_error(HP16CError("Invalid register number", "E01"))
            except ValueError:
                self.handle_error(HP16CError("Invalid input for register", "E02"))
            return

        if digit.upper() not in VALID_CHARS[self.display.mode]:
            logger.info(f"Ignoring invalid digit {digit} for base {self.display.mode}")
            return

        if not self.is_user_entry:
            self.pre_entry_x = self.stack.peek()
            self.display.clear_entry()
            self.display.raw_value = ""
            self.is_user_entry = True
            self.decimal_entered = False
            self.result_displayed = False

        max_digits = self.get_max_digits(self.display.mode)
        display_value = self.display.raw_value or ""
        current_length = len(display_value)
        if self.display.mode == "DEC" and display_value.startswith("-"):
            current_length -= 1

        if current_length >= max_digits:
            logger.info(f"Input blocked: Max {max_digits} digits reached for mode {self.display.mode}")
            return

        if self.display.mode == "HEX":
            digit_upper = digit.upper()
            display_digit = digit_upper.lower() if digit_upper in ['B', 'D'] else digit_upper
        else:
            display_digit = digit

        current = self.display.raw_value or ""
        new_value = current + display_digit
        self.display.raw_value = new_value

        if self.display.mode == "FLOAT":
            if digit == ".":
                if self.decimal_entered:
                    logger.info("Ignoring additional decimal point")
                    return
                self.decimal_entered = True
            formatted_value = self.format_float_with_commas(new_value)
            self.display.set_entry(formatted_value, raw=True)
        else:
            val = self.stack.interpret_in_base(new_value, self.display.mode)
            self.stack._x_register = val
            formatted_value = self.stack.format_in_base(val, self.display.mode, pad=False)
            # Pad DEC mode to 3 digits for HP-16C compatibility (8-bit word size)
            if self.display.mode == "DEC" and self.stack.word_size == 8:
                try:
                    num = int(formatted_value)
                    if -999 <= num <= 999:
                        formatted_value = f"{num:04d}" if num < 0 else f"{num:03d}"
                except ValueError:
                    pass  # If conversion fails, use original formatted_value
            self.display.set_entry(formatted_value, raw=False)
            self.update_stack_display()

    def enter_operator(self, operator: str) -> None:
        """Process an operator command (+, -, *, /)."""
        logger.info(f"Entering operator: {operator}, X={self.stack.peek()}, stack={self.stack._stack}")
        if self.program_mode:
            logger.info("Operation skipped due to program mode")
            return
        try:
            self.finalize_entry()
            if self.display.is_error_displayed:
                logger.info("Operation skipped due to error state")
                return
            if operator == "+":
                self.stack.add()
            elif operator == "-":
                self.stack.subtract()
            elif operator == "*":
                self.stack.multiply()
            elif operator == "/":
                self.stack.divide()
            else:
                raise ValueError(f"Unknown operator: {operator}")
            self.display.set_entry(self.stack.format_in_base(self.stack.peek(), self.display.mode), blink=True)
            self.update_stack_display()
            self.stack_lift_enabled = True
        except ValueError as e:
            self.display.set_error(str(e))
            logger.info(f"Value error: {e}")
        except HP16CError as e:
            self.handle_error(e)
        except Exception as e:
            self.display.set_error(f"Error: {e}")
            logger.info(f"Unexpected error: {e}")
        self.post_enter = False

    def enter_value(self) -> None:
        """Finalize entry and push to stack, or record ENTER in program mode."""
        logger.info("Entering value (lifting stack)")
        if self.program_mode:
            instruction = "ENTER"
            display_code = "36"
            self.program_memory.append(instruction)
            step = len(self.program_memory)
            program_logger.info(f"{step:03d} - {instruction} ({display_code})")
            self.display.set_entry((step, display_code), program_mode=True)
            self.last_program_step = step
            return
        if self.is_user_entry:
            entry = self.display.raw_value
            val = self.stack.interpret_in_base(entry, self.display.mode)
            self.stack._x_register = val
            formatted_value = self.stack.format_in_base(val, self.display.mode)
            self.display.set_entry(formatted_value, blink=True)
            self.is_user_entry = False
            self.decimal_entered = False
        self.stack.push(self.stack._x_register)
        self.stack_lift_enabled = False
        self.result_displayed = True
        self.update_stack_display()

    def enter_base_change(self, base: str) -> None:
        """Handle base change (HEX, DEC, OCT, BIN)."""
        logger.info(f"Entering base change: {base}")
        if self.program_mode:
            base_map = {"HEX": "23", "DEC": "24", "OCT": "25", "BIN": "26"}
            instruction = base
            display_code = base_map.get(base, base)
            self.program_memory.append(instruction)
            step = len(self.program_memory)
            program_logger.info(f"{step:03d} - {instruction} ({display_code})")
            self.display.set_entry((step, display_code), program_mode=True)
            self.last_program_step = step
        else:
            self.display.set_base(base)
            self.is_user_entry = False
            self.update_stack_display()
            logger.info(f"Base set to {base}, display updated via set_base")

    def format_float_with_commas(self, raw_value: str) -> str:
        """Format a raw float string with commas for the integer part."""
        if not raw_value:
            return "0"
        sign = "-" if raw_value.startswith("-") else ""
        number = raw_value[1:] if raw_value.startswith("-") else raw_value
        if "." in number:
            integer_part, fractional_part = number.split(".")
            integer_formatted = "{:,}".format(int(integer_part)) if integer_part else "0"
            return f"{sign}{integer_formatted}.{fractional_part}"
        return f"{sign}{'{:,}'.format(int(number))}"

    def delete_digit(self) -> None:
        """Remove the last entered digit."""
        if self.is_user_entry and self.display.raw_value:
            self.display.raw_value = self.display.raw_value[:-1]
            if not self.display.raw_value:
                self.is_user_entry = False
                self.display.set_entry("0", raw=True)
            else:
                if self.display.mode == "FLOAT":
                    formatted_value = self.format_float_with_commas(self.display.raw_value)
                else:
                    formatted_value = self.display.raw_value
                self.display.set_entry(formatted_value, raw=True)
                self.decimal_entered = "." in self.display.raw_value
        logger.info("Delete digit executed")

    def finalize_entry(self) -> None:
        """Convert pending display value to number and update X."""
        if self.is_user_entry:
            entry = self.display.raw_value
            val = self.stack.interpret_in_base(entry, self.display.mode)
            self.stack._x_register = val
            self.is_user_entry = False
            self.display.clear_entry()

    def update_display(self) -> None:
        """Update display based on current state."""
        if self.is_user_entry:
            self.display.set_entry(self.display.raw_value, raw=True)
        else:
            self.display.set_entry(self.stack.format_in_base(self.stack.peek(), self.display.mode))

    def update_stack_display(self) -> None:
        """Update stack display (Y, Z, T)."""
        logger.debug("Updating stack display")
        if self.stack_display:
            formatted_stack = [self.stack.format_in_base(x, self.display.mode) for x in self.stack._stack[:3]]
            while len(formatted_stack) < 3:
                formatted_stack.insert(0, "0")
            y, z, t = formatted_stack[-3:]
            self.stack_display.config(text=f"Y: {y} Z: {z} T: {t}")
        self.display.update_stack_content()

    def toggle_stack_display(self) -> None:
        """Toggle stack display visibility."""
        if self.stack_display.winfo_ismapped():
            self.stack_display.place_forget()
            logger.info("Stack display hidden")
        else:
            self.stack_display.place(x=125, y=110, width=575, height=40)
            self.update_stack_display()
            logger.info("Stack display shown")

    def handle_error(self, error: Exception) -> None:
        """Display error message."""
        self.previous_value = self.display.current_entry
        error_message = str(error)
        self.display.set_entry(error_message, raw=True, is_error=True)
        self.display.widget.after(5000, self.restore_normal_display)

    def restore_normal_display(self) -> None:
        """Restore display after error."""
        self.display.set_entry(self.previous_value, raw=False)

    def pop_value(self) -> int:
        """Pop top-of-stack value."""
        logger.info("Popping value")
        try:
            val = self.stack.pop()
            # Note: save_last_x is not a method in Stack; assuming it's meant to be _last_x
            self.stack._last_x = val
            top_val = self.stack.peek()
            self.display.set_entry(self.stack.format_in_base(top_val, self.display.mode))
            self.display.raw_value = str(top_val)
            self.update_stack_display()
            return val
        except HP16CError as e:
            self.handle_error(e)
            return 0

    def push_value(self, value: int) -> None:
        """Push value onto stack."""
        logger.info(f"Pushing value: {value}")
        self.stack.push(value)
        self.update_stack_display()

    def count_bits(self) -> None:
        """Count 1 bits in X (not implemented in Stack)."""
        logger.info("Counting bits")
        try:
            # Placeholder: Stack class needs count_bits method
            raise NotImplementedError("count_bits not implemented in Stack")
        except HP16CError as e:
            self.handle_error(e)

    def absolute(self) -> None:
        """Set X to its absolute value (not implemented in Stack)."""
        logger.info("Computing absolute value")
        try:
            # Placeholder: Stack class needs absolute method
            raise NotImplementedError("absolute not implemented in Stack")
        except HP16CError as e:
            self.handle_error(e)

    def build_labels(self) -> None:
        """Map program labels to line numbers."""
        self.labels = {}
        for i, cmd in enumerate(self.program_memory):
            if isinstance(cmd, str) and cmd.startswith("LBL "):
                self.labels[cmd.split()[1]] = i

    def toggle_mode(self, mode: str) -> None:
        """Toggle f-mode or g-mode."""
        logger.info(f"Toggling mode: {mode}, f_active={self.f_mode_active}, g_active={self.g_mode_active}")
        if (mode == "f" and self.f_mode_active) or (mode == "g" and self.g_mode_active):
            self.f_mode_active = False
            self.g_mode_active = False
            self.display.hide_f_mode()
            self.display.hide_g_mode()
            for btn in self.buttons:
                if btn.get("command_name") not in ("yellow_f_function", "blue_g_function", "reload_program"):
                    revert_to_normal(btn, self.buttons, self.display, self)
            logger.info("Mode reset to normal")
            return
        for btn in self.buttons:
            if btn.get("command_name") not in ("yellow_f_function", "blue_g_function", "reload_program"):
                revert_to_normal(btn, self.buttons, self.display, self)
                for w in [btn["frame"], btn.get("top_label"), btn.get("main_label"), btn.get("sub_label")]:
                    if w:
                        w.unbind("<Button-1>")
        if mode == "f":
            self.f_mode_active = True
            self.g_mode_active = False
            self.display.show_f_mode()
            self.display.hide_g_mode()
            color = "#e3af01"
            label_key = "top_label"
        elif mode == "g":
            self.f_mode_active = False
            self.g_mode_active = True
            self.display.hide_f_mode()
            self.display.show_g_mode()
            color = "#59b7d1"
            label_key = "sub_label"
        else:
            logger.warning(f"Invalid mode: {mode}")
            return
        for btn in self.buttons:
            if btn.get("command_name") in ("yellow_f_function", "blue_g_function", "reload_program"):
                continue
            frame = btn["frame"]
            label = btn.get(label_key)
            if label:
                frame.config(bg=color)
                label.config(bg=color, fg="black")
                label.place(relx=0.5, rely=0.5, anchor="center")
                if btn.get("main_label"):
                    btn["main_label"].place_forget()
                if mode == "f" and btn.get("sub_label"):
                    btn["sub_label"].place_forget()
                if mode == "g" and btn.get("top_label"):
                    btn["top_label"].place_forget()
                self._bind_mode_action(btn, mode)
        logger.info(f"Mode set: {mode}")

    def _bind_mode_action(self, btn: dict, mode: str) -> None:
        """Bind mode-specific action to button."""
        def on_click(e: Any, b: dict = btn) -> None:
            if mode == "f":
                f_action(b, self.display, self)
            elif mode == "g":
                g_action(b, self.display, self)
        for w in [btn["frame"], btn.get("top_label"), btn.get("main_label"), btn.get("sub_label")]:
            if w:
                w.unbind("<Button-1>")
                w.bind("<Button-1>", on_click)

    # NORMAL MODE ROW 2
    def gsb(self, label: Optional[str] = None) -> None:
        """Process GSB command."""
        logger.info(f"GSB called with label: {label}")
        if self.program_mode:
            if label is None:
                self.entry_mode = "gsb_label"
            else:
                instruction = f"GSB {label}"
                self.program_memory.append(instruction)
                step = len(self.program_memory)
                program_logger.info(f"{step:03d} - {instruction} ({label})")
                self.display.set_entry((step, label), program_mode=True)
                self.entry_mode = None
        else:
            if label is None:
                self.entry_mode = "gsb_label"
            else:
                try:
                    if label not in self.labels:
                        raise HP16CError("No such label", "E04")
                    self.current_line = self.labels[label]
                    while self.current_line < len(self.program_memory):
                        instr = self.program_memory[self.current_line]
                        if instr == "RTN":
                            break
                        if not isinstance(instr, str) or not instr.startswith("LBL "):
                            logger.info(f"Executing: {instr}")
                        self.current_line += 1
                except HP16CError as e:
                    self.handle_error(e)

    # NORMAL MODE ROW 3
    def roll_down(self) -> None:
        """Roll stack down."""
        logger.info(f"Before R↓: X={self.stack._x_register}, stack={self.stack._stack}")
        old_x = self.stack._x_register
        self.stack._x_register = self.stack._stack[0]
        self.stack._stack[0] = self.stack._stack[1]
        self.stack._stack[1] = self.stack._stack[2]
        self.stack._stack[2] = old_x
        logger.info(f"After R↓: X={self.stack._x_register}, stack={self.stack._stack}")
        self.display.set_entry(self.stack.format_in_base(self.stack._x_register, self.display.mode, pad=False))
        self.update_stack_display()

    def swap_xy(self) -> None:
        """Swap X and Y registers."""
        if self.is_user_entry:
            val = self.stack.interpret_in_base(self.display.raw_value, self.display.mode)
            self.stack._x_register = val
            self.is_user_entry = False
        temp = self.stack._x_register
        self.stack._x_register = self.stack._stack[0]
        self.stack._stack[0] = temp
        self.display.set_entry(self.stack.format_in_base(self.stack._x_register, self.display.mode, pad=False))
        self.update_stack_display()

    # NORMAL MODE ROW 4
    def change_sign(self) -> None:
        """Change the sign of the X register based on the complement mode."""
        logger.info("Changing sign of X register")
        try:
            if self.display.mode == "FLOAT":
                self.stack._x_register = -self.stack._x_register
            else:
                mode = self.stack.get_complement_mode()
                word_size = self.stack.get_word_size()
                mask = (1 << word_size) - 1
                if mode == "UNSIGNED":
                    self.stack._x_register = (mask - self.stack._x_register) & mask
                elif mode == "1S":
                    self.stack._x_register = (~self.stack._x_register) & mask  # 1's complement: invert bits
                else:  # 2S
                    self.stack._x_register = (-self.stack._x_register) & mask  # 2's complement: arithmetic negation
            top_val = self.stack.peek()
            self.display.set_entry(self.stack.format_in_base(top_val, self.display.mode, pad=False))
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    # F MODE ROW 1
    def shift_left(self) -> None:
        """Shift X left by one bit."""
        logger.info("Shifting left")
        self.stack.shift_left()
        top_val = self.stack.peek()
        self.display.set_entry(self.stack.format_in_base(top_val, self.display.mode, pad=False))
        self.update_stack_display()

    def shift_right(self) -> None:
        """Shift X right by one bit."""
        logger.info("Shifting right")
        try:
            self.stack.shift_right()
            top_val = self.stack.peek()
            self.display.set_entry(self.stack.format_in_base(top_val, self.display.mode, pad=False))
            self.display.raw_value = str(top_val)
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    def rotate_left(self) -> None:
        """Rotate X left by one bit."""
        logger.info("Rotating left")
        self.stack.rotate_left()
        top_val = self.stack.peek()
        self.display.set_entry(self.stack.format_in_base(top_val, self.display.mode, pad=False))
        self.update_stack_display()

    def rotate_right(self) -> None:
        """Rotate X right by one bit."""
        logger.info("Rotating right")
        self.stack.rotate_right()
        top_val = self.stack.peek()
        self.display.set_entry(self.stack.format_in_base(top_val, self.display.mode, pad=False))
        self.update_stack_display()

    def rotate_left_carry(self) -> None:
        """Rotate X left with carry."""
        logger.info("Rotating left with carry")
        try:
            if self.is_user_entry:
                self.finalize_entry()
            self.stack.rotate_left_carry()
            top_val = self.stack.peek()
            logger.info(f"After rotation, top_val = {top_val}")
            self.display.set_entry(top_val, raw=False, blink=True)
            self.display.raw_value = str(top_val)
            self.is_user_entry = False
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    def rotate_right_carry(self) -> None:
        """Rotate X right with carry."""
        logger.info("Rotating right with carry")
        try:
            self.stack.rotate_right_carry()
            top_val = self.stack.peek()
            self.display.set_entry(self.stack.format_in_base(top_val, self.display.mode, pad=False))
            self.display.raw_value = str(top_val)
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    def mask_left(self, bits: int) -> None:
        """Mask leftmost bits of Y into X."""
        logger.info(f"Masking left: {bits} bits")
        try:
            if len(self.stack._stack) < 1:
                raise StackUnderflowError("Need Y value for MASKL")
            self.stack.mask_left(bits)
            top_val = self.stack.peek()
            self.display.set_entry(self.stack.format_in_base(top_val, self.display.mode, pad=False))
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    def mask_right(self, bits: int) -> None:
        """Mask rightmost bits of Y into X."""
        logger.info(f"Masking right: {bits} bits")
        try:
            if len(self.stack._stack) < 1:
                raise StackUnderflowError("Need Y value for MASKR")
            self.stack.mask_right(bits)
            top_val = self.stack.peek()
            self.display.set_entry(self.stack.format_in_base(top_val, self.display.mode, pad=False))
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    def double_remainder(self) -> None:
        """Retrieve remainder (should be remainder, not double_remainder)."""
        logger.info("Retrieving remainder")
        try:
            self.stack.remainder()
            top_val = self.stack.peek()
            self.display.set_entry(self.stack.format_in_base(top_val, self.display.mode, pad=False))
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    # F MODE ROW 2
    def exchange_x_with_i(self) -> None:
        """Exchange X with I register."""
        logger.info("Exchanging X with I register")
        try:
            top_val = self.stack.pop()
            i_val = self.stack._i_register  # Direct access since get_i not defined
            self.stack.push(i_val)
            self.stack._i_register = top_val  # Direct set since store_in_i not fully implemented
            self.display.set_entry(self.stack.format_in_base(self.stack.peek(), self.display.mode, pad=False))
            self.display.raw_value = str(self.stack.peek())
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    def set_bit(self, bit_index: int) -> None:
        """Set a bit in X (not implemented in Stack)."""
        logger.info(f"Setting bit: {bit_index}")
        try:
            raise NotImplementedError("set_bit not implemented in Stack")
        except HP16CError as e:
            self.handle_error(e)

    def clear_bit(self, bit_index: int) -> None:
        """Clear a bit in X (not implemented in Stack)."""
        logger.info(f"Clearing bit: {bit_index}")
        try:
            raise NotImplementedError("clear_bit not implemented in Stack")
        except HP16CError as e:
            self.handle_error(e)

    def test_bit(self, bit_index: int) -> int:
        """Test a bit in X (not implemented in Stack)."""
        logger.info(f"Testing bit: {bit_index}")
        try:
            raise NotImplementedError("test_bit not implemented in Stack")
        except HP16CError as e:
            self.handle_error(e)
            return 0

    # F MODE ROW 3
    def store_in_i(self) -> None:
        """Store X in I register."""
        logger.info("Storing in I register")
        try:
            self.stack._i_register = self.stack.peek()  # Simplified implementation
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    def recall_i(self) -> None:
        """Recall I register into X."""
        logger.info("Recalling I register")
        try:
            self.stack.push(self.stack._i_register)
            top_val = self.stack.peek()
            self.display.set_entry(self.stack.format_in_base(top_val, self.display.mode, pad=False))
            self.display.raw_value = str(top_val)
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    def set_complement_mode(self, mode: str) -> None:
        logger.info(f"Setting complement mode: {mode}")
        try:
            self.stack.set_complement_mode(mode)
            self.update_stack_display()
            top_val = self.stack.peek()
            self.display.set_entry(self.stack.format_in_base(top_val, self.display.mode, pad=False))
            self.display.raw_value = str(top_val)
        except (HP16CError, ValueError) as e:
            self.handle_error(HP16CError(str(e), "E01"))

    # F MODE ROW 4
    def set_word_size(self, bits: int) -> None:
        """Set word size and update display (fixed: confirmed present and functional)."""
        logger.info(f"Setting word size to {bits}")
        try:
            self.stack.set_word_size(bits)  # Calls Stack.set_word_size, which is defined
            top_val = self.stack.peek()
            self.display.set_entry(self.stack.format_in_base(top_val, self.display.mode, pad=False))
            self.update_stack_display()
            self.is_user_entry = False
        except HP16CError as e:
            self.handle_error(e)

    # G MODE ROW 1
    def left_justify(self) -> None:
        """Left justify X (not implemented in Stack, fix dependency)."""
        if self.is_user_entry:
            entry = self.display.raw_value
            # Fix: interpret_in_base should be self.stack.interpret_in_base
            val = self.stack.interpret_in_base(entry, self.display.mode)
            self.stack._x_register = val
            self.is_user_entry = False
        try:
            raise NotImplementedError("left_justify not implemented in Stack")
        except Exception as e:
            self.handle_error(e)

    def double_multiply(self) -> None:
        """Double multiply (not implemented in Stack)."""
        logger.info("Double multiplying")
        try:
            raise NotImplementedError("double_multiply not implemented in Stack")
        except HP16CError as e:
            self.handle_error(e)

    def double_divide(self) -> None:
        """Double divide (not implemented in Stack)."""
        logger.info("Double dividing")
        try:
            raise NotImplementedError("double_divide not implemented in Stack")
        except HP16CError as e:
            self.handle_error(e)

    # G MODE ROW 2
    def set_flag(self, flag_num: int) -> None:
        """Set a flag."""
        logger.info(f"Setting flag: {flag_num}")
        try:
            self.stack.set_flag(flag_num)
            self.update_stack_display()
            self.display.update_stack_content()
            current_val = self.stack.peek()
            formatted_value = self.stack.format_in_base(current_val, self.display.mode, pad=False)
            self.display.set_entry(formatted_value)
            self.display.raw_value = formatted_value
            self.is_user_entry = False
            self.stack_lift_enabled = True
        except HP16CError as e:
            self.handle_error(e)
        except ValueError:
            self.handle_error(HP16CError(f"Invalid flag number: {flag_num}", "E01"))

    def clear_flag(self, flag_num: int) -> None:
        """Clear a flag."""
        logger.info(f"Clearing flag: {flag_num}")
        try:
            self.stack.clear_flag(flag_num)
            self.update_stack_display()
            self.display.update_stack_content()
            current_val = self.stack.peek()
            formatted_value = self.stack.format_in_base(current_val, self.display.mode, pad=False)
            self.display.set_entry(formatted_value)
            self.display.raw_value = formatted_value
        except HP16CError as e:
            self.handle_error(e)
        except ValueError:
            self.handle_error(HP16CError(f"Invalid flag number: {flag_num}", "E01"))

    def test_flag(self, flag_type: Union[str, int]) -> Union[int, bool]:
        """Test a flag."""
        logger.info(f"Testing flag: {flag_type}")
        try:
            if flag_type == "CF":
                # Fix: get_carry_flag not defined, use test_flag(4) for carry
                result = self.stack.test_flag(4)
            else:
                result = self.stack.test_flag(int(flag_type))
            self.display.set_entry("1" if result else "0")
            self.update_stack_display()
            return result
        except (ValueError, HP16CError):
            self.handle_error(HP16CError(f"Invalid flag type: {flag_type}", "E01"))
            return False

    # G MODE ROW 3
    def run_program(self) -> None:
        """Execute program."""
        if self.program_mode:
            return
        self.build_labels()
        self.current_line = 0
        self.return_stack = []
        while self.current_line < len(self.program_memory):
            cmd = self.program_memory[self.current_line]
            if isinstance(cmd, tuple):
                pass
            elif isinstance(cmd, str):
                if cmd.startswith("enter_digit"):
                    self.enter_digit(cmd.split()[1])
                elif cmd.startswith("enter_operator"):
                    self.enter_operator(cmd.split()[1])
                elif cmd.startswith("enter_value"):
                    self.enter_value()
                elif cmd.startswith("LBL "):
                    pass
                elif cmd.startswith("goto"):
                    label = cmd.split()[1]
                    if label in self.labels:
                        self.current_line = self.labels[label]
                        continue
                    else:
                        self.display.set_error("Label not found")
                        break
            self.current_line += 1

    def clear_x(self) -> None:
        """Clear X register."""
        self.stack._x_register = 0
        self.display.set_entry("0")
        self.display.raw_value = "0"
        self.is_user_entry = False
        self.stack_lift_enabled = True
        self.update_stack_display()
        logger.info("Cleared X register")

    # G MODE ROW 4 (incomplete in original, left as placeholder)