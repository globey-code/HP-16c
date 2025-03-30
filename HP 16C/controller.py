# controller.py
# Coordinates stack operations and display updates for the HP-16C emulator, implementing RPN behavior.
# Author: GlobeyCode
# License: MIT
# Date: 3/23/2025
# Dependencies: Python 3.6+, HP-16C emulator modules (stack, buttons, error, base_conversion, arithmetic)

import stack
import buttons
import base_conversion
import program
from buttons import VALID_CHARS
from buttons import revert_to_normal
from f_mode import f_action
from g_mode import g_action
from error import (
    HP16CError, IncorrectWordSizeError, NoValueToShiftError, 
    ShiftExceedsWordSizeError, InvalidBitOperationError, 
    StackUnderflowError, DivisionByZeroError, InvalidOperandError
)
from base_conversion import format_in_current_base, interpret_in_base
from logging_config import logger, program_logger
from arithmetic import add, subtract, multiply, divide

class HP16CController:
    def __init__(self, display, buttons, stack_display):
        logger.info("Initializing HP16CController")
        self.display = display
        self.buttons = buttons
        self.stack_display = stack_display
        self.is_user_entry = False
        self.result_displayed = True
        self.stack_lift_enabled = True
        self.post_enter = False
        self.f_mode_active = False
        self.g_mode_active = False
        self.program_mode = False        # True when in program mode
        self.entry_mode = None           # For multi-key sequences (e.g., "sto", "rcl")
        self.program_memory = []         # Stores program steps as tuples
        self.last_program_step = 0       # Track last step for re-entry
        self.current_line = 0            # Program counter for execution
        self.labels = {}                 # Maps label names to line numbers
        self.return_stack = []           # Stack for subroutine returns

    def build_labels(self):
        self.labels = {}
        for i, cmd in enumerate(self.program_memory):
            if cmd[0] == "label":
                self.labels[cmd[1]] = i

    def run_program(self):
        if self.program_mode:
            return  # Don’t run while in program mode
        self.build_labels()
        self.current_line = 0
        self.return_stack = []
        while self.current_line < len(self.program_memory):
            cmd = self.program_memory[self.current_line]
            if cmd[0] == "enter_digit":
                self.enter_digit(cmd[1])
            elif cmd[0] == "enter_operator":
                self.enter_operator(cmd[1])
            elif cmd[0] == "enter_value":
                self.enter_value()
            elif cmd[0] == "label":
                pass  # Labels are skipped during execution
            elif cmd[0] == "goto":
                label = cmd[1]
                if label in self.labels:
                    self.current_line = self.labels[label]
                    continue
                else:
                    self.display.set_error("Label not found")
                    break
            self.current_line += 1

    def enter_base_change(self, base):
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
            base_conversion.set_base(base, self.display)
            self.update_stack_display()
            self.display.update_stack_content()

    def enter_digit(self, digit):
        logger.info(f"Entering digit: {digit}")

        # Handle STO mode
        if self.entry_mode == "sto":
            try:
                reg_num = int(digit)
                if 0 <= reg_num <= 9:
                    # Store the current X value in the register
                    stack.set_register(reg_num, stack.peek())
                    # Reset entry mode and user entry state
                    self.entry_mode = None
                    self.is_user_entry = False  # Ensure next digit starts a new entry
                    # Update display with current value and blink
                    self.display.set_entry(format_in_current_base(stack.peek(), self.display.mode), blink=True)
                    logger.info(f"Stored X={stack.peek()} into R{reg_num}")
                else:
                    self.handle_error(HP16CError("Invalid register number", "E01"))
            except ValueError:
                self.handle_error(HP16CError("Invalid input for register", "E02"))
            return

        # Handle RCL mode
        elif self.entry_mode == "rcl":
            try:
                reg_num = int(digit)
                if 0 <= reg_num <= 9:
                    # Recall the value from the register and push to stack
                    value = stack.get_register(reg_num)
                    stack.push(value)
                    # Update display with recalled value and blink
                    self.display.set_entry(format_in_current_base(value, self.display.mode), blink=True)
                    # Reset entry mode and states
                    self.entry_mode = None
                    self.is_user_entry = False
                    self.stack_lift_enabled = False  # RCL disables stack lift
                    self.update_stack_display()
                    logger.info(f"Recalled R{reg_num}={value} into X")
                else:
                    self.handle_error(HP16CError("Invalid register number", "E01"))
            except ValueError:
                self.handle_error(HP16CError("Invalid input for register", "E02"))
            return

        # Handle flag operations if in set_flag or clear_flag mode
        if self.entry_mode in {"set_flag", "clear_flag"}:
            try:
                flag_num = int(digit)
                if 0 <= flag_num <= 5:
                    if self.entry_mode == "set_flag":
                        self.set_flag(flag_num)
                    elif self.entry_mode == "clear_flag":
                        self.clear_flag(flag_num)
                else:
                    self.handle_error(HP16CError("Invalid flag number", "E01"))
            except ValueError:
                self.handle_error(HP16CError("Invalid input for flag", "E02"))
            self.entry_mode = None
            return

        # Program mode handling
        valid_program_chars = set("0123456789ABCDEFabcdef")
        log_digit = digit.lower() if digit.upper() in {"B", "D"} else digit.upper()

        if self.entry_mode == "label":
            if digit not in valid_program_chars:
                logger.info(f"Ignoring invalid digit {digit} for label in program mode")
                return
            instruction = f"LBL {digit}"
            self.program_memory.append(instruction)
            step = len(self.program_memory)
            program_logger.info(f"{step:03d} - {instruction} ({digit.upper()})")
            self.entry_mode = None
            self.display.set_entry((step, log_digit), program_mode=True)
            return

        if self.entry_mode == "test_flag":
            try:
                flag_num = int(digit)
                if flag_num in range(6):
                    result = stack.test_flag(flag_num)
                    self.display.set_entry("1" if result else "0")
                elif digit.upper() == "C":
                    result = stack.get_carry_flag()
                    self.display.set_entry("1" if result else "0")
                else:
                    self.handle_error(HP16CError("Invalid flag number", "E01"))
            except ValueError:
                self.handle_error(HP16CError("Invalid input for flag", "E02"))
            self.entry_mode = None
            return

        if self.program_mode:
            if digit not in valid_program_chars:
                logger.info(f"Ignoring invalid digit {digit} in program mode")
                return
            self.program_memory.append(digit)
            step = len(self.program_memory)
            program_logger.info(f"{step:03d} - {log_digit} ({digit.upper()})")
            self.display.set_entry((step, log_digit), program_mode=True)
            self.last_program_step = step
            return

        if digit.upper() not in VALID_CHARS[self.display.mode]:
            logger.info(f"Ignoring invalid digit {digit} for base {self.display.mode}")
            return

        # If this is the start of a new entry after an operation
        if not self.is_user_entry or self.stack_lift_enabled:
            if self.stack_lift_enabled:
                stack.stack_lift()
                self.stack_lift_enabled = False
            self.display.clear_entry()
            self.result_displayed = False

        # Append the new digit
        test_input = self.display.raw_value + digit
        try:
            if self.display.mode == "HEX":
                value = int(test_input, 16)
            elif self.display.mode == "OCT":
                value = int(test_input, 8)
            elif self.display.mode == "BIN":
                value = int(test_input, 2)
            else:  # DEC
                value = int(test_input, 10)
            max_value = (1 << stack.get_word_size()) - 1
            if value > max_value:
                logger.info(f"Ignoring digit {digit}: value {value} exceeds max {max_value}")
                return
        except ValueError:
            logger.info(f"Invalid input {test_input} for base {self.display.mode}")
            return

        self.display.append_entry(digit)
        val = interpret_in_base(self.display.raw_value, self.display.mode)
        stack._x_register = val
        self.is_user_entry = True
        self.update_stack_display()

    def toggle_mode(self, mode):
        logger.info(f"Toggling mode: {mode}, f_active={self.f_mode_active}, g_active={self.g_mode_active}")
    
        # Reset mode if already active
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

        # Reset to normal and unbind previous events
        for btn in self.buttons:
            if btn.get("command_name") not in ("yellow_f_function", "blue_g_function", "reload_program"):
                revert_to_normal(btn, self.buttons, self.display, self)
                for w in [btn["frame"], btn.get("top_label"), btn.get("main_label"), btn.get("sub_label")]:
                    if w:
                        w.unbind("<Button-1>")

        # Enter the new mode
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

        # Apply mode-specific changes, excluding "ON" button
        for btn in self.buttons:
            if btn.get("command_name") in ("yellow_f_function", "blue_g_function", "reload_program"):
                continue
            frame = btn["frame"]
            label = btn.get(label_key)
            if label:
                frame.config(bg=color)
                label.config(bg=color, fg="black")
                label.place(relx=0.5, rely=0.5, anchor="center")
                btn.get("main_label") and btn["main_label"].place_forget()
                btn.get("sub_label" if label_key == "top_label" else "top_label") and btn["sub_label" if label_key == "top_label" else "top_label"].place_forget()
                self._bind_mode_action(btn, mode)
        logger.info(f"Mode set: {mode}")

    def _bind_mode_action(self, btn, mode):
        def on_click(e, b=btn):
            if mode == "f":
                f_action(b, self.display, self)
            elif mode == "g":
                g_action(b, self.display, self)
        for w in [btn["frame"], btn.get("top_label"), btn.get("main_label"), btn.get("sub_label")]:
            if w:
                w.unbind("<Button-1>")
                w.bind("<Button-1>", on_click)

    def enter_value(self):
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

        if hasattr(self, 'entry_mode') and self.entry_mode == "gsb_label":
            label = self.display.raw_value
            try:
                self.gsb(label)
            except Exception as e:
                self.display.set_error(str(e))
            self.entry_mode = None
            self.is_user_entry = False
            return

        if self.is_user_entry:
            entry = self.display.raw_value
            val = interpret_in_base(entry, self.display.mode)
            stack._x_register = val
            self.is_user_entry = False

        stack.stack_lift()
        self.display.set_entry(format_in_current_base(stack.peek(), self.display.mode))
        self.stack_lift_enabled = False
        self.result_displayed = True
        self.update_stack_display()

    def enter_operator(self, operator):
        logger.info(f"Entering operator: {operator}, X={stack.peek()}, stack={stack._stack}")
        if self.program_mode:
            op_map = {"/": "10", "*": "20", "-": "30", "+": "40", ".": "48"}
            instruction = operator
            display_code = op_map.get(operator, operator)
            self.program_memory.append(instruction)
            step = len(self.program_memory)
            program_logger.info(f"{step:03d} - {instruction} ({display_code})")
            self.display.set_entry((step, display_code), program_mode=True)
            self.last_program_step = step
            return

        if self.is_user_entry:
            entry = self.display.raw_value
            val = interpret_in_base(entry, self.display.mode)
            stack._x_register = val
            self.is_user_entry = False
            self.display.clear_entry()

        if self.display.is_error_displayed:
            logger.info("Operation skipped due to existing error state")
            return

        operator = operator.upper()

        try:
            mask = (1 << stack.get_word_size()) - 1

            if operator in {"+", "-", "*", "/", "AND", "OR", "XOR", "RMD"}:
                if len(stack._stack) < 1:
                    raise StackUnderflowError(display=self.display)
                y = stack.pop()
                x = stack._x_register
                if operator == "+":
                    result = add(y, x)
                elif operator == "-":
                    result = subtract(x, y)
                elif operator == "*":
                    result = multiply(y, x)
                elif operator == "/":
                    if y == 0:
                        raise DivisionByZeroError(display=self.display)
                    result = divide(x, y)
                elif operator == "AND":
                    result = x & y & mask
                elif operator == "OR":
                    result = x | y & mask
                elif operator == "XOR":
                    result = x ^ y & mask
                elif operator == "RMD":
                    if y == 0:
                        raise DivisionByZeroError(display=self.display)
                    result = x % y
                stack._x_register = result
            elif operator == "NOT":
                x = stack._x_register
                result = ~x & mask
                stack._x_register = result
            else:
                raise InvalidOperandError(f"Unsupported operator: {operator}", display=self.display)

            if stack.get_complement_mode() == "UNSIGNED" and stack._x_register < 0:
                stack._x_register = stack._x_register & mask

            if self.entry_mode in {"sto", "rcl"}:
                self.entry_mode = None
                logger.info("Canceled STO/RCL operation")

            self.display.set_entry(format_in_current_base(stack.peek(), self.display.mode))
            self.display.raw_value = str(stack.peek())
            self.update_stack_display()
            self.stack_lift_enabled = True

        except HP16CError as e:
            self.display.set_error(str(e))
            logger.info(f"Error occurred: {e}")
        except Exception as e:
            self.display.set_error(str(e))
            logger.info(f"Unexpected error: {e}")

        self.post_enter = False

    def handle_error(self, exc: HP16CError):
        logger.info(f"Handling error: {exc.display_message}")
        if self.display is not None:
            original_value = self.display.current_entry
            self.display.set_entry(exc.display_message, raw=True)
            self.display.widget.after(5000, lambda: self.display.set_entry(original_value))
        else:
            raise exc
            print(f"Error: {exc.display_message}")

    def pop_value(self):
        logger.info("Popping value")
        try:
            val = stack.pop()
            stack.save_last_x()
            top_val = stack.peek()
            self.display.set_entry(format_in_current_base(top_val, self.display.mode))
            self.display.raw_value = str(top_val)
            self.update_stack_display()
            return val
        except HP16CError as e:
            self.handle_error(e)
            return 0

    def push_value(self, value):
        logger.info(f"Pushing value: {value}")
        stack.push(value)
        self.update_stack_display()

    def update_stack_display(self):
        if self.stack_display:
            y, z, t = [format_in_current_base(val, self.display.mode) for val in stack._stack[:3]]
            self.stack_display.config(text=f"Y: {y} Z: {z} T: {t}")
        self.display.update_stack_content()

    def count_bits(self):
        logger.info("Counting bits")
        try:
            stack.count_bits()
            top_val = stack.peek()
            self.display.set_entry(format_in_current_base(top_val, self.display.mode))
            self.display.raw_value = str(top_val)
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    def set_bit(self, bit_index):
        logger.info(f"Setting bit: {bit_index}")
        try:
            stack.set_bit(bit_index)
            top_val = stack.peek()
            self.display.set_entry(format_in_current_base(top_val, self.display.mode))
            self.display.raw_value = str(top_val)
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    def clear_bit(self, bit_index):
        logger.info(f"Clearing bit: {bit_index}")
        try:
            stack.clear_bit(bit_index)
            top_val = stack.peek()
            self.display.set_entry(format_in_current_base(top_val, self.display.mode))
            self.display.raw_value = str(top_val)
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    def test_bit(self, bit_index):
        logger.info(f"Testing bit: {bit_index}")
        try:
            result = stack.test_bit(bit_index)
            self.update_stack_display()
            return result
        except HP16CError as e:
            self.handle_error(e)
            return 0

    def absolute(self):
        logger.info("Computing absolute value")
        try:
            stack.absolute()
            top_val = stack.peek()
            self.display.set_entry(format_in_current_base(top_val, self.display.mode))
            self.display.raw_value = str(top_val)
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    # Normal Mode Functions 

    def roll_down(self):
        if self.is_user_entry:
            val = interpret_in_base(self.display.raw_value, self.display.mode)
            stack._x_register = val
            self.is_user_entry = False

        old_x = stack._x_register
        stack._x_register = stack._stack[0]
        stack._stack[0] = stack._stack[1]
        stack._stack[1] = stack._stack[2]
        stack._stack[2] = old_x

        self.display.set_entry(format_in_current_base(stack._x_register, self.display.mode))

    def swap_xy(self):
        if self.is_user_entry:
            val = interpret_in_base(self.display.raw_value, self.display.mode)
            stack._x_register = val
            self.is_user_entry = False

        temp = stack._x_register
        stack._x_register = stack._stack[0]
        stack._stack[0] = temp

        self.display.set_entry(format_in_current_base(stack._x_register, self.display.mode))

    def change_sign(self):
        logger.info("Changing sign")
        val = self.display.current_value or 0
        complement_mode = stack.get_complement_mode()
        word_size = stack.get_word_size()
        mask = (1 << word_size) - 1
        if complement_mode == "UNSIGNED":
            negated = (-val) & mask
        elif complement_mode == "1S":
            negated = (~val) & mask
        else:  # 2S
            negated = ((~val) + 1) & mask
        self.display.set_entry(negated)
        stack._x_register = negated
        self.is_user_entry = True
        self.stack_lift_enabled = True
        self.result_displayed = False

    def gsb(self, label=None):
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
                        if not instr.startswith("LBL "):
                            self.program.execute(self.stack)
                        self.current_line += 1
                except HP16CError as e:
                    self.handle_error(e)

    # f Mode Functions

    def set_word_size(self, bits):
        logger.info(f"Setting word size: {bits}")
        try:
            old_x = stack.peek()
            stack.set_word_size(bits)
            if stack._stack[0] != old_x:
                stack._x_register = stack._stack[0]
            else:
                stack._x_register = 0
            self.display.update_stack_content()
            self.update_stack_display()
            self.display.set_entry(format_in_current_base(stack.peek(), self.display.mode))
            self.display.raw_value = "0"
            self.is_user_entry = False
            self.result_displayed = True
            self.stack_lift_enabled = True
            return True
        except HP16CError as e:
            self.handle_error(e)
            return False

    def set_complement_mode(self, mode):
        logger.info(f"Setting complement mode: {mode}")
        try:
            stack.set_complement_mode(mode)
            self.update_stack_display()
            top_val = stack.peek()
            self.display.set_entry(format_in_current_base(top_val, self.display.mode))
            self.display.raw_value = str(top_val)
        except HP16CError as e:
            self.handle_error(e)

    def recall_i(self):
        logger.info("Recalling I register")
        try:
            stack.recall_i()
            top_val = stack.peek()
            self.display.set_entry(format_in_current_base(top_val, self.display.mode))
            self.display.raw_value = str(top_val)
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    def exchange_x_with_i(self):
        logger.info("Exchanging X with I register")
        try:
            top_val = stack.pop()
            i_val = stack.get_i()
            stack.push(i_val, duplicate_x=False)
            stack.store_in_i(top_val)
            self.display.set_entry(format_in_current_base(stack.peek(), self.display.mode))
            self.display.raw_value = str(stack.peek())
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    def store_in_i(self):
        logger.info("Storing in I register")
        try:
            stack.store_in_i()
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    def double_remainder(self):
        logger.info("Double remainder")
        try:
            stack.double_remainder()
            top_val = stack.peek()
            self.display.set_entry(format_in_current_base(top_val, self.display.mode))
            self.display.raw_value = str(top_val)
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    def mask_right(self, bits):
        logger.info(f"Masking right: {bits} bits")
        try:
            stack.mask_right(bits)
            top_val = stack.peek()
            self.display.set_entry(format_in_current_base(top_val, self.display.mode))
            self.display.raw_value = str(top_val)
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    def rotate_left(self):
        logger.info("Rotating left")
        try:
            stack.rotate_left()
            top_val = stack.peek()
            self.display.set_entry(format_in_current_base(top_val, self.display.mode))
            self.display.raw_value = str(top_val)
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    def rotate_right(self):
        logger.info("Rotating right")
        try:
            stack.rotate_right()
            top_val = stack.peek()
            self.display.set_entry(format_in_current_base(top_val, self.display.mode))
            self.display.raw_value = str(top_val)
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    def rotate_left_carry(self):
        logger.info("Rotating left with carry")
        try:
            stack.rotate_left_carry()
            top_val = stack.peek()
            self.display.set_entry(format_in_current_base(top_val, self.display.mode))
            self.display.raw_value = str(top_val)
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    def rotate_right_carry(self):
        logger.info("Rotating right with carry")
        try:
            stack.rotate_right_carry()
            top_val = stack.peek()
            self.display.set_entry(format_in_current_base(top_val, self.display.mode))
            self.display.raw_value = str(top_val)
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    def mask_left(self, bits):
        logger.info(f"Masking left: {bits} bits")
        try:
            stack.mask_left(bits)
            top_val = stack.peek()
            self.display.set_entry(format_in_current_base(top_val, self.display.mode))
            self.display.raw_value = str(top_val)
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    def shift_left(self):
        logger.info("Shifting left")
        try:
            stack.shift_left()
            top_val = stack.peek()
            self.display.set_entry(format_in_current_base(top_val, self.display.mode))
            self.display.raw_value = str(top_val)
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    def shift_right(self):
        logger.info("Shifting right")
        try:
            stack.shift_right()
            top_val = stack.peek()
            self.display.set_entry(format_in_current_base(top_val, self.display.mode))
            self.display.raw_value = str(top_val)
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    # g Mode Functions    
    def clear_x(self):
        stack._x_register = 0
        self.display.set_entry("0")
        self.display.raw_value = "0"
        self.is_user_entry = False
        self.stack_lift_enabled = True
        self.update_stack_display()
        logger.info("Cleared X register")

    def double_multiply(self):
        logger.info("Double multiplying")
        try:
            stack.double_multiply()
            top_val = stack.peek()
            self.display.set_entry(format_in_current_base(top_val, self.display.mode))
            self.display.raw_value = str(top_val)
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    def double_divide(self):
        logger.info("Double dividing")
        try:
            stack.double_divide()
            top_val = stack.peek()
            self.display.set_entry(format_in_current_base(top_val, self.display.mode))
            self.display.raw_value = str(top_val)
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    def left_justify(self):
        if self.is_user_entry:
            entry = self.display.raw_value
            val = interpret_in_base(entry, self.display.mode)
            stack._x_register = val
            self.is_user_entry = False
        try:
            stack.left_justify()
            top_val = stack.peek()
            self.display.set_entry(format_in_current_base(top_val, self.display.mode))
            self.display.raw_value = str(top_val)
            self.update_stack_display()
            self.stack_lift_enabled = True
            self.result_displayed = True
        except Exception as e:
            self.handle_error(e)

    def set_flag(self, flag_num):
        logger.info(f"Setting flag: {flag_num}")
        try:
            stack.set_flag(flag_num)
            self.update_stack_display()
            self.display.update_stack_content()
            current_val = stack.peek()
            formatted_value = format_in_current_base(current_val, self.display.mode, pad=False)
            self.display.set_entry(formatted_value)
            self.display.raw_value = formatted_value
            self.is_user_entry = False
            self.stack_lift_enabled = True
        except HP16CError as e:
            self.handle_error(e)
        except ValueError as e:
            self.handle_error(HP16CError(f"Invalid flag number: {flag_num}", "E01"))

    def clear_flag(self, flag_num):
        logger.info(f"Clearing flag: {flag_num}")
        try:
            stack.clear_flag(flag_num)
            self.update_stack_display()
            self.display.update_stack_content()
            current_val = stack.peek()
            formatted_value = format_in_current_base(current_val, self.display.mode, pad=False)
            self.display.set_entry(formatted_value)
            self.display.raw_value = formatted_value
        except HP16CError as e:
            self.handle_error(e)
        except ValueError as e:
            self.handle_error(HP16CError(f"Invalid flag number: {flag_num}", "E01"))

    def test_flag(self, flag_type):
        logger.info(f"Testing flag: {flag_type}")
        try:
            if flag_type == "CF":
                result = stack.get_carry_flag()
            else:
                result = stack.test_flag(int(flag_type))
            self.display.set_entry("1" if result else "0")
            self.update_stack_display()
            return result
        except (ValueError, HP16CError) as e:
            self.handle_error(HP16CError(f"Invalid flag type: {flag_type}", "E01"))
            return False