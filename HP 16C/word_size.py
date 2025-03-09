# word_size.py

ALLOWED_WORD_SIZES = [4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64]

from stack import set_word_size

def set_word_size_from_input(input_value):
    try:
        new_size = int(input_value)
    except ValueError:
        print("Invalid input for word size. Please enter an integer.")
        return None

    if new_size not in ALLOWED_WORD_SIZES:
        print(f"Word size must be one of {ALLOWED_WORD_SIZES}.")
        return None

    set_word_size(new_size)
    print(f"Word size set to {new_size} bits.")
    return new_size
