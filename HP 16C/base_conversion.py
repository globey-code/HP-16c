"""
base_conversion.py

Handles base conversion for the HP-16C emulator (DEC, HEX, BIN, OCT).
"""

import stack
from logging_config import logger

current_base = "DEC"

def interpret_in_current_base(string_value, base=None):
    """Interpret a string value in the specified or current base."""
    global current_base
    if base is None:
        base = current_base
    
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
            result = int(string_value)
        return result
    except ValueError:
        logger.info(f"Failed to interpret {string_value} in {base}, defaulting to 0")
        return 0

def format_in_current_base(value, base=None):
    """Format a value in the specified or current base."""
    global current_base
    if base is None:
        base = current_base
    
    value = int(value)  # Ensure integer for non-FLOAT modes
    word_size = stack.get_word_size()
    mask = (1 << word_size) - 1
    complement_mode = stack.get_complement_mode()

    if base == "DEC":
        if complement_mode in {"1S", "2S"} and value & (1 << (word_size - 1)):
            if complement_mode == "1S":
                signed_val = -((~value) & mask)
            else:  # 2S
                signed_val = value - (1 << word_size)
            result = str(signed_val)
        else:
            result = str(value & mask)
    elif base == "HEX":
        padding = max(0, (word_size + 3) // 4)
        result = format(value & mask, f'0{padding}X').lower()
    elif base == "BIN":
        result = format(value & mask, f'0{word_size}b')
    elif base == "OCT":
        padding = max(0, (word_size + 2) // 3)
        result = format(value & mask, f'0{padding}o')
    else:
        result = str(value & mask)
    
    logger.info(f"Formatted {value} in {base} as {result}")
    return result

def set_base(new_base, display):
    """Set the current base and update the display."""
    global current_base
    if hasattr(display, 'current_value') and display.current_value is not None:
        num = display.current_value
    else:
        if display.raw_value and display.raw_value != "0":
            num = interpret_in_current_base(display.raw_value, current_base)
            display.current_value = num
        else:
            num = 0
            display.current_value = 0
    
    current_base = new_base
    display.set_mode(new_base)
    display.raw_value = format_in_current_base(num, new_base)
    display.set_entry(num)
    logger.info(f"Base set to {new_base}")