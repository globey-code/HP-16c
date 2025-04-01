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
    mode = stack.get_current_mode()
    if mode == "FLOAT":
        result = a + b
        # Clear flags since carry and overflow are less relevant in float mode
        stack.clear_flag(4)  # Carry flag
        stack.clear_flag(5)  # Overflow flag (unless result is infinity)
        if isinstance(result, float) and (result == float('inf') or result == float('-inf')):
            stack.set_flag(5)  # Set overflow for infinity
        logger.info(f"Add (FLOAT): {a} + {b} = {result}")
        return result
    else:
        # Existing integer addition logic
        mode = stack.get_complement_mode()
        word_size = stack.get_word_size()
        mask = (1 << word_size) - 1
        max_signed = (1 << (word_size - 1)) - 1
        min_signed = -(1 << (word_size - 1))

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
            carry = 0

        stack.set_flag(4) if carry else stack.clear_flag(4)
        stack.set_flag(5) if overflow else stack.clear_flag(5)
        logger.info(f"Add: {a} + {b} = {result} ({mode}), carry={carry}, overflow={overflow}")
        return result

def subtract(a, b):
    mode = stack.get_current_mode()
    if mode == "FLOAT":
        result = a - b
        stack.clear_flag(4)  # Carry flag
        stack.clear_flag(5)  # Overflow flag
        if isinstance(result, float) and (result == float('inf') or result == float('-inf')):
            stack.set_flag(5)  # Set overflow for infinity
        logger.info(f"Subtract (FLOAT): {a} - {b} = {result}")
        return result
    else:
        # Existing integer subtraction logic
        mode = stack.get_complement_mode()
        word_size = stack.get_word_size()
        mask = (1 << word_size) - 1
        max_signed = (1 << (word_size - 1)) - 1
        min_signed = -(1 << (word_size - 1))

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
            borrow = 0

        stack.set_flag(4) if borrow else stack.clear_flag(4)
        stack.set_flag(5) if overflow else stack.clear_flag(5)
        logger.info(f"Subtract: {a} - {b} = {result} ({mode}), borrow={borrow}, overflow={overflow}")
        return result

def multiply(a, b):
    mode = stack.get_current_mode()
    if mode == "FLOAT":
        result = a * b
        stack.clear_flag(4)  # Carry flag
        stack.clear_flag(5)  # Overflow flag
        if isinstance(result, float) and (result == float('inf') or result == float('-inf')):
            stack.set_flag(5)  # Set overflow for infinity
        logger.info(f"Multiply (FLOAT): {a} * {b} = {result}")
        return result
    else:
        # Existing integer multiplication logic
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

        stack.clear_flag(4)
        stack.clear_flag(5)
        logger.info(f"Multiply: {a} * {b} = {result} ({mode})")
        return result

def divide(a, b):
    mode = stack.get_current_mode()
    if mode == "FLOAT":
        if b == 0:
            raise DivisionByZeroError()
        result = a / b
        stack.clear_flag(4)  # Carry flag (no remainder in float mode)
        stack.clear_flag(5)  # Overflow flag
        if isinstance(result, float) and (result == float('inf') or result == float('-inf')):
            stack.set_flag(5)  # Set overflow for infinity
        logger.info(f"Divide (FLOAT): {a} / {b} = {result}")
        return result
    else:
        # Existing integer division logic
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

        result = stack.apply_word_size(result)
        stack._last_x = remainder
        stack.set_flag(4) if remainder != 0 else stack.clear_flag(4)
        stack.set_flag(5) if overflow else stack.clear_flag(5)
        logger.info(f"Divide: {a} / {b} = {result} ({mode}), remainder={remainder}, overflow={overflow}")
        return result