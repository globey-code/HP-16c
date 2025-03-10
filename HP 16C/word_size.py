"""
word_size.py

Handles setting the word size from user input, e.g. "16" -> set_word_size(16).
"""

from stack import set_word_size

ALLOWED_WORD_SIZES = [4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64]

def set_word_size_from_input(input_value):
    try:
        new_size = int(input_value)
    except ValueError:
        print("Invalid input for word size. Must be integer.")
        return None

    if new_size not in ALLOWED_WORD_SIZES:
        print(f"Word size must be one of {ALLOWED_WORD_SIZES}.")
        return None

    set_word_size(new_size)
    return new_size
