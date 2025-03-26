# arithmetic.py
# Provides integer-based arithmetic operations for the HP-16C emulator.
# Author: GlobeyCode
# License: MIT
# Date: 3/23/2025
# Dependencies: Python 3.6+, HP-16C emulator modules (stack, error)

import stack
from error import (
    HP16CError, IncorrectWordSizeError, NoValueToShiftError, 
    ShiftExceedsWordSizeError, InvalidBitOperationError, 
    StackUnderflowError, DivisionByZeroError, InvalidOperandError
)
from logging_config import logger

def to_signed(value, word_size, mode):
    mask = (1 << word_size) - 1
    value &= mask  # Ensure value is within word size

    if mode == "UNSIGNED":
        return value  # No conversion needed
    elif mode == "1S":
        if value == mask:
            return 0  # Negative zero in 1's complement (e.g., 0xFF = 0)
        elif value & (1 << (word_size - 1)):
            # Negative number: flip bits and negate
            return -((~value) & mask)
        else:
            return value  # Positive number
    else:  # "2S"
        if value & (1 << (word_size - 1)):
            # Negative number: subtract 2^word_size
            return value - (1 << word_size)
        else:
            return value  # Positive number

def from_signed(value, word_size, mode):
    mask = (1 << word_size) - 1

    if mode == "UNSIGNED":
        return value & mask
    elif mode == "1S":
        if value < 0:
            # Negative number: flip bits of absolute value
            return (~(-value)) & mask
        else:
            return value & mask  # Positive number
    else:  # "2S"
        if value < 0:
            # Negative number: add 2^word_size to wrap into unsigned range
            return (value + (1 << word_size)) & mask
        else:
            return value & mask  # Positive number

def add(a, b):
    mode = stack.get_complement_mode()
    word_size = stack.get_word_size()
    mask = (1 << word_size) - 1
    if mode == "UNSIGNED":
        result = (a + b) & mask
    else:
        a_signed = to_signed(a, word_size, mode)
        b_signed = to_signed(b, word_size, mode)
        result_signed = a_signed + b_signed
        result = from_signed(result_signed, word_size, mode)
        result &= mask
    logger.info(f"Add: {a} + {b} = {result} ({mode})")
    return result

def subtract(a, b):
    mode = stack.get_complement_mode()  # Get current mode: "UNSIGNED", "1S", or "2S"
    word_size = stack.get_word_size()   # Get current word size (e.g., 8, 16, 32, 64)
    mask = (1 << word_size) - 1         # Mask to keep results within word size (e.g., 0xFF for 8 bits)

    if mode == "UNSIGNED":
        # Simple subtraction with wrap-around
        result = (a - b) & mask
    else:
        # Convert operands to signed integers
        a_signed = to_signed(a, word_size, mode)
        b_signed = to_signed(b, word_size, mode)
        
        # Perform subtraction in signed arithmetic
        result_signed = a_signed - b_signed
        
        # Convert result back to unsigned representation
        result = from_signed(result_signed, word_size, mode)
        result &= mask  # Ensure result fits within word size

    logger.info(f"Subtract: {a} - {b} = {result} ({mode})")
    return result

def multiply(a, b):
    """Multiply two integers with word size consideration."""
    result = a * b
    result = stack.apply_word_size(result)
    logger.info(f"Multiply: {a} * {b} = {result}")
    return result

def divide(a, b):
    if b == 0:
        raise DivisionByZeroError()
    result = int(a / b)
    remainder = a % b
    stack._last_x = remainder  # Store remainder in last_x
    result = stack.apply_word_size(result)
    logger.info(f"Divide: {a} / {b} = {result}, remainder={remainder}")
    return result