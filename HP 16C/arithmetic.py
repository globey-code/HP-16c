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
            return -((~value) & mask)
        else:
            return value  # Positive number
    else:  # "2S"
        if value & (1 << (word_size - 1)):
            return value - (1 << word_size)
        else:
            return value  # Positive number

def from_signed(value, word_size, mode):
    mask = (1 << word_size) - 1

    if mode == "UNSIGNED":
        return value & mask
    elif mode == "1S":
        if value < 0:
            return (~(-value)) & mask
        else:
            return value & mask  # Positive number
    else:  # "2S"
        if value < 0:
            return (value + (1 << word_size)) & mask
        else:
            return value & mask  # Positive number

def add(a, b):
    mode = stack.get_complement_mode()
    word_size = stack.get_word_size()
    mask = (1 << word_size) - 1
    max_signed = (1 << (word_size - 1)) - 1  # e.g., 32767 for 16-bit
    min_signed = -(1 << (word_size - 1))     # e.g., -32768 for 16-bit

    if mode == "UNSIGNED":
        unmasked_result = a + b
        result = unmasked_result & mask
        carry = 1 if unmasked_result > mask else 0
        overflow = carry
    else:
        a_signed = to_signed(a, word_size, mode)
        b_signed = to_signed(b, word_size, mode)
        result_signed = a_signed + b_signed
        overflow = result_signed > max_signed or result_signed < min_signed
        result = from_signed(result_signed, word_size, mode)
        carry = 0  # No carry in signed mode per real calculator

    # Set flags
    stack.set_flag(4) if carry else stack.clear_flag(4)  # Flag 4: Carry only in unsigned
    stack.set_flag(5) if overflow else stack.clear_flag(5)  # Flag 5: Overflow
    logger.info(f"Add: {a} + {b} = {result} ({mode}), carry={carry}, overflow={overflow}")
    return result

def subtract(a, b):
    mode = stack.get_complement_mode()
    word_size = stack.get_word_size()
    mask = (1 << word_size) - 1
    max_signed = (1 << (word_size - 1)) - 1  # e.g., 32767 for 16-bit
    min_signed = -(1 << (word_size - 1))     # e.g., -32768 for 16-bit

    if mode == "UNSIGNED":
        unmasked_result = a - b
        result = unmasked_result & mask
        borrow = 1 if a < b else 0
        overflow = borrow
    else:
        a_signed = to_signed(a, word_size, mode)
        b_signed = to_signed(b, word_size, mode)
        result_signed = a_signed - b_signed
        overflow = result_signed > max_signed or result_signed < min_signed
        result = from_signed(result_signed, word_size, mode)
        borrow = 0  # No borrow in signed mode per real calculator

    # Set flags
    stack.set_flag(4) if borrow else stack.clear_flag(4)  # Flag 4: Borrow only in unsigned
    stack.set_flag(5) if overflow else stack.clear_flag(5)  # Flag 5: Overflow
    logger.info(f"Subtract: {a} - {b} = {result} ({mode}), borrow={borrow}, overflow={overflow}")
    return result

def multiply(a, b):
    """Multiply two integers with word size consideration."""
    mode = stack.get_complement_mode()
    word_size = stack.get_word_size()
    mask = (1 << word_size) - 1
    max_signed = (1 << (word_size - 1)) - 1
    min_signed = -(1 << (word_size - 1))

    if mode == "UNSIGNED":
        unmasked_result = a * b
        result = unmasked_result & mask
    else:
        a_signed = to_signed(a, word_size, mode)
        b_signed = to_signed(b, word_size, mode)
        result_signed = a_signed * b_signed
        result = from_signed(result_signed, word_size, mode)

    # No flags set for multiplication overflow per real calculator
    stack.clear_flag(4)  # Flag 4: No carry
    stack.clear_flag(5)  # Flag 5: No overflow
    logger.info(f"Multiply: {a} * {b} = {result} ({mode})")
    return result

def divide(a, b):
    """Divide two integers with word size consideration."""
    if b == 0:
        raise DivisionByZeroError()
    
    mode = stack.get_complement_mode()
    word_size = stack.get_word_size()
    mask = (1 << word_size) - 1
    max_signed = (1 << (word_size - 1)) - 1
    min_signed = -(1 << (word_size - 1))

    if mode == "UNSIGNED":
        result = int(a / b)
        remainder = a % b
        overflow = 0
    else:
        a_signed = to_signed(a, word_size, mode)
        b_signed = to_signed(b, word_size, mode)
        result_signed = int(a_signed / b_signed)
        remainder = a_signed % b_signed
        overflow = result_signed > max_signed or result_signed < min_signed
        result = from_signed(result_signed, word_size, mode)

    # Apply word size and set flags
    result = stack.apply_word_size(result)
    stack._last_x = remainder
    stack.set_flag(4) if remainder != 0 else stack.clear_flag(4)  # Flag 4: Carry if remainder
    stack.set_flag(5) if overflow else stack.clear_flag(5)  # Flag 5: Overflow
    logger.info(f"Divide: {a} / {b} = {result} ({mode}), remainder={remainder}, overflow={overflow}")
    return result