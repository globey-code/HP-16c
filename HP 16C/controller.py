"""
controller.py

A single class that coordinates stack operations and the display.
No circular imports: we import stack here, but not the other way around.
"""

import stack
from error import HP16CError
import buttons


class HP16CController:
    def __init__(self, display, buttons):
        self.display = display  # The UI display instance
        self.buttons = buttons  # The UI buttons instance

    def enter_digit(self, digit: str):
        """User pressed a digit (0-9, A-F)."""
        self.display.append_entry(digit)

    def enter_operator(self, operator: str):
        """Perform +, -, *, / on the stack."""
        try:
            result = stack.perform_operation(operator)
            self.display.set_entry(str(result))
            self.display.update_stack_content()
        except HP16CError as e:
            self.handle_error(e)

    def enter_value(self):
        """Equivalent of pressing 'ENTER': push display value onto the stack."""
        raw_val = self.display.raw_value
        try:
            val = float(raw_val) if "." in raw_val else int(raw_val)
        except ValueError:
            val = 0
        try:
            stack.push(val)
            self.display.clear_entry()
            self.display.update_stack_content()
        except HP16CError as e:
            self.handle_error(e)

    def handle_error(self, exc: HP16CError):
        self.display.set_entry(f"ERROR {exc.error_code}: {exc.message}")
    
    def pop_value(self):
        val = stack.pop()
        top_val = stack.peek()
        self.display.set_entry(str(top_val))
        return val

    def update_stack_display(self):
        self.display.update_stack_content()

    def push_value(value, display_widget):
        """Push the given value onto the stack, then update the display."""
        stack.push(value)
        # Optionally update the display to show the new top of stack
        display_widget.update_stack_content()
