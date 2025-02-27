# arithmetic.py
"""
arithmetic.py
--------------
Provides arithmetic operations for the HP 16C emulator.
These functions perform basic arithmetic and handle any necessary error checking.
"""

def add(a, b):
    """Return the sum of a and b."""
    return a + b

def subtract(a, b):
    """Return the result of b - a."""
    return b - a

def multiply(a, b):
    """Return the product of a and b."""
    return a * b

def divide(a, b):
    """
    Return the result of b / a.
    Raises ZeroDivisionError if a is zero.
    """
    if a == 0:
        raise ZeroDivisionError("Division by zero")
    return b / a
