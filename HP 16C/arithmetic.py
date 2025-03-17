"""
arithmetic.py

Provides integer-based arithmetic for the HP16C. Raises custom exceptions on error.
"""

from error import DivisionByZeroError
from base_conversion import current_base
import stack
from logging_config import logger

def add(a, b):
    """Add two integers with word size consideration."""
    result = a + b
    if current_base != "DEC":
        result = stack.apply_word_size(result)
    logger.info(f"Add: {a} + {b} = {result}")
    return result

def subtract(a, b):
    """Subtract two integers with word size consideration."""
    result = a - b
    if current_base != "DEC":
        result = stack.apply_word_size(result)
    logger.info(f"Subtract: {a} - {b} = {result}")
    return result

def multiply(a, b):
    """Multiply two integers with word size consideration."""
    result = a * b
    if current_base != "DEC":
        result = stack.apply_word_size(result)
    logger.info(f"Multiply: {a} * {b} = {result}")
    return result

def divide(a, b):
    """Divide two integers with word size consideration."""
    if b == 0:
        raise DivisionByZeroError()
    result = int(a / b)
    if current_base != "DEC":
        result = stack.apply_word_size(result)
    logger.info(f"Divide: {a} / {b} = {result}")
    return result