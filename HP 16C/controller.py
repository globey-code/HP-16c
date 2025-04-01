# controller.py
# Coordinates stack operations and display updates for the HP-16C emulator, implementing RPN behavior.
# Author: GlobeyCode
# License: MIT
# Date: 3/23/2025
# Dependencies: Python 3.6+, HP-16C emulator modules (stack, buttons, error, base_conversion)

import stack
import base_conversion
from buttons import VALID_CHARS, revert_to_normal
from f_mode import f_action
from g_mode import g_action
from error import (
    HP16CError, StackUnderflowError, DivisionByZeroError, InvalidOperandError
)
from base_conversion import format_in_current_base, interpret_in_base
from logging_config import logger, program_logger

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
        self.program_mode = False
        self.entry_mode = None
        self.program_memory = []
        self.last_program_step = 0
        self.current_line = 0
        self.labels = {}
        self.return_stack = []
        self.decimal_entered = False

    def initialize(self):
        """Initialize stack mode and display after attributes are set."""
        stack.set_current_mode("DEC")
        if self.display is not None:
            self.display.set_entry("0.0")  # Initial display in float mode
        logger.info("Stack mode initialized to DEC")

    def enter_digit(self, digit):
        """Handle digit entry with live comma formatting in float mode."""
        logger.info(f"Entering digit: {digit}")
    
        # Handle setting decimal places in float mode
        if self.entry_mode == "set_decimal_places":
            if digit in "0123456789":
                decimal_places = int(digit)
                if decimal_places == 0:
                    self.display.decimal_places = None  # Floating decimal
                else:
                    self.display.decimal_places = decimal_places  # Fixed decimal
                self.display.set_mode("FLOAT")
                stack.set_current_mode("FLOAT")
                self.entry_mode = None
                current_value = stack.peek()
                formatted_value = self.format_float(current_value)
                self.display.set_entry(formatted_value, blink=True)
                logger.info(f"Set decimal places to {decimal_places if decimal_places else 'floating'}")
            return
    
        # Handle store mode
        if self.entry_mode == "sto":
            try:
                reg_num = int(digit)
                if 0 <= reg_num <= 9:
                    stack.set_register(reg_num, stack.peek())
                    self.entry_mode = None
                    self.is_user_entry = False
                    self.display.set_entry(format_in_current_base(stack.peek(), self.display.mode), blink=True)
                    logger.info(f"Stored X={stack.peek()} into R{reg_num}")
                else:
                    self.handle_error(HP16CError("Invalid register number", "E01"))
            except ValueError:
                self.handle_error(HP16CError("Invalid input for register", "E02"))
            return
        # Handle recall mode
        elif self.entry_mode == "rcl":
            try:
                reg_num = int(digit)
                if 0 <= reg_num <= 9:
                    value = stack.get_register(reg_num)
                    stack.push(value)
                    self.display.set_entry(format_in_current_base(value, self.display.mode), blink=True)
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

        # Validate digit for current mode
        if digit.upper() not in VALID_CHARS[self.display.mode]:
            logger.info(f"Ignoring invalid digit {digit} for base {self.display.mode}")
            return

        # Initialize entry if not already in user entry mode
        if not self.is_user_entry:
            self.display.clear_entry()
            self.is_user_entry = True
            self.decimal_entered = False
            self.result_displayed = False

        # Handle float mode input
        if self.display.mode == "FLOAT":
            if digit == ".":
                if self.decimal_entered:
                    logger.info("Ignoring additional decimal point")
                    return
                self.decimal_entered = True
                self.display.raw_value += "."
            elif digit in "0123456789":
                self.display.raw_value += digit
            formatted_value = self.format_float_with_commas(self.display.raw_value)
            self.display.set_entry(formatted_value, raw=True)
        # Handle other modes (integer bases)
        else:
            self.display.append_entry(digit)
            val = interpret_in_base(self.display.raw_value, self.display.mode)
            stack._x_register = val
            self.update_stack_display()

    def format_float_with_commas(self, raw_value):
        """Format the raw float string with commas in the integer part."""
        if not raw_value:
            return "0"
        if raw_value.startswith("-"):
            sign = "-"
            number = raw_value[1:]
        else:
            sign = ""
            number = raw_value
        if "." in number:
            integer_part, fractional_part = number.split(".")
            integer_part = "{:,}".format(int(integer_part)) if integer_part else "0"
            return f"{sign}{integer_part}.{fractional_part}"
        else:
            integer_part = "{:,}".format(int(number)) if number else "0"
            return f"{sign}{integer_part}"

    def format_float(self, value):
        """Format a number as a float based on decimal_places setting."""
        if self.display.decimal_places is not None:
            return "{:.{}f}".format(float(value), self.display.decimal_places)
        else:
            return "{:.9f}".format(float(value)).rstrip('0').rstrip('.')

    def delete_digit(self):
        """Remove the last digit and reformat the display in float mode."""
        if self.is_user_entry and self.display.raw_value:
            self.display.raw_value = self.display.raw_value[:-1]
            if not self.display.raw_value:
                self.is_user_entry = False
                self.display.set_entry("0", raw=True)
            else:
                formatted_value = self.format_float_with_commas(self.display.raw_value)
                self.display.set_entry(formatted_value, raw=True)
                self.decimal_entered = "." in self.display.raw_value

    def finalize_entry(self):
        """Finalize the current user entry and set it to X register."""
        if self.is_user_entry:
            entry = self.display.raw_value
            val = interpret_in_base(entry, self.display.mode)
            stack._x_register = val
            self.is_user_entry = False
            self.display.clear_entry()

    def enter_value(self):
        """Finalize the entered value and push it onto the stack."""
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
            if self.display.mode == "FLOAT":
                val = float(entry)
                if '.' in entry:
                    entry_str = "{:,.9f}".format(val).rstrip('0').rstrip('.')
                else:
                    integer_part = "{:,}".format(int(val))
                    entry_str = f"{integer_part}.0"
                self.display.set_entry(entry_str, raw=False, blink=True)
                stack._x_register = val
            else:
                val = interpret_in_base(entry, self.display.mode)
                stack._x_register = val
                self.display.set_entry(format_in_current_base(val, self.display.mode), blink=True)
            self.is_user_entry = False
            self.decimal_entered = False

        stack.stack_lift()
        self.stack_lift_enabled = False
        self.result_displayed = True
        self.update_stack_display()

    def update_display(self):
        """Update the display based on the current state."""
        if self.is_user_entry:
            self.display.set_entry(self.display.raw_value, raw=True)
        else:
            self.display.set_entry(format_in_current_base(stack.peek(), self.display.mode))

    def update_stack_display(self):
        """Update the stack display with current Y, Z, T values."""
        logger.debug("Updating stack display")
        if self.stack_display:
            if self.display.mode == "FLOAT":
                formatted_stack = [f"{float(x):.9f}".rstrip("0").rstrip(".") for x in stack._stack[:3]]
            else:
                formatted_stack = [format_in_current_base(x, self.display.mode) for x in stack._stack[:3]]
            while len(formatted_stack) < 3:
                formatted_stack.insert(0, "0")
            y, z, t = formatted_stack[-3:]
            self.stack_display.config(text=f"Y: {y} Z: {z} T: {t}")
        self.display.update_stack_content()

    def toggle_stack_display(self):
        """Toggle the visibility of the stack display."""
        if self.stack_display.winfo_ismapped():
            self.stack_display.place_forget()
            logger.info("Stack display hidden")
        else:
            self.stack_display.place(x=125, y=110, width=575, height=40)
            self.update_stack_display()
            logger.info("Stack display shown")

    def enter_operator(self, operator):
        """Handle operator input by delegating to stack.py."""
        logger.info(f"Entering operator: {operator}, X={stack.peek()}, stack={stack._stack}")
        if self.program_mode:
            return

        try:
            self.finalize_entry()
            if self.display.is_error_displayed:
                logger.info("Operation skipped due to existing error state")
                return
            result = stack.perform_operation(operator)
            self.display.set_entry(format_in_current_base(result, self.display.mode))
            self.update_stack_display()
            self.stack_lift_enabled = True
        except HP16CError as e:
            self.handle_error(e)
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
        if self.display.mode == "FLOAT":
            if self.is_user_entry:
                val = self.display.raw_value or "0"
                if val.startswith("-"):
                    negated = val[1:]
                else:
                    negated = "-" + val
                self.display.raw_value = negated
                self.display.set_entry(self.format_float_with_commas(negated), raw=True, blink=False)
            else:
                val = float(stack._x_register or 0)
                negated = -val
                stack._x_register = negated
                self.display.set_entry("{:,.9f}".format(negated).rstrip('0').rstrip('.'), raw=False, blink=True)
                self.stack_lift_enabled = False
        else:
            val = int(self.display.current_value or 0)
            complement_mode = stack.get_complement_mode()
            word_size = stack.get_word_size()
            mask = (1 << word_size) - 1
            if complement_mode == "UNSIGNED":
                negated = (-val) & mask
            elif complement_mode == "1S":
                negated = (~val) & mask
            else:  # 2S
                negated = ((~val) + 1) & mask
            stack._x_register = negated
            self.display.set_entry(format_in_current_base(negated, self.display.mode), blink=True)
            self.stack_lift_enabled = False

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

    def build_labels(self):
        self.labels = {}
        for i, cmd in enumerate(self.program_memory):
            if cmd[0] == "label":
                self.labels[cmd[1]] = i

    def run_program(self):
        if self.program_mode:
            return
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
                pass
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

    def toggle_mode(self, mode):
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