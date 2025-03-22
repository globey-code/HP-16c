"""
base_conversion.py

Handles base conversion for the HP-16C emulator (DEC, HEX, BIN, OCT).
"""

import stack
from logging_config import logger

def interpret_in_base(string_value, base):
    """Interpret a string value in the specified base."""
    if not string_value:
        return 0
    
    try:
        if base == "DEC":
            result = int(string_value)
        elif base == "HEX":
            result = int(string_value, 16)
        elif base == "BIN":
            result = int(string_value, 2)
        elif base == "OCT":
            result = int(string_value, 8)
        else:
            result = int(string_value)  # Default to DEC
        return result
    except ValueError:
        logger.info(f"Failed to interpret {string_value} in {base}, defaulting to 0")
        return 0

def format_in_current_base(value, base):
    """Format a value in the specified base without unnecessary leading zeros."""
    value = int(value)  # Ensure integer for non-FLOAT modes
    word_size = stack.get_word_size()
    mask = (1 << word_size) - 1
    complement_mode = stack.get_complement_mode()

    if base == "BIN":
        result = format(value & mask, f'0{word_size}b')
    elif base == "OCT":
        result = format(value & mask, 'o')
    elif base == "DEC":
        if complement_mode in {"1S", "2S"} and value & (1 << (word_size - 1)):
            if complement_mode == "1S":
                signed_val = -((~value) & mask)
            else:  # 2S
                signed_val = value - (1 << word_size)
            result = str(signed_val)
        else:
            result = str(value & mask)
    elif base == "HEX":
        result = format(value & mask, 'x')
    else:
        result = str(value & mask)
    
    logger.info(f"Formatted {value} in {base} as {result}")
    return result

def set_base(new_base, display):
    """Set the display mode and update the display."""
    if hasattr(display, 'current_value') and display.current_value is not None:
        num = display.current_value
    else:
        if display.raw_value and display.raw_value != "0":
            num = interpret_in_base(display.raw_value, display.mode)  # Use current mode
            display.current_value = num
        else:
            num = 0
            display.current_value = 0
    
    display.set_mode(new_base)
    display.raw_value = format_in_current_base(num, new_base)
    display.set_entry(num)
    logger.info(f"Base set to {new_base}")