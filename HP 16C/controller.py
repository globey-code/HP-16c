# controller.py
# Coordinates stack operations and display updates for the HP-16C emulator, implementing RPN behavior.
# Author: GlobeyCode
# License: MIT
# Date: 3/23/2025
# Dependencies: Python 3.6+, HP-16C emulator modules (stack, buttons, error, base_conversion, arithmetic)

import stack
import buttons
from buttons import VALID_CHARS
from buttons import revert_to_normal
from f_mode import f_action
from g_mode import g_action
from error import HP16CError, StackUnderflowError, InvalidOperandError
from base_conversion import format_in_current_base, interpret_in_base
from logging_config import logger
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

    def enter_digit(self, digit):
        logger.info(f"Entering digit: {digit}")
        digit = digit.upper()
        if digit not in VALID_CHARS[self.display.mode]:
            logger.info(f"Ignoring invalid digit {digit} for base {self.display.mode}")
            return

        # If this is the first digit after an operation or result, lift stack and clear entry
        if not self.is_user_entry:
            if self.stack_lift_enabled:
                stack.stack_lift()
                self.stack_lift_enabled = False
            self.display.clear_entry()  # Reset raw_value to "0"
            self.result_displayed = False

        # Append the digit to the current entry
        test_input = self.display.raw_value + digit
        try:
            if self.display.mode == "OCT":
                value = int(test_input, 8)
            elif self.display.mode == "DEC":
                value = int(test_input, 10)
            elif self.display.mode == "HEX":
                value = int(test_input, 16)
            else:
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
        if (mode == "f" and self.f_mode_active) or (mode == "g" and self.g_mode_active):
            for btn in self.buttons:
                if btn.get("command_name") in ("yellow_f_function", "blue_g_function"):
                    continue
                revert_to_normal(btn, self.buttons, self.display, self)
            self.f_mode_active = False
            self.g_mode_active = False
            logger.info("Mode reset to normal")
            if not self.display.is_error_displayed:
                self.display.set_entry(stack.peek())
                self.result_displayed = True
            else:
                logger.info("Display update deferred due to active error")
            return

        for btn in self.buttons:
            if btn.get("command_name") in ("yellow_f_function", "blue_g_function"):
                continue
            revert_to_normal(btn, self.buttons, self.display, self)

        if mode == "f":
            self.f_mode_active = True
            self.g_mode_active = False
            color = "#e3af01"
            label_key = "top_label"
        elif mode == "g":
            self.f_mode_active = False
            self.g_mode_active = True
            color = "#59b7d1"
            label_key = "sub_label"
        else:
            logger.warning(f"Invalid mode: {mode}")
            return

        for btn in self.buttons:
            if btn.get("command_name") in ("yellow_f_function", "blue_g_function"):
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
                handled = f_action(b, self.display, self)
                if not handled:
                    self.display.master.after(0, lambda: self.toggle_mode(mode))
            elif mode == "g":
                g_action(b, self.display, self)
                self.display.master.after(0, lambda: self.toggle_mode(mode))
        for w in [btn["frame"], btn.get("top_label"), btn.get("main_label"), btn.get("sub_label")]:
            if w:
                w.bind("<Button-1>", on_click)

    def enter_value(self):
        logger.info("Entering value (lifting stack)")
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

        if self.is_user_entry:
            entry = self.display.raw_value
            val = interpret_in_base(entry, self.display.mode)
            stack._x_register = val
            self.is_user_entry = False
            self.display.clear_entry()

        if self.display.is_error_displayed:
            logger.info("Operation skipped due to existing error state")
            return

        try:
            if operator in {"+", "-", "*", "/", "AND", "OR", "XOR", "RMD"}:
                if len(stack._stack) < 1:
                    raise StackUnderflowError("Insufficient operands on stack")
                y = stack._stack[0]  # Y from stack
                x = stack._x_register  # X from register
                if operator == "+":
                    result = add(x, y)
                elif operator == "-":
                    result = subtract(y, x)
                elif operator == "*":
                    result = multiply(x, y)
                elif operator == "/":
                    if x == 0:
                        raise DivisionByZeroError()
                    result = divide(y, x)
                elif operator == "AND":
                    result = x & y
                elif operator == "OR":
                    result = x | y
                elif operator == "XOR":
                    result = x ^ y
                elif operator == "RMD":
                    if x == 0:
                        raise DivisionByZeroError()
                    result = y % x
                # Update stack: drop stack correctly
                stack._stack[0] = stack._stack[1]  # Y = Z
                stack._stack[1] = stack._stack[2]  # Z = T
                # T remains stack._stack[2]
                stack._x_register = result  # Set result as new X
                self.display.set_entry(format_in_current_base(result, self.display.mode))
                self.display.raw_value = str(result)
                self.update_stack_display()
                self.stack_lift_enabled = True  # Enable stack lift for next entry
            elif operator == "NOT":
                x = stack._x_register
                result = ~x & ((1 << stack.get_word_size()) - 1)
                stack._x_register = result
                # Do not lift stack for unary operation
                self.display.set_entry(format_in_current_base(result, self.display.mode))
                self.display.raw_value = str(result)
                self.update_stack_display()
                self.stack_lift_enabled = True
            else:
                raise InvalidOperandError(f"Unsupported operator: {operator}")
        except HP16CError as e:
            self.handle_error(e)
            self.display.set_error()
        except Exception as e:
            self.handle_error(HP16CError(str(e)))
            self.display.set_error()

        self.post_enter = False

    def change_sign(self):
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

    def handle_error(self, exc: HP16CError):
        logger.info(f"Handling error: {exc.display_message}")
        original_value = self.display.current_entry
        self.display.set_entry(exc.display_message, raw=True)
        self.display.widget.after(5000, lambda: self.display.set_entry(original_value))

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

    def left_justify(self):
        logger.info("Left justifying")
        try:
            stack.left_justify()
            top_val = stack.peek()
            self.display.set_entry(format_in_current_base(top_val, self.display.mode))
            self.display.raw_value = str(top_val)
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

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

    def set_flag(self, flag_type):
        logger.info(f"Setting flag: {flag_type}")
        try:
            stack.set_flag(flag_type)
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    def clear_flag(self, flag_type):
        logger.info(f"Clearing flag: {flag_type}")
        try:
            stack.clear_flag(flag_type)
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    def test_flag(self, flag_type):
        logger.info(f"Testing flag: {flag_type}")
        try:
            result = stack.test_flag(flag_type)
            return result
        except HP16CError as e:
            self.handle_error(e)
            return False

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

    def store_in_i(self):
        logger.info("Storing in I register")
        try:
            stack.store_in_i()
            self.update_stack_display()
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