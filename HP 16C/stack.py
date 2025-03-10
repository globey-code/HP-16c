"""
stack.py

Implements a 4-level stack. Raises custom exceptions on error.
No UI references. Only logic + data.
"""

from logging_config import logger
from error import StackUnderflowError, InvalidOperandError
from arithmetic import add, subtract, multiply, divide

stack = [0.0, 0.0, 0.0, 0.0]  # T, Z, Y, X
current_word_size = 16
current_complement_mode = "2S"

def push(value):
    global stack
    value = apply_word_size(value)
    stack.insert(0, value)
    if len(stack) > 4:
        stack.pop()
    logger.debug(f"Pushed {value}, stack={stack}")

def pop():
    global stack
    if not stack or stack[0] == 0.0:
        raise StackUnderflowError()
    top_val = stack[0]
    stack[:] = stack[1:] + [0.0]
    logger.debug(f"Popped {top_val}, stack={stack}")
    return top_val

def peek():
    return stack[0]

def clear_stack():
    global stack
    stack = [0.0, 0.0, 0.0, 0.0]
    logger.debug("Stack cleared")

def get_state():
    return stack.copy()

def set_word_size(bits):
    global current_word_size
    if bits < 1 or bits > 64:
        raise ValueError("Word size must be between 1 and 64.")
    current_word_size = bits
    logger.debug(f"Word size set to {bits}")

def get_word_size():
    return current_word_size

def apply_word_size(value):
    global current_word_size, current_complement_mode

    # If float has fractional part, keep as float
    if isinstance(value, float) and not value.is_integer():
        return value

    val_int = int(value)
    mask = (1 << current_word_size) - 1
    val_int &= mask  # mask off bits above current_word_size

    if current_complement_mode == "UNSIGNED":
        # In UNSIGNED mode, we do NOT interpret sign bit as negative
        # So we just return val_int as is (0..65535 if 16-bit, e.g.)
        return val_int

    elif current_complement_mode == "1S":
        # 1's complement logic: if sign bit is set, interpret as negative
        sign_bit = 1 << (current_word_size - 1)
        if val_int & sign_bit:
            # 1's complement negative
            # Typically, 1's complement negative is: -(~val_int & mask)
            # or -(mask ^ val_int)
            val_int = -((~val_int) & mask)
        return val_int

    else:  # "2S" (default)
        sign_bit = 1 << (current_word_size - 1)
        if val_int & sign_bit:
            val_int -= (1 << current_word_size)
        return val_int


def perform_operation(operator):
    top_value = pop()
    second_value = pop()

    if operator == "+":
        result = add(second_value, top_value)
    elif operator == "-":
        result = subtract(second_value, top_value)
    elif operator == "*":
        result = multiply(second_value, top_value)
    elif operator == "/":
        result = divide(second_value, top_value)
    else:
        raise InvalidOperandError()

    result = apply_word_size(result)
    push(result)
    return result

def duplicate():
    push(peek())

def swap():
    global stack
    if len(stack) >= 2:
        stack[0], stack[1] = stack[1], stack[0]
    logger.debug(f"Swapped top two, stack={stack}")

def roll():
    global stack
    stack = [stack[-1]] + stack[:-1]
    logger.debug(f"Rolled stack, stack={stack}")

def set_complement_mode(mode: str):
    global current_complement_mode
    valid_modes = {"1S", "2S", "UNSIGNED"}
    if mode not in valid_modes:
        raise ValueError(f"Invalid complement mode: {mode}")
    current_complement_mode = mode
    print(f"[stack] Complement mode set to {mode}")
