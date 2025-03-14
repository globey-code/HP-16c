"""
arithmetic.py

Provides integer-based arithmetic for the HP16C. Raises custom exceptions on error.
"""

from error import DivisionByZeroError

def add(a, b):
    result = a + b
    from stack import apply_word_size, current_base  # Lazy import to avoid circular import
    return result if current_base == "DEC" else apply_word_size(result)

def subtract(a, b):
    result = a - b
    from stack import apply_word_size, current_base
    return result if current_base == "DEC" else apply_word_size(result)

def multiply(a, b):
    result = a * b
    from stack import apply_word_size, current_base
    return result if current_base == "DEC" else apply_word_size(result)

def divide(a, b):
    if b == 0:
        from error import DivisionByZeroError
        raise DivisionByZeroError()
    result = int(a / b)  # Truncate toward zero
    from stack import apply_word_size, current_base
    return result if current_base == "DEC" else apply_word_size(result)
