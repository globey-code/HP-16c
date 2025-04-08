"""
arithmetic.py
Provides integer-based arithmetic operations for the HP-16C emulator, supporting multiple complement modes.
Author: GlobeyCode
License: MIT
Created: 3/23/2025
Last Modified: 4/06/2025
Dependencies: Python 3.6+, stack, error, logging_config
"""

from typing import Union, Tuple
from stack import Stack, global_stack
from error import (
    HP16CError, IncorrectWordSizeError, NoValueToShiftError,
    DivisionByZeroError, InvalidOperandError
)
from logging_config import logger

Number = Union[int, float]

def to_signed(value: int, word_size: int, mode: str) -> int:
    mask = (1 << word_size) - 1
    value &= mask
    if mode == "UNSIGNED":
        return value
    elif mode == "1S":
        if value == mask:
            return 0
        elif value & (1 << (word_size - 1)):
            return -((~value) & mask)
        else:
            return value
    else:  # "2S"
        if value & (1 << (word_size - 1)):
            return value - (1 << word_size)
        else:
            return value

def from_signed(value: int, word_size: int, mode: str) -> int:
    mask = (1 << word_size) - 1
    if mode == "UNSIGNED":
        return value & mask
    elif mode == "1S":
        return (~(-value)) & mask if value < 0 else value & mask
    else:  # "2S"
        return (value + (1 << word_size)) & mask if value < 0 else value & mask

def add(a: int, b: int, stack: Stack = global_stack) -> Number:
    if stack.current_mode == "FLOAT":
        result: Number = a + b
        stack.clear_flag(4)  # Clear carry
        stack.clear_flag(5)  # Clear overflow/infinity
        if isinstance(result, float) and (result == float('inf') or result == float('-inf')):
            stack.set_flag(5)  # Set infinity flag
        logger.info(f"Add (FLOAT): {a} + {b} = {result}")
        return result
    else:
        if not (isinstance(a, int) and isinstance(b, int)):
            raise ValueError("Inputs must be integers in integer mode")
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

def subtract(a: int, b: int, stack: Stack = global_stack) -> Number:
    if stack.current_mode == "FLOAT":
        result: Number = a - b
        stack.clear_flag(4)
        stack.clear_flag(5)
        if isinstance(result, float) and (result == float('inf') or result == float('-inf')):
            stack.set_flag(5)
        logger.info(f"Subtract (FLOAT): {a} - {b} = {result}")
        return result
    else:
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
        if borrow:
            stack.set_flag(4)
        else:
            stack.clear_flag(4)
        if overflow:
            stack.set_flag(5)
        else:
            stack.clear_flag(5)
        logger.info(f"Subtract: {a} - {b} = {result} ({mode}), borrow={borrow}, overflow={overflow}")
        return result

def multiply(a: int, b: int, stack: Stack = global_stack) -> Number:
    if stack.current_mode == "FLOAT":
        result: Number = a * b
        stack.clear_flag(4)
        stack.clear_flag(5)
        if isinstance(result, float) and (result == float('inf') or result == float('-inf')):
            stack.set_flag(5)
        logger.info(f"Multiply (FLOAT): {a} * {b} = {result}")
        return result
    else:
        mode = stack.get_complement_mode()
        word_size = stack.get_word_size()
        mask = (1 << word_size) - 1
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

def divide(a: int, b: int, stack: Stack = global_stack) -> Number:
    if stack.current_mode == "FLOAT":
        if b == 0:
            raise DivisionByZeroError()
        result: Number = a / b
        stack.clear_flag(4)
        stack.clear_flag(5)
        if isinstance(result, float) and (result == float('inf') or result == float('-inf')):
            stack.set_flag(5)
        logger.info(f"Divide (FLOAT): {a} / {b} = {result}")
        return result
    else:
        if b == 0:
            raise DivisionByZeroError()
        mode = stack.get_complement_mode()
        word_size = stack.get_word_size()
        mask = (1 << word_size) - 1
        if mode == "UNSIGNED":
            result = int(a / b)
            remainder = a % b
            overflow = 0
        else:
            a_signed = to_signed(a, word_size, mode)
            b_signed = to_signed(b, word_size, mode)
            result_signed = int(a_signed / b_signed)
            remainder = a_signed % b_signed
            overflow = result_signed > ((1 << (word_size - 1)) - 1) or result_signed < -(1 << (word_size - 1))
            result = from_signed(result_signed, word_size, mode)
        result = result & mask
        # Store remainder in a manner similar to saving last_x
        global_stack._last_x = remainder  # or pass stack instance if needed
        if remainder != 0:
            stack.set_flag(4)
        else:
            stack.clear_flag(4)
        if overflow:
            stack.set_flag(5)
        else:
            stack.clear_flag(5)
        logger.info(f"Divide: {a} / {b} = {result} ({mode}), remainder={remainder}, overflow={overflow}")
        return result
