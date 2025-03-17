"""
controller.py

A single class that coordinates stack operations and the display.
Matches HP-16C RPN behavior per Owner's Handbook.
"""

import stack
import buttons
from buttons import revert_to_normal
from f_mode import f_action
from g_mode import g_action
from error import (
    HP16CError, StackUnderflowError, InvalidOperandError, 
    ShiftExceedsWordSizeError, InvalidBitOperationError
)
from base_conversion import format_in_current_base, current_base, interpret_in_current_base
from logging_config import logger

class HP16CController:
    def __init__(self, display, buttons):
        logger.info("Initializing HP16CController")
        self.display = display
        self.buttons = buttons
        self.post_enter = False
        self.f_mode_active = False
        self.g_mode_active = False

    def toggle_mode(self, mode):
        """Toggle f or g mode, updating button appearance and bindings."""
        logger.info(f"Toggling mode: {mode}, f_active={self.f_mode_active}, g_active={self.g_mode_active}")
        if (mode == "f" and self.f_mode_active) or (mode == "g" and self.g_mode_active):
            for btn in self.buttons:
                if btn.get("command_name") in ("yellow_f_function", "blue_g_function"):
                    continue
                revert_to_normal(btn, self.buttons, self.display, self)
            self.f_mode_active = False
            self.g_mode_active = False
            logger.info("Mode reset to normal")
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
        """Bind mode-specific actions to buttons."""
        def on_click(e, b=btn):
            if mode == "f":
                f_action(b, self.display, self)
            elif mode == "g":
                g_action(b, self.display, self)
            self.display.master.after(0, lambda: self.toggle_mode(mode))
        for w in [btn["frame"], btn.get("top_label"), btn.get("main_label"), btn.get("sub_label")]:
            if w:
                w.bind("<Button-1>", on_click)

    def enter_digit(self, digit):
        logger.info(f"Entering digit: {digit}")
        if self.post_enter:
            self.display.clear_entry()
            self.post_enter = False
        self.display.append_entry(digit)

    def enter_value(self):
        logger.info("Entering value")
        entry = self.display.get_entry()
        val = interpret_in_current_base(entry, current_base)
        stack.push(val)
        self.post_enter = True
        self.result_displayed = False
        self.display.set_entry(val)

    def enter_operator(self, operator):
        logger.info(f"Entering operator: {operator}")
        if operator == "R↓":
            stack.roll_down()
            result = stack.peek()
            self.display.set_entry(result)
            logger.info(f"Performed R↓: stack rotated down")
        else:
            entry = self.display.get_entry()
            val = interpret_in_current_base(entry, current_base)
            stack.push(val)
            try:
                y = stack.pop()
                x = stack.pop()
                if operator == "+":
                    result = stack.add(x, y)
                elif operator == "-":
                    result = stack.subtract(x, y)
                elif operator == "*":
                    result = stack.multiply(x, y)
                elif operator == "/":
                    result = stack.divide(x, y)
                elif operator == "AND":
                    result = x & y
                elif operator == "OR":
                    result = x | y
                elif operator == "XOR":
                    result = x ^ y
                elif operator == "NOT":
                    result = ~x
                    stack.push(y)
                elif operator == "RMD":
                    result = x % y
                else:
                    stack.push(x)
                    stack.push(y)
                    raise InvalidOperandError(f"Unsupported operator: {operator}")
                stack.push(result)
                self.display.set_entry(result)
                logger.info(f"Performed {operator}: result={result}")
            except HP16CError as e:
                self.handle_error(e)
            except Exception as e:
                self.handle_error(HP16CError(str(e)))

        self.post_enter = False
        self.result_displayed = operator != "R↓"

    def change_sign(self):
        """Change the sign of the current value based on complement mode."""
        val = self.display.current_value or 0
        if val == 0:
            return
        logger.info(f"Changing sign: {val}")
        complement_mode = stack.get_complement_mode()
        word_size = stack.get_word_size()
        mask = (1 << word_size) - 1

        if complement_mode == "UNSIGNED":
            negated = (0 - val) & mask
        elif complement_mode == "1S":
            negated = (~val) & mask
        else:  # 2S
            negated = ((~val) + 1) & mask

        self.display.current_value = negated
        self.display.raw_value = format_in_current_base(negated, self.display.mode)
        self.display.set_entry(self.display.raw_value)
        logger.info(f"Sign changed: {negated}")

    def handle_error(self, exc: HP16CError):
        """Display an error message for 3 seconds."""
        logger.info(f"Handling error: {exc.display_message}")
        self.display.set_entry(exc.display_message, raw=True)
        self.display.widget.after(3000, lambda: self.display.set_entry(0))

    def pop_value(self):
        """Pop a value from the stack and update the display."""
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

    def update_stack_display(self):
        """Update the stack content on the display."""
        self.display.update_stack_content()

    def push_value(self, value):
        """Push a value onto the stack and update the display."""
        logger.info(f"Pushing value: {value}")
        stack.push(value)
        self.update_stack_display()

    def shift_left(self):
        """Shift the top stack value left."""
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
        """Shift the top stack value right."""
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
        """Rotate the top stack value left."""
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
        """Rotate the top stack value right."""
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
        """Rotate the top stack value left with carry."""
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
        """Rotate the top stack value right with carry."""
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
        """Mask the leftmost bits of the top stack value."""
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
        """Mask the rightmost bits of the top stack value."""
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
        """Count the number of 1 bits in the top stack value."""
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
        """Set a specific bit in the top stack value."""
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
        """Clear a specific bit in the top stack value."""
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
        """Test if a specific bit is set in the top stack value."""
        logger.info(f"Testing bit: {bit_index}")
        try:
            result = stack.test_bit(bit_index)
            self.update_stack_display()
            return result
        except HP16CError as e:
            self.handle_error(e)
            return 0

    def left_justify(self):
        """Left justify the top stack value."""
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
        """Set the top stack value to its absolute value."""
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
        """Multiply the top two stack values."""
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
        """Divide the top two stack values."""
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
        """Compute the remainder of the top two stack values."""
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
        """Set a flag in the stack."""
        logger.info(f"Setting flag: {flag_type}")
        try:
            stack.set_flag(flag_type)
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    def clear_flag(self, flag_type):
        """Clear a flag in the stack."""
        logger.info(f"Clearing flag: {flag_type}")
        try:
            stack.clear_flag(flag_type)
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    def test_flag(self, flag_type):
        """Test a flag in the stack."""
        logger.info(f"Testing flag: {flag_type}")
        try:
            result = stack.test_flag(flag_type)
            return result
        except HP16CError as e:
            self.handle_error(e)
            return False

    def set_word_size(self, bits):
        """Set the stack word size."""
        logger.info(f"Setting word size: {bits}")
        try:
            stack.set_word_size(bits)
            self.update_stack_display()
            top_val = stack.peek()
            self.display.set_entry(format_in_current_base(top_val, self.display.mode))
            self.display.raw_value = str(top_val)
        except HP16CError as e:
            self.handle_error(e)

    def set_complement_mode(self, mode):
        """Set the stack complement mode."""
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
        """Store the top stack value in the I register."""
        logger.info("Storing in I register")
        try:
            stack.store_in_i()
            self.update_stack_display()
        except HP16CError as e:
            self.handle_error(e)

    def recall_i(self):
        """Recall the I register value to the stack."""
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
        """Exchange the top stack value with the I register."""
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