"""
modes.py

Handles toggling f/g modes. In many HP16C clones, these modify the meaning of buttons.
Here, we store just an example skeleton to show how to avoid circular imports.
"""

from error import InvalidOperandError
import stack

f_mode_active = False
g_mode_active = False

def toggle_f_mode():
    global f_mode_active
    f_mode_active = not f_mode_active

def toggle_g_mode():
    global g_mode_active
    g_mode_active = not g_mode_active

def do_shift_left(controller):
    """
    Example of an 'f' function: shift left the top of the stack by 1 bit.
    Called from the button manager when in f-mode.
    """
    try:
        val = stack.pop()
        if isinstance(val, float) and val.is_integer():
            val = int(val)
        if not isinstance(val, int):
            raise InvalidOperandError()
        shifted = stack.apply_word_size(val << 1)
        stack.push(shifted)
        controller.display.set_entry(str(shifted))
        controller.display.update_stack_content()
    except InvalidOperandError as e:
        controller.handle_error(e)
