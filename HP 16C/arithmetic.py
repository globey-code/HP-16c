"""
arithmetic.py

Provides integer-based arithmetic for the HP16C. Raises custom exceptions on error.
"""

from error import DivisionByZeroError

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise DivisionByZeroError()
    return int(a / b)  # Truncate toward zero
