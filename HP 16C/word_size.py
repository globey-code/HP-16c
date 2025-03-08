# word_size.py

# Define the allowed word sizes.
ALLOWED_WORD_SIZES = [4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64]

from stack import set_word_size

def set_word_size_from_input(input_value):
    """
    Convert the given input string to an integer and update the stack's word size.
    Only allowed values from ALLOWED_WORD_SIZES are permitted.
    
    Parameters:
        input_value (str): The string from the display containing the desired word size.
    
    Returns:
        int or None: The new word size if valid; otherwise, None.
    """
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
