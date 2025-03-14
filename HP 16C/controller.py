"""
controller.py

A single class that coordinates stack operations and the display.
Matches HP-16C RPN behavior per the Owner's Handbook.
"""

import stack
import buttons.buttons as buttons
from error import HP16CError
from base_conversion import format_in_current_base, current_base, interpret_in_current_base

class HP16CController:
    def __init__(self, display, buttons):
        self.display = display
        self.buttons = buttons
        self.post_enter = False  # New flag to track ENTER state

    def enter_digit(self, digit: str):
            """Enter a digit into X, clearing if post-ENTER (page 17)."""
            print(f"[DEBUG] enter_digit called with {digit}; result_displayed: {self.display.result_displayed}")
            if digit.upper() not in buttons.VALID_CHARS[self.display.mode]:
                print(f"[DEBUG] Invalid digit '{digit}' for mode {self.display.mode}")
                return
            if self.display.result_displayed or self.post_enter:
                self.display.clear_entry()  # Reset to 0
                self.display.result_displayed = False
                self.post_enter = False  # Clear flag after reset
            self.display.append_entry(digit.upper())

    def enter_operator(self, operator: str):
        """Lift stack and perform operation using X and Y, per HP-16C RPN (pages 16-19)."""
        from stack import get_state
        if self.display.raw_value and self.display.raw_value != "0":
            val = interpret_in_current_base(self.display.raw_value, current_base)
            stack.push(val)
            self.display.raw_value = "0"
        self.post_enter = False
        current_stack = get_state()
        print(f"[DEBUG] Operator pressed: {operator}")
        print(f"[DEBUG] Current base: {self.display.mode}")
        print(f"[DEBUG] Stack before: {current_stack}")

        try:
            result = stack.perform_operation(operator)
            result_str = format_in_current_base(result, self.display.mode)
            self.display.set_entry(result_str)
            self.display.raw_value = result_str
            self.display.update_stack_content()
            self.display.result_displayed = True
            print(f"[DEBUG] Result: {result_str}, Stack after: {stack.get_state()}")
        except HP16CError as e:
            self.handle_error(e)

    def enter_value(self):
        raw_val = self.display.raw_value
        try:
            val = interpret_in_current_base(raw_val, current_base)
        except ValueError:
            val = 0
        stack.push(val, duplicate_x=False)
        self.display.current_value = val
        self.display.set_entry(val)  # Use set_entry for formatting
        self.display.raw_value = str(val)
        self.display.update_stack_content()
        self.display.result_displayed = False
        self.post_enter = True
        print(f"[DEBUG] Pushed {val} via ENTER. Stack: {stack.get_state()}")

    def handle_error(self, exc: HP16CError):
        self.display.set_entry(f"ERROR {exc.error_code}: {exc.message}")

    def pop_value(self):
        """Pop X and update display (page 27)."""
        val = stack.pop()
        top_val = stack.peek()
        self.display.set_entry(format_in_current_base(top_val, self.display.mode))
        self.display.raw_value = str(top_val)
        self.display.update_stack_content()
        return val

    def update_stack_display(self):
        self.display.update_stack_content()

    def push_value(self, value):
        """Push a value onto the stack and update the display."""
        stack.push(value)
        self.display.update_stack_content()

    # New Methods for Stack Features
    def shift_left(self):
        """Shift X left by 1 bit (SL, page 56)."""
        stack.shift_left()
        self.update_stack_display()

    def shift_right(self):
        """Shift X right by 1 bit (SR, page 56)."""
        stack.shift_right()
        self.update_stack_display()

    def rotate_left(self):
        """Rotate X left by 1 bit (RL, page 57)."""
        stack.rotate_left()
        self.update_stack_display()

    def rotate_right(self):
        """Rotate X right by 1 bit (RR, page 57)."""
        stack.rotate_right()
        self.update_stack_display()

    def rotate_left_carry(self):
        """Rotate X left through carry (RLC, page 58)."""
        stack.rotate_left_carry()
        self.update_stack_display()

    def rotate_right_carry(self):
        """Rotate X right through carry (RRC, page 58)."""
        stack.rotate_right_carry()
        self.update_stack_display()

    def mask_left(self, bits):
        """Mask leftmost bits of X (MASKL, page 59)."""
        stack.mask_left(bits)
        self.update_stack_display()

    def mask_right(self, bits):
        """Mask rightmost bits of X (MASKR, page 59)."""
        stack.mask_right(bits)
        self.update_stack_display()

    def count_bits(self):
        """Count 1 bits in X (#B, page 55)."""
        stack.count_bits()
        self.update_stack_display()

    def set_bit(self, bit_index):
        """Set bit in X (SB, page 51)."""
        stack.set_bit(bit_index)
        self.update_stack_display()

    def clear_bit(self, bit_index):
        """Clear bit in X (CB, page 51)."""
        stack.clear_bit(bit_index)
        self.update_stack_display()

    def test_bit(self, bit_index):
        """Test bit in X, update carry flag (B?, page 52)."""
        stack.test_bit(bit_index)
        self.update_stack_display()

    def left_justify(self):
        """Left justify X (LJ, page 58)."""
        stack.left_justify()
        self.update_stack_display()

    def absolute(self):
        """Absolute value of X (ABS, page 52)."""
        stack.absolute()
        self.update_stack_display()

    def double_multiply(self):
        """Double-word multiply Y and X (DBL×, page 60)."""
        stack.double_multiply()
        self.update_stack_display()

    def double_divide(self):
        """Double-word divide Y:X by Z (DBL÷, page 61)."""
        stack.double_divide()
        self.update_stack_display()

    def double_remainder(self):
        """Double-word remainder Y:X % Z (DBLR, page 62)."""
        stack.double_remainder()
        self.update_stack_display()

    def set_flag(self, flag_type):
        """Set carry or overflow flag (SF, page 50)."""
        stack.set_flag(flag_type)
        self.update_stack_display()

    def clear_flag(self, flag_type):
        """Clear carry or overflow flag (CF, page 50)."""
        stack.clear_flag(flag_type)
        self.update_stack_display()

    def test_flag(self, flag_type):
        """Test flag state (F?, page 50)."""
        return stack.test_flag(flag_type)  # Return for UI use

    def set_word_size(self, bits):
        """Set word size (WSIZE, page 45)."""
        stack.set_word_size(bits)
        self.update_stack_display()

    def set_complement_mode(self, mode):
        """Set complement mode (SC, page 46)."""
        stack.set_complement_mode(mode)
        self.update_stack_display()