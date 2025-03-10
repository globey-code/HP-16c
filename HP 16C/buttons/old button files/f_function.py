"""
f_function.py

Implements the "f" (yellow) functions. Now we call 'stack' or 'controller' 
logic but do not do direct UI manipulation beyond setting display entries.

Reason for change:
- Raises exceptions if needed. The controller or UI catches them.
"""

import stack
from error import StackUnderflowError, InvalidOperandError
from word_size import set_word_size_from_input
import controller

def f_action(button, display_widget):
    top_text = button.get("orig_top_text", "").replace("\n", "").strip()
    if top_text == "SL":
        action_sl(display_widget)
    # ... other "f" functions ...
    else:
        print("No f function defined for top label:", top_text)

def action_sl(display_widget):
    """Shift left the top stack value."""
    val = controller.pop_value(display_widget)  # pop top
    if val is None:
        return  # Error was handled
    if isinstance(val, float) and val.is_integer():
        val = int(val)
    if not isinstance(val, int):
        raise InvalidOperandError()
    result = stack.apply_word_size(val << 1)
    stack.push(result)
    display_widget.set_entry(str(result))
    controller.update_stack_display(display_widget)
    print(f"Shift Left: {val} -> {result}")

def action_wsize(display_widget):
    """Set word size from the display's raw_value."""
    input_value = display_widget.raw_value
    new_size = set_word_size_from_input(input_value)
    if new_size is not None:
        display_widget.clear_entry()
        display_widget.word_size_label.config(text=f"WS: {new_size} bits")
