# base_conversion.py
# Handles base conversion for the HP-16C emulator (DEC, HEX, BIN, OCT).
# Author: GlobeyCode
# License: MIT
# Date: 3/23/2025
# Dependencies: Python 3.6+, HP-16C emulator modules (stack)

import stack
from logging_config import logger

def interpret_in_base(string_value, base):
    # Handle empty input case
    if not string_value:
        return 0.0 if base == "FLOAT" else 0
    
    try:
        # FLOAT mode: convert directly to float
        if base == "FLOAT":
            result = float(string_value)
        # DEC mode: handle integers with complement logic
        elif base == "DEC":
            val = int(string_value)
            complement_mode = stack.get_complement_mode()
            word_size = stack.get_word_size()
            mask = (1 << word_size) - 1
            if complement_mode == "UNSIGNED":
                if val < 0:
                    raise ValueError("Negative numbers not allowed in unsigned mode")
                result = val & mask
            elif complement_mode == "1S":
                if val < 0:
                    magnitude = -val
                    result = (~magnitude) & mask
                else:
                    result = val & mask
            else:  # 2S (Two's complement)
                if val < 0:
                    result = (1 << word_size) + val
                    result &= mask
                else:
                    result = val & mask
        # HEX mode: interpret as hexadecimal
        elif base == "HEX":
            result = int(string_value, 16)
        # BIN mode: interpret as binary
        elif base == "BIN":
            result = int(string_value, 2)
        # OCT mode: interpret as octal
        elif base == "OCT":
            result = int(string_value, 8)
        # Default case: treat as decimal
        else:
            result = int(string_value)
        return result
    except ValueError:
        # Log error and return appropriate default value
        logger.info(f"Failed to interpret {string_value} in {base}, defaulting to 0")
        return 0.0 if base == "FLOAT" else 0

def format_in_current_base(value, base, pad=False):
    # Handle FLOAT mode
    if base == "FLOAT":
        if isinstance(value, (int, float)):
            result = f"{float(value):.9f}".rstrip('0').rstrip('.')
            if result == '':
                result = '0'
        else:
            result = '0'
        return result
    
    # Original logic for integer bases
    value = int(value)
    word_size = stack.get_word_size()
    mask = (1 << word_size) - 1
    value = value & mask

    # Use Flag 3 to control leading zeros, overridden by explicit pad=True
    display_leading_zeros = stack.test_flag(3) or pad

    if base == "BIN":
        if display_leading_zeros:
            result = format(value, f'0{word_size}b')
        else:
            result = format(value, 'b') if value != 0 else '0'
    elif base == "OCT":
        if display_leading_zeros:
            oct_digits = (word_size + 2) // 3
            result = format(value, f'0{oct_digits}o')
        else:
            result = format(value, 'o') if value != 0 else '0'
    elif base == "DEC":
        complement_mode = stack.get_complement_mode()
        if complement_mode in {"1S", "2S"} and value & (1 << (word_size - 1)):
            if complement_mode == "1S":
                signed_val = -((~value) & mask)
            else:  # 2S
                signed_val = value - (1 << word_size)
            result = str(signed_val)
        else:
            result = str(value)
    elif base == "HEX":
        if display_leading_zeros:
            hex_digits = (word_size + 3) // 4
            hex_str = format(value, f'0{hex_digits}x')
        else:
            hex_str = format(value, 'x') if value != 0 else '0'
        mapping = {'a': 'A', 'c': 'C', 'e': 'E', 'f': 'F'}
        result = ''.join(mapping.get(c, c) for c in hex_str)
    else:
        result = str(value)
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