"""
stack.py

Implements a 4-level stack per HP-16C Owner's Handbook (pages 27-31).
Includes all arithmetic, bit operations, shifts, and double precision from the manual.
No UI references. Only logic + data.
"""

from logging_config import logger
from error import StackUnderflowError, InvalidOperandError
from arithmetic import add, subtract, multiply, divide
from base_conversion import current_base

stack = [0.0, 0.0, 0.0, 0.0]  # T, Z, Y, X (page 27)
current_word_size = 16  # Default 16 bits (page 45)
current_complement_mode = "2S"  # Default two's complement (page 46)
carry_flag = False  # CF for overflow/carry (page 49)
overflow_flag = False  # Overflow indicator (page 50)

# Core Stack Operations
def push(value, duplicate_x=False):
    """Push a value onto the stack, lifting X to Y (page 28)."""
    global stack
    value = apply_word_size(value)
    if duplicate_x:
        stack.insert(0, stack[0])
    stack.insert(0, value)
    if len(stack) > 4:
        stack.pop()
    logger.debug(f"Pushed {value}, stack={stack}")

def pop():
    """Pop X from the stack, shifting Y to X (page 27)."""
    global stack
    if not stack:  # Only raise if stack is truly empty
        raise StackUnderflowError()
    top_val = stack[0]
    stack[:] = stack[1:] + [0.0]
    logger.debug(f"Popped {top_val}, stack={stack}")
    return top_val

def peek():
    """Return the value in X without popping (page 27)."""
    return stack[0]

def clear_stack():
    """Clear all stack levels to 0 (page 30, CLx extends to all)."""
    global stack
    stack = [0.0, 0.0, 0.0, 0.0]
    logger.debug("Stack cleared")

def get_state():
    """Return a copy of the current stack (page 27)."""
    return stack.copy()

def duplicate():
    """Duplicate X into Y, shifting stack up (page 28)."""
    val = peek()
    stack[:] = [val] + stack[:3]
    logger.debug(f"Duplicated X: stack={stack}")

def swap():
    """Swap X and Y (page 29, x<>y)."""
    global stack
    if len(stack) >= 2:
        stack[0], stack[1] = stack[1], stack[0]
    logger.debug(f"Swapped top two, stack={stack}")

def roll():
    """Roll stack down (T to X, X to Y, etc.) (page 29, R↓)."""
    global stack
    stack = [stack[-1]] + stack[:-1]
    logger.debug(f"Rolled stack, stack={stack}")

# Configuration Functions
def set_word_size(bits):
    """Set word size from 1 to 64 bits (page 45)."""
    global current_word_size
    if not 1 <= bits <= 64:
        raise ValueError("Word size must be between 1 and 64.")
    current_word_size = bits
    logger.debug(f"Word size set to {bits}")

def get_word_size():
    """Return current word size (page 45)."""
    return current_word_size

def set_complement_mode(mode: str):
    """Set complement mode: 1S, 2S, UNSIGNED (page 46)."""
    global current_complement_mode
    valid_modes = {"1S", "2S", "UNSIGNED"}
    if mode not in valid_modes:
        raise ValueError(f"Invalid complement mode: {mode}")
    current_complement_mode = mode
    print(f"[stack] Complement mode set to {mode}")

def apply_word_size(value):
    """Apply word size and complement mode to value (pages 46-48)."""
    global current_word_size, current_complement_mode
    val_int = int(value)

    if current_base == "DEC":
        return val_int

    mask = (1 << current_word_size) - 1
    val_int &= mask

    if current_complement_mode == "UNSIGNED":
        return val_int
    elif current_complement_mode == "1S":
        sign_bit = 1 << (current_word_size - 1)
        if val_int & sign_bit:
            val_int = -((~val_int) & mask)
        return val_int
    else:  # "2S"
        sign_bit = 1 << (current_word_size - 1)
        if val_int & sign_bit:
            val_int -= (1 << current_word_size)
        return val_int

# Arithmetic and Bit Operations
def perform_operation(operator):
    """Perform arithmetic or bit operation on X and Y (pages 16-19, 53-55)."""
    global carry_flag, overflow_flag
    top_value = pop()  # X
    second_value = pop()  # Y

    if operator == "+":
        result = add(second_value, top_value)
    elif operator == "-":
        result = subtract(second_value, top_value)
    elif operator == "*":
        result = multiply(second_value, top_value)
    elif operator == "/":
        result = divide(second_value, top_value)
    elif operator == "AND":
        result = int(second_value) & int(top_value)  # page 53
    elif operator == "OR":
        result = int(second_value) | int(top_value)  # page 54
    elif operator == "XOR":
        result = int(second_value) ^ int(top_value)  # page 54
    elif operator == "NOT":
        push(second_value)  # Unary, restore Y
        result = ~int(top_value) & ((1 << current_word_size) - 1)  # page 55
    elif operator == "RMD":
        if top_value == 0:
            raise InvalidOperandError()
        result = int(second_value) % int(top_value)  # page 54
    else:
        raise InvalidOperandError()

    if current_base != "DEC":
        mask = (1 << current_word_size) - 1
        carry_flag = result > mask or result < -mask
        result = apply_word_size(result)
        overflow_flag = carry_flag  # Simplified overflow logic
    push(result)
    return result

def shift_left():
    """Shift X left by 1 bit (SL, page 56)."""
    global carry_flag
    val = int(pop())
    mask = (1 << current_word_size) - 1
    carry_flag = bool(val & (1 << (current_word_size - 1)))
    result = (val << 1) & mask
    push(result)
    logger.debug(f"Shift left: {val} -> {result}, carry={carry_flag}")

def shift_right():
    """Shift X right by 1 bit (SR, page 56)."""
    global carry_flag
    val = int(pop())
    carry_flag = bool(val & 1)
    result = val >> 1
    push(result)
    logger.debug(f"Shift right: {val} -> {result}, carry={carry_flag}")

def rotate_left():
    """Rotate X left by 1 bit (RL, page 57)."""
    val = int(pop())
    mask = (1 << current_word_size) - 1
    carry = (val >> (current_word_size - 1)) & 1
    result = ((val << 1) & mask) | carry
    push(result)
    logger.debug(f"Rotate left: {val} -> {result}")

def rotate_right():
    """Rotate X right by 1 bit (RR, page 57)."""
    val = int(pop())
    mask = (1 << current_word_size) - 1
    carry = (val & 1) << (current_word_size - 1)
    result = (val >> 1) | carry
    push(result)
    logger.debug(f"Rotate right: {val} -> {result}")

def rotate_left_carry():
    """Rotate X left through carry (RLC, page 58)."""
    global carry_flag
    val = int(pop())
    mask = (1 << current_word_size) - 1
    new_carry = bool(val & (1 << (current_word_size - 1)))
    result = ((val << 1) & mask) | (1 if carry_flag else 0)
    carry_flag = new_carry
    push(result)
    logger.debug(f"Rotate left carry: {val} -> {result}, carry={carry_flag}")

def rotate_right_carry():
    """Rotate X right through carry (RRC, page 58)."""
    global carry_flag
    val = int(pop())
    mask = (1 << current_word_size) - 1
    new_carry = bool(val & 1)
    result = (val >> 1) | ((1 << (current_word_size - 1)) if carry_flag else 0)
    carry_flag = new_carry
    push(result)
    logger.debug(f"Rotate right carry: {val} -> {result}, carry={carry_flag}")

def mask_left(bits):
    """Mask the leftmost 'bits' of X (MASKL, page 59)."""
    val = int(pop())
    mask = ((1 << bits) - 1) << (current_word_size - bits)
    result = val & mask
    push(result)
    logger.debug(f"Mask left {bits} bits: {val} -> {result}")

def mask_right(bits):
    """Mask the rightmost 'bits' of X (MASKR, page 59)."""
    val = int(pop())
    mask = (1 << bits) - 1
    result = val & mask
    push(result)
    logger.debug(f"Mask right {bits} bits: {val} -> {result}")

def count_bits():
    """Count 1 bits in X (#B, page 55)."""
    val = int(pop())
    count = bin(val & ((1 << current_word_size) - 1)).count("1")
    push(count)
    logger.debug(f"Count bits in {val} -> {count}")

def set_bit(bit_index):
    """Set bit 'bit_index' in X to 1 (SB, page 51)."""
    val = int(pop())
    if not 0 <= bit_index < current_word_size:
        raise ValueError(f"Bit index {bit_index} out of range")
    result = val | (1 << bit_index)
    push(apply_word_size(result))
    logger.debug(f"Set bit {bit_index}: {val} -> {result}")

def clear_bit(bit_index):
    """Clear bit 'bit_index' in X to 0 (CB, page 51)."""
    val = int(pop())
    if not 0 <= bit_index < current_word_size:
        raise ValueError(f"Bit index {bit_index} out of range")
    result = val & ~(1 << bit_index)
    push(apply_word_size(result))
    logger.debug(f"Clear bit {bit_index}: {val} -> {result}")

def test_bit(bit_index):
    """Test if bit 'bit_index' in X is 1, set carry flag (B?, page 52)."""
    global carry_flag
    val = int(pop())
    if not 0 <= bit_index < current_word_size:
        raise ValueError(f"Bit index {bit_index} out of range")
    carry_flag = bool(val & (1 << bit_index))
    push(val)  # X unchanged
    logger.debug(f"Test bit {bit_index} in {val}, carry={carry_flag}")

def left_justify():
    """Shift X left until leftmost bit is 1 (LJ, page 58)."""
    global carry_flag
    val = int(pop())
    mask = (1 << current_word_size) - 1
    if val == 0:
        push(0)
        carry_flag = False
        return
    while not (val & (1 << (current_word_size - 1))):
        carry_flag = bool(val & (1 << (current_word_size - 1)))
        val = (val << 1) & mask
    push(val)
    logger.debug(f"Left justify: {val}")

def absolute():
    """Return absolute value of X (ABS, page 52)."""
    val = int(pop())
    result = abs(val)
    push(apply_word_size(result))
    logger.debug(f"Absolute: {val} -> {result}")

# Double Precision (pages 60-62)
def double_multiply():
    """Multiply X and Y, return double-word result in Y:X (DBL×)."""
    x = int(pop())
    y = int(pop())
    result = x * y
    mask = (1 << current_word_size) - 1
    low_word = apply_word_size(result & mask)
    high_word = apply_word_size(result >> current_word_size)
    push(high_word)  # Y
    push(low_word)  # X
    logger.debug(f"Double multiply: {y} * {x} = {high_word}:{low_word}")

def double_divide():
    """Divide Y:X by Z, return quotient in X, remainder in Y (DBL÷)."""
    x = int(pop())  # Divisor
    y = int(pop())  # Low word
    z = int(pop())  # High word
    dividend = (z << current_word_size) | y
    if x == 0:
        raise InvalidOperandError()
    quotient = dividend // x
    remainder = dividend % x
    push(apply_word_size(remainder))  # Y
    push(apply_word_size(quotient))   # X
    logger.debug(f"Double divide: {z}:{y} / {x} = {quotient}, rem={remainder}")

def double_remainder():
    """Return remainder of Y:X divided by Z in X (DBLR)."""
    x = int(pop())  # Divisor
    y = int(pop())  # Low word
    z = int(pop())  # High word
    dividend = (z << current_word_size) | y
    if x == 0:
        raise InvalidOperandError()
    remainder = dividend % x
    push(apply_word_size(remainder))
    logger.debug(f"Double remainder: {z}:{y} % {x} = {remainder}")

# Flag Operations (pages 49-50)
def set_flag(flag_type):
    """Set carry or overflow flag (SF, page 50)."""
    global carry_flag, overflow_flag
    if flag_type == "CF":
        carry_flag = True
    elif flag_type == "OF":
        overflow_flag = True
    logger.debug(f"Set flag {flag_type}")

def clear_flag(flag_type):
    """Clear carry or overflow flag (CF, page 50)."""
    global carry_flag, overflow_flag
    if flag_type == "CF":
        carry_flag = False
    elif flag_type == "OF":
        overflow_flag = False
    logger.debug(f"Cleared flag {flag_type}")

def test_flag(flag_type):
    """Test carry or overflow flag state (F?, page 50)."""
    if flag_type == "CF":
        return carry_flag
    elif flag_type == "OF":
        return overflow_flag
    logger.debug(f"Test flag {flag_type} = {carry_flag if flag_type == 'CF' else overflow_flag}")

def get_carry_flag():
    """Return carry flag state (page 49)."""
    return carry_flag

def get_overflow_flag():
    """Return overflow flag state (page 50)."""
    return overflow_flag