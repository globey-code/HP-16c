﻿# stack.py
# Implements the stack for the HP-16C emulator, including push, pop, and various bit operations.
# Author: GlobeyCode
# License: MIT
# Date: 3/23/2025
# Dependencies: Python 3.6+, HP-16C emulator modules (arithmetic, error)

from arithmetic import add, subtract, multiply, divide
from error import (
    IncorrectWordSizeError, NoValueToShiftError, 
    InvalidBitOperationError, 
    StackUnderflowError, DivisionByZeroError, InvalidOperandError
)
from logging_config import logger
import logging
logger = logging.getLogger(__name__)

# Stack and register variables
_stack = [0, 0, 0]  # Y, Z, T
_x_register = 0     # X (display entry)
_word_size = 16
_complement_mode = "UNSIGNED"
_flags = {i: 0 for i in range(6)}  # Flags 0-5 initialized to 0
_last_x = 0
_i_register = 0
_data_registers = [0] * 10  # R0 to R9
_current_mode = "DEC"

logger.info(f"Stack initialized: {_stack}, X={_x_register}, word_size={_word_size}, complement_mode={_complement_mode}")

# --- Centralized Operation Handling ---

def perform_binary_operation(op):
    """Perform a binary operation using X and Y registers."""
    global _x_register, _stack
    if len(_stack) < 1 or _stack[0] == 0:
        raise StackUnderflowError("Insufficient stack values for binary operation")
    y = _stack[0]  # Y register
    x = _x_register  # X register
    if _current_mode == "FLOAT":
        if op == "+":
            result = float(y) + float(x)
        elif op == "-":
            result = float(y) - float(x)
        elif op == "*":
            result = float(y) * float(x)
        elif op == "/":
            if float(x) == 0:
                raise DivisionByZeroError("Division by zero")
            result = float(y) / float(x)
        elif op == "RMD":
            if float(x) == 0:
                raise DivisionByZeroError("Division by zero")
            result = float(y) % float(x)
        else:
            raise InvalidOperandError(f"Operation '{op}' not supported in FLOAT mode")
    else:
        # Integer mode operations
        if op == "+":
            result = add(y, x)
        elif op == "-":
            result = subtract(y, x)
        elif op == "*":
            result = multiply(y, x)
        elif op == "/":
            result = divide(y, x)
        elif op == "AND":
            mask = (1 << _word_size) - 1
            result = (y & x) & mask
        elif op == "OR":
            mask = (1 << _word_size) - 1
            result = (y | x) & mask
        elif op == "XOR":
            mask = (1 << _word_size) - 1
            result = (y ^ x) & mask
        elif op == "RMD":
            if x == 0:
                raise DivisionByZeroError("Division by zero")
            result = y % x
        else:
            raise InvalidOperandError(f"Operation '{op}' not supported in current mode")
    # Update stack: X = result, Y = Z, Z = T, T remains unchanged
    _x_register = result
    if len(_stack) >= 2:
        _stack[0] = _stack[1]  # Y = Z
        _stack[1] = _stack[2]  # Z = T
    logger.info(f"Performed binary {op}: result={result}, X={_x_register}, stack={_stack}")
    return result

def perform_unary_operation(op):
    """Perform a unary operation on the X register."""
    global _x_register
    x = _x_register
    if _current_mode == "FLOAT":
        if op == "NOT":
            raise InvalidOperandError("NOT not supported in FLOAT mode")
        # Add other unary operations if needed
        raise InvalidOperandError(f"Operation '{op}' not supported in FLOAT mode")
    else:
        # Integer mode operations
        if op == "NOT":
            mask = (1 << _word_size) - 1
            result = (~x) & mask
        else:
            raise InvalidOperandError(f"Operation '{op}' not supported in current mode")
    _x_register = result
    logger.info(f"Performed unary {op}: result={result}, X={_x_register}, stack={_stack}")
    return result

def perform_operation(op):
    """Perform the specified operation based on its type (binary or unary)."""
    op = op.upper()
    if op in {"+", "-", "*", "/", "AND", "OR", "XOR", "RMD"}:
        return perform_binary_operation(op)
    elif op == "NOT":
        return perform_unary_operation(op)
    else:
        raise ValueError(f"Unknown operator: {op}")

# --- Existing Functions (Unchanged Unless Noted) ---

def set_current_mode(mode):
    global _current_mode
    _current_mode = mode

def get_current_mode():
    return current_mode

def get_state():
    """Return a copy of the current stack plus X."""
    return [_x_register] + _stack.copy()

def push(value):
    """Push a value into X, shifting stack up: T=Z, Z=Y, Y=X, X=value."""
    global _x_register
    if isinstance(value, float) and not value.is_integer():
        value = int(value)
    if _complement_mode == "1S" and value < 0:
        value = (~(-value)) & ((1 << _word_size) - 1)
    elif _complement_mode == "2S" and value < 0:
        value = (1 << _word_size) + value
    value = value & ((1 << _word_size) - 1)
    
    _stack[2] = _stack[1]  # T = Z
    _stack[1] = _stack[0]  # Z = Y
    _stack[0] = _x_register  # Y = X
    _x_register = value    # X = new value
    logger.info(f"Pushed value: {value}, X={_x_register}, stack={_stack}")

def pop():
    """Pop X into last_x, shift stack down (Y→X, Z→Y, T→Z, 0→T)."""
    global _x_register, _last_x
    if _x_register == 0 and all(x == 0 for x in _stack):
        raise StackUnderflowError("Stack is empty")
    _last_x = _x_register
    _x_register = _stack.pop(0)  # Y → X
    _stack.append(0)            # 0 → T
    logger.info(f"Popped value: {_last_x}, X={_x_register}, stack={_stack}")
    return _last_x

def peek():
    """Return the current X value without popping."""
    return _x_register

def roll_down():
    """Roll down the stack: Y→X, Z→Y, T→Z, X→T"""
    global _x_register, _stack
    old_x = _x_register
    _x_register = _stack[0]  # Y moves to X
    _stack = [_stack[1], _stack[2], old_x]  # Z→Y, T→Z, X→T
    logger.info(f"Stack rolled down: X={_x_register}, stack={_stack}")

def shift_left():
    """Shift X left by 1 bit or multiply by 2 in float mode."""
    global _x_register
    if _current_mode == "FLOAT":
        if not isinstance(_x_register, (int, float)):
            raise InvalidOperandError("Invalid operand type for shift in FLOAT mode")
        _x_register = float(_x_register) * 2.0
        logger.info(f"Multiplied by 2 in FLOAT mode: X={_x_register}, stack={_stack}")
    else:
        if _x_register == 0 and all(x == 0 for x in _stack):
            raise NoValueToShiftError()
        mask = (1 << _word_size) - 1
        _x_register = (_x_register << 1) & mask
        logger.info(f"Shifted left: X={_x_register}, stack={_stack}")

def shift_right():
    """Shift X right by 1 bit."""
    global _x_register
    if _x_register == 0 and all(x == 0 for x in _stack):
        raise NoValueToShiftError()
    _x_register = (_x_register >> 1) & ((1 << _word_size) - 1)
    logger.info(f"Shifted right: X={_x_register}, stack={_stack}")

def rotate_left():
    """Rotate X left by 1 bit."""
    global _x_register
    if _x_register == 0 and all(x == 0 for x in _stack):
        raise NoValueToShiftError()
    _x_register = ((_x_register << 1) | (_x_register >> (_word_size - 1))) & ((1 << _word_size) - 1)
    logger.info(f"Rotated left: X={_x_register}, stack={_stack}")

def rotate_right():
    """Rotate X right by 1 bit."""
    global _x_register
    if _x_register == 0 and all(x == 0 for x in _stack):
        raise NoValueToShiftError()
    _x_register = ((_x_register >> 1) | (_x_register << (_word_size - 1))) & ((1 << _word_size) - 1)
    logger.info(f"Rotated right: X={_x_register}, stack={_stack}")

def rotate_left_carry():
    """Rotate X left with carry."""
    global _x_register
    if _x_register == 0 and all(x == 0 for x in _stack):
        raise NoValueToShiftError()
    carry = 1 if get_carry_flag() else 0
    result = ((_x_register << 1) | carry) & ((1 << _word_size) - 1)
    set_carry_flag(_x_register >> (_word_size - 1))
    _x_register = result
    logger.info(f"Rotated left with carry: X={_x_register}, carry={_flags['CF']}, stack={_stack}")

def rotate_right_carry():
    """Rotate X right with carry."""
    global _x_register
    if _x_register == 0 and all(x == 0 for x in _stack):
        raise NoValueToShiftError()
    carry = 1 if get_carry_flag() else 0
    result = ((_x_register >> 1) | (carry << (_word_size - 1))) & ((1 << _word_size) - 1)
    set_carry_flag(_x_register & 1)
    _x_register = result
    logger.info(f"Rotated right with carry: X={_x_register}, carry={_flags['CF']}, stack={_stack}")

def mask_left(bits):
    """Mask the leftmost bits of X."""
    global _x_register
    if bits < 0 or bits > _word_size:
        raise InvalidBitOperationError()
    mask = (((1 << (_word_size - bits)) - 1) << bits)
    _x_register = _x_register & mask
    logger.info(f"Masked left {bits} bits: X={_x_register}, stack={_stack}")

def mask_right(bits):
    """Mask the rightmost bits of X."""
    global _x_register
    if bits < 0 or bits > _word_size:
        raise InvalidBitOperationError()
    mask = (1 << bits) - 1
    _x_register = _x_register & mask
    logger.info(f"Masked right {bits} bits: X={_x_register}, stack={_stack}")

def count_bits():
    """Count the number of 1 bits in X."""
    global _x_register
    count = bin(_x_register).count("1")
    _x_register = count
    logger.info(f"Counted bits: X={_x_register}, stack={_stack}")

def set_bit(bit_index):
    """Set a specific bit in X."""
    global _x_register
    if bit_index < 0 or bit_index >= _word_size:
        raise InvalidBitOperationError()
    mask = 1 << bit_index
    _x_register = (_x_register | mask) & ((1 << _word_size) - 1)
    logger.info(f"Set bit {bit_index}: X={_x_register}, stack={_stack}")

def clear_bit(bit_index):
    """Clear a specific bit in X."""
    global _x_register
    if bit_index < 0 or bit_index >= _word_size:
        raise InvalidBitOperationError()
    mask = ~(1 << bit_index)
    _x_register = _x_register & mask & ((1 << _word_size) - 1)
    logger.info(f"Cleared bit {bit_index}: X={_x_register}, stack={_stack}")

def test_bit(bit_index):
    """Test if a specific bit is set in X."""
    if bit_index < 0 or bit_index >= _word_size:
        raise InvalidBitOperationError()
    return (_x_register >> bit_index) & 1

def absolute():
    """Set X to its absolute value."""
    global _x_register
    if _complement_mode == "UNSIGNED":
        result = _x_register
    elif _complement_mode == "1S":
        result = (~_x_register) & ((1 << _word_size) - 1) if _x_register & (1 << (_word_size - 1)) else _x_register
    else:  # "2S"
        result = (-_x_register) & ((1 << _word_size) - 1) if _x_register & (1 << (_word_size - 1)) else _x_register
    _x_register = result
    logger.info(f"Absolute value: X={_x_register}, stack={_stack}")

def double_multiply():
    """Multiply two double-word values (X and Y)."""
    if _x_register == 0 or _stack[0] == 0:
        raise StackUnderflowError("Double multiply requires two values")
    y = pop()
    x = pop()
    result = x * y
    push(result)
    logger.info(f"Double multiply: {x} * {y} = {result}")

def double_divide():
    """Divide two double-word values (X by Y)."""
    if _x_register == 0 or _stack[0] == 0:
        raise StackUnderflowError("Double divide requires two values")
    y = pop()
    if y == 0:
        raise DivisionByZeroError("Division by zero")
    x = pop()
    result = int(x / y)
    push(result)
    logger.info(f"Double divide: {x} / {y} = {result}")

def double_remainder():
    """Compute remainder of two double-word values."""
    if _x_register == 0 or _stack[0] == 0:
        raise StackUnderflowError("Double remainder requires two values")
    y = pop()
    if y == 0:
        raise DivisionByZeroError("Division by zero")
    x = pop()
    result = x % y
    push(result)
    logger.info(f"Double remainder: {x} % {y} = {result}")
    return result

def set_flag(flag_num):
    if not isinstance(flag_num, int) or flag_num < 0 or flag_num > 5:
        raise ValueError(f"Invalid flag number: {flag_num}")
    _flags[flag_num] = 1

def clear_flag(flag_num):
    """Clear the specified flag (0-5)."""
    if not isinstance(flag_num, int) or flag_num < 0 or flag_num > 5:
        raise ValueError(f"Invalid flag number: {flag_num}")
    _flags[flag_num] = 0

def test_flag(flag_num):
    if not isinstance(flag_num, int) or flag_num < 0 or flag_num > 5:
        raise ValueError(f"Invalid flag number: {flag_num}")
    return _flags[flag_num]

def get_flags_bitfield():
    """Return a 4-bit integer representing flags 0-3."""
    return (_flags[0] |
            (_flags[1] << 1) |
            (_flags[2] << 2) |
            (_flags[3] << 3))

def set_word_size(size):
    """Set the word size (1-64 bits) and apply mask to stack and registers."""
    global _word_size, _x_register
    if not isinstance(size, int) or size < 1 or size > 64:
        raise IncorrectWordSizeError()
    old_size = _word_size
    _word_size = size
    mask = (1 << _word_size) - 1
    _x_register = _x_register & mask
    for i in range(len(_stack)):
        _stack[i] = _stack[i] & mask
    for i in range(len(_data_registers)):
        _data_registers[i] = _data_registers[i] & mask
    logger.info(f"Word size changed: {old_size} -> {_word_size}, X={_x_register}, stack={_stack}, registers={_data_registers}")

def get_word_size():
    """Get the current word size."""
    return _word_size

def apply_word_size(val):
    """Apply word size mask to a value."""
    try:
        if isinstance(val, float) and not val.is_integer():
            return val
        mask = (1 << _word_size) - 1
        return int(val) & mask
    except Exception:
        return val

def get_complement_mode():
    """Get the current complement mode."""
    return _complement_mode

def set_complement_mode(mode):
    """Set the complement mode."""
    global _complement_mode
    if mode not in {"UNSIGNED", "1S", "2S"}:
        raise ValueError(f"Invalid complement mode: {mode}")
    old_mode = _complement_mode
    _complement_mode = mode
    logger.info(f"Complement mode changed: {old_mode} -> {_complement_mode}")

def get_carry_flag():
    return _flags[4]

def set_carry_flag(flag):
    _flags[4] = 1 if flag else 0
    logger.info(f"Carry flag (Flag 4) set: {_flags[4]}")

def get_last_x():
    """Get the last X value."""
    global _last_x
    return _last_x

def save_last_x():
    """Save the current X as last X."""
    global _last_x
    _last_x = _x_register
    logger.info(f"Saved last X: {_last_x}")

def last_x():
    """Return the last X value."""
    return _last_x

def store_in_i():
    """Store X in the I register."""
    global _i_register
    _i_register = _x_register
    logger.info(f"Stored in I register: {_i_register}")

def get_i():
    """Get the value from the I register."""
    return _i_register

def recall_i():
    """Push the I register value into X."""
    push(_i_register)
    logger.info(f"Recalled I register: {_i_register}, X={_x_register}, stack={_stack}")

# --- g-mode functions ---

def roll_up():
    """Rotate stack upward: X→Y, Y→Z, Z→T, T→X."""
    global _x_register
    temp = _stack[2]
    _stack[2] = _stack[1]
    _stack[1] = _stack[0]
    _stack[0] = _x_register
    _x_register = temp
    logger.info(f"Stack rolled up: X={_x_register}, stack={_stack}")

def stack_lift():
    """Lift the stack: T = Z, Z = Y, Y = X, X remains unchanged."""
    global _stack, _x_register
    _stack[2] = _stack[1]  # T = Z
    _stack[1] = _stack[0]  # Z = Y
    _stack[0] = _x_register  # Y = X
    logger.info(f"Stack lifted: X={_x_register}, stack={_stack}")

def left_justify():
    global _x_register, _word_size
    mask = (1 << _word_size) - 1  # Mask to ensure value fits word size
    x = _x_register & mask        # Apply mask to X
    if x == 0:
        _x_register = _word_size  # If X is 0, set to word size (16)
    else:
        _x_register = _word_size - x.bit_length()  # Number of leading zeros

# --- New Functions for Data Storage Registers ---

def clear_registers():
    global _data_registers
    _data_registers = [0] * len(_data_registers)
    logger.info("Registers cleared")

def set_register(index, value):
    """Set the value of a storage register, applying the word size mask."""
    if 0 <= index < len(_data_registers):
        mask = (1 << _word_size) - 1  # Mask based on current word size
        _data_registers[index] = value & mask
        logger.info(f"Set register R{index} to {_data_registers[index]}")
    else:
        raise IndexError("Register index out of range")

def get_register(index):
    """Get the value of a storage register."""
    if 0 <= index < len(_data_registers):
        return _data_registers[index]
    else:
        raise IndexError("Register index out of range")