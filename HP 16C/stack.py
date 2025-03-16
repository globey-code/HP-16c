"""
stack.py

Implements a simple stack and word size/complement mode management for the HP-16C emulator.
This module provides basic operations like push, pop, and peek,
as well as functions to get/set the word size and complement mode,
and a function to apply the current word size to a value.
"""

from error import HP16CError, StackUnderflowError, InvalidOperandError, ShiftExceedsWordSizeError, InvalidBitOperationError

# --- Global Variables ---

# Simulate a 4-level stack (T, Z, Y, X); initial values are 0.
_stack = [0, 0, 0, 0]

# Default word size in bits (e.g., 16 bits)
_word_size = 16

# Complement mode: "UNSIGNED", "1S", or "2S"
_complement_mode = "UNSIGNED"

# To hold the last X value
_last_x = 0  

# --- Stack Operations ---
def get_state():
    """Return a copy of the current stack state."""
    return _stack.copy()

def push(val, duplicate_x=True):
    global _stack
    if not isinstance(val, (int, float)):
        raise InvalidOperandError("Value must be numeric")
    val = val & ((1 << _word_size) - 1)  # Truncate to word size
    _stack.pop(0)
    _stack.append(val)

def pop():
    global _stack, _last_x
    if all(x == 0 for x in _stack):
        raise StackUnderflowError()
    val = _stack.pop()
    _stack.insert(0, 0)
    _last_x = val
    return val

def peek():
    """Return the top value (X) of the stack without removing it."""
    return _stack[-1]

def perform_operation(op):
    y = pop()
    x = pop()
    _last_x = x
    result = 0
    if op == '+':
        result = x + y
    elif op == '-':
        result = x - y
    elif op == '*':
        result = x * y
    elif op == '/':
        if y == 0:
            raise ZeroDivisionError("Division by zero")
        result = int(x / y)
    elif op == 'xor':
        result = x ^ y
    elif op == 'and':
        result = x & y
    elif op == 'or':
        result = x | y
    elif op == 'not':
        result = ~x & ((1 << _word_size) - 1)
        push(y)  # NOT only operates on X, push Y back
    else:
        raise ValueError(f"Unknown operator: {op}")
    push(result)
    return result

# --- Bitwise and Stack Feature Operations ---
def shift_left():
    x = peek()
    result = x << 1
    result = result & ((1 << _word_size) - 1)  # Truncate to word size
    push(result)

def shift_right():
    x = peek()
    result = x >> 1
    result = result & ((1 << _word_size) - 1)  # Truncate to word size
    push(result)

def rotate_left():
    x = peek()
    result = (x << 1) | (x >> (_word_size - 1))
    result = result & ((1 << _word_size) - 1)  # Truncate to word size
    push(result)

def rotate_right():
    x = peek()
    result = (x >> 1) | (x << (_word_size - 1))
    result = result & ((1 << _word_size) - 1)  # Truncate to word size
    push(result)

def rotate_left_carry():
    x = peek() & ((1 << _word_size) - 1)  # Truncate first
    carry = 1 if get_carry_flag() else 0
    result = (x << 1) | carry
    set_carry_flag(x >> (_word_size - 1))
    result = result & ((1 << _word_size) - 1)  # Truncate again if needed
    push(result)

def rotate_right_carry():
    x = peek() & ((1 << _word_size) - 1)  # Truncate first
    carry = 1 if get_carry_flag() else 0
    result = (x >> 1) | (carry << (_word_size - 1))
    set_carry_flag(x & 1)
    result = result & ((1 << _word_size) - 1)  # Truncate again if needed
    push(result)

def mask_left(bits):
    """Mask leftmost bits of X (simplified implementation)."""
    x = peek()
    mask = (1 << bits) - 1
    push(x & mask)

def mask_right(bits):
    """Mask rightmost bits of X (simplified implementation)."""
    x = peek()
    mask = (1 << bits) - 1
    push(x & mask)

def count_bits():
    """Count the number of 1s in the binary representation of X."""
    x = peek()
    count = bin(x).count("1")
    push(count)

def set_bit(bit_index):
    x = peek()
    if bit_index < 0 or bit_index >= _word_size:
        raise InvalidBitOperationError()
    mask = 1 << bit_index
    result = x | mask
    result = result & ((1 << _word_size) - 1)  # Truncate to word size
    push(result)

def clear_bit(bit_index):
    x = peek()
    if bit_index < 0 or bit_index >= _word_size:
        raise InvalidBitOperationError()
    mask = ~(1 << bit_index)
    result = x & mask
    result = result & ((1 << _word_size) - 1)  # Truncate to word size
    push(result)

def test_bit(bit_index):
    """Test the bit at the given index in X; returns 0 or 1."""
    x = peek()
    return (x >> bit_index) & 1

def left_justify():
    """
    Left justify the number in X.
    (For many HP calculators, this may be a no-op or reformatting.)
    """
    # Not implemented in this simplified version.
    pass

def absolute():
    """Replace X with its absolute value."""
    x = peek()
    push(abs(x))

def double_multiply():
    """Double-word multiply the top two values."""
    y = pop()
    x = pop()
    push(x * y)

def double_divide():
    """Double-word divide the top two values."""
    y = pop()
    x = pop()
    if y == 0:
        raise ZeroDivisionError("Division by zero")
    push(int(x / y))

def double_remainder():
    y = pop()
    x = pop()
    if y == 0:
        raise DivisionByZeroError("Division by zero")
    push(x % y)

def set_flag(flag_type):
    """Set a flag (e.g., carry or overflow). Not implemented in this version."""
    pass

def clear_flag(flag_type):
    """Clear a flag (e.g., carry or overflow). Not implemented in this version."""
    pass

def test_flag(flag_type):
    """Test a flag. Not implemented; returns False."""
    return False

# --- Word Size and Complement Mode Management ---
def set_word_size(size):
    global _word_size
    if not 1 <= size <= 64:
        raise IncorrectWordSizeError()
    _word_size = size

def get_word_size():
    global _word_size
    return _word_size

def apply_word_size(val):
    """
    Apply the current word size to the value.
    For integer values, mask them to the current word size.
    Non-integer floats are returned unchanged.
    """
    try:
        if isinstance(val, float) and not val.is_integer():
            return val
        mask = (1 << _word_size) - 1
        return int(val) & mask
    except Exception:
        return val

# --- Complement Mode Management ---
def get_complement_mode():
    """Return the current complement mode."""
    return _complement_mode

def set_complement_mode(mode):
    """
    Set the current complement mode.
    mode should be "UNSIGNED", "1S", or "2S".
    """
    global _complement_mode
    if mode in {"UNSIGNED", "1S", "2S"}:
        _complement_mode = mode
    else:
        raise ValueError("Invalid complement mode. Must be 'UNSIGNED', '1S', or '2S'.")

 # Carry Flag 0 means no carry
_carry_flag = 0

# --- Carry Flag Management ---
def get_carry_flag():
    global _carry_flag
    return _carry_flag

def set_carry_flag(value):
    global _carry_flag
    _carry_flag = 1 if value else 0

# --- Last X Register Management ---
def get_last_x():
    global _last_x
    return _last_x

def save_last_x():
    global _last_x
    _last_x = peek()

def last_x():
    """Return the last X register value."""
    return _last_x


# --- Stack Initialization --- Testing purposes
def clear_stack():
    global _stack
    _stack = [0, 0, 0, 0]