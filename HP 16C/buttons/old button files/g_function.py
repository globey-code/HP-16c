"""
g_function.py

Implements the "g" (blue) functions. Similar to f_function.py.
"""

import stack
import controller
from error import InvalidOperandError

def g_action(button):
    sub_text = button.get("orig_sub_text", "").strip()
    if sub_text == "LJ":
        action_lj()
    else:
        print("No g function for sub label:", sub_text)

def action_lj():
    """Left justify top stack value. Example operation."""
    val = stack.pop()
    # ... do something ...
    stack.push(val)
    # Possibly update display via controller
    # (In real usage, you'd do controller.pop_value() etc.)
