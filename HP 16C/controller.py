"""
controller.py

A single class that coordinates stack operations and the display.
Matches HP-16C RPN behavior per the Owner's Handbook.
"""

import stack
import buttons as buttons
from f_mode import f_action
from g_mode import g_action
from error import HP16CError
from base_conversion import format_in_current_base, current_base, interpret_in_current_base
from error import HP16CError, StackUnderflowError, InvalidOperandError, ShiftExceedsWordSizeError, InvalidBitOperationError


class HP16CController:
    def __init__(self, display, buttons):
        self.display = display
        self.buttons = buttons
        self.post_enter = False
        self.f_mode_active = False  # Track f-mode
        self.g_mode_active = False  # Track g-mode

    # New centralized toggle method
    def toggle_mode(self, mode):
        """Toggle f or g mode, updating button appearance and bindings."""
        from buttons import revert_to_normal, bind_normal_button

        # Reset to normal if toggling off or switching modes
        if (mode == "f" and self.f_mode_active) or (mode == "g" and self.g_mode_active):
            for btn in self.buttons:
                if btn.get("command_name") in ("yellow_f_function", "blue_g_function"):
                    continue
                revert_to_normal(btn, self.buttons, self.display, self)
            self.f_mode_active = False
            self.g_mode_active = False
            return

        # Reset all buttons to normal first
        for btn in self.buttons:
            if btn.get("command_name") in ("yellow_f_function", "blue_g_function"):
                continue
            revert_to_normal(btn, self.buttons, self.display, self)

        # Set new mode
        if mode == "f":
            self.f_mode_active = True
            self.g_mode_active = False
            color = "#e3af01"  # Yellow for f-mode
            label_key = "top_label"
            orig_text_key = "orig_top_text"
        elif mode == "g":
            self.f_mode_active = False
            self.g_mode_active = True
            color = "#59b7d1"  # Blue for g-mode
            label_key = "sub_label"
            orig_text_key = "orig_sub_text"
        else:
            return

        # Update button appearance and bindings
        for btn in self.buttons:
            if btn.get("command_name") in ("yellow_f_function", "blue_g_function"):
                continue
            frame = btn["frame"]
            label = btn.get(label_key)
            main_label = btn.get("main_label")
            other_label = btn.get("sub_label" if label_key == "top_label" else "top_label")

            if label:
                frame.config(bg=color)
                label.config(bg=color, fg="black")
                label.place(relx=0.5, rely=0.5, anchor="center")
                if main_label:
                    main_label.place_forget()
                if other_label:
                    other_label.place_forget()
                self._bind_mode_action(btn, mode)

    def _bind_mode_action(self, btn, mode):
        def on_click(e, b=btn):
            if mode == "f":
                from f_mode import f_action
                f_action(b, self.display, self)
            elif mode == "g":
                from g_mode import g_action
                g_action(b, self.display, self)
            self.toggle_mode(mode)  # Reset mode after action
        for w in [btn["frame"], btn.get("top_label"), btn.get("main_label"), btn.get("sub_label")]:
            if w:
                w.bind("<Button-1>", on_click)

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
        print(f"[DEBUG] enter_operator called with operator='{operator}'")
        if self.display.raw_value and self.display.raw_value != "0":
            val = interpret_in_current_base(self.display.raw_value, current_base)
            stack.push(val)
            self.display.raw_value = "0"
        self.post_enter = False
        try:
            result = stack.perform_operation(operator)
            self.save_last_x(stack.peek())
            result_str = format_in_current_base(result, self.display.mode)
            self.display.set_entry(result_str)
            self.display.raw_value = result_str
            self.display.update_stack_content()
            self.display.result_displayed = True
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
        print(f"[DEBUG] Handling error: {exc.error_code} - {exc.message}")
        self.display.set_entry(exc.display_message, raw=True)
        self.display.widget.after(3000, lambda: self.display.set_entry(0))

    def pop_value(self):
        val = stack.pop()
        self.save_last_x(val)  # Save popped value
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
        if bits < 0 or bits > stack.get_word_size():
            raise InvalidBitOperationError()
        x = stack.peek()
        mask = ((1 << (stack.get_word_size() - bits)) - 1) << bits
        result = x & mask
        stack.push(result)

    def mask_right(self, bits):
        if bits < 0 or bits > stack.get_word_size():
            raise InvalidBitOperationError()
        x = stack.peek()
        mask = (1 << bits) - 1
        result = x & mask
        stack.push(result)

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
 
    def store_in_i(self):
        """Store the X register value into the I register."""
        val = stack.peek()
        stack.set_i_register(val)
        print(f"[DEBUG] Stored {val} in I register")

# New class for g-mode functions
    def last_x(self):
        return stack.get_last_x()

    def save_last_x(self, x):
        self.last_x = x