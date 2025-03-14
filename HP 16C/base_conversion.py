"""
base_conversion.py

Handles base conversion for HP-16C emulator (DEC, HEX, BIN, OCT).
"""

current_base = "DEC"

def interpret_in_current_base(string_value, base=None):
    global current_base
    if base is None:
        base = current_base

    if not string_value:
        return 0

    try:
        if base == "DEC":
            return int(string_value)
        elif base == "HEX":
            return int(string_value, 16)
        elif base == "BIN":
            return int(string_value, 2)
        elif base == "OCT":
            return int(string_value, 8)
        else:
            return int(string_value)
    except ValueError:
        return 0

def format_in_current_base(value, base=None):
    """Format a value in the specified base, respecting word size (page 45)."""
    global current_base
    if base is None:
        base = current_base

    import stack
    value = int(value)  # Ensure integer for non-DEC modes

    if base == "DEC":
        from stack import current_complement_mode, current_word_size
        if current_complement_mode in {"1S", "2S"}:
            return str(value)
        else:
            mask = (1 << current_word_size) - 1
            unsigned_val = value & mask
            return str(unsigned_val)
    elif base == "HEX":
        word_size = stack.get_word_size()
        padding = max(0, (word_size + 3) // 4)
        return format(value & ((1 << word_size) - 1), f'0{padding}X')
    elif base == "BIN":
        word_size = stack.get_word_size()
        return format(value & ((1 << word_size) - 1), f'0{word_size}b')
    elif base == "OCT":
        word_size = stack.get_word_size()
        padding = max(0, (word_size + 2) // 3)
        return format(value & ((1 << word_size) - 1), f'0{padding}o')
    else:
        return str(value)

def set_base(new_base, display):
    """Switch the display mode and reformat the current value (page 17)."""
    global current_base
    if hasattr(display, 'current_value') and display.current_value is not None:
        num = display.current_value
        print(f"[DEBUG] Using display.current_value: {num}")
    else:
        if display.raw_value and display.raw_value != "0":
            print(f"[DEBUG] Using raw_value: '{display.raw_value}' with current base: {current_base}")
            num = interpret_in_current_base(display.raw_value, current_base)
            display.current_value = num
        else:
            print("[DEBUG] raw_value is '0' or empty; using 0")
            num = 0
            display.current_value = 0

    current_base = new_base
    display.set_mode(new_base)
    display.set_entry(num)  # Pass numeric value, not formatted string
    new_str = format_in_current_base(num, new_base)
    display.raw_value = new_str
    print(f"[base_conversion] Changed base to {new_base}. Now display shows '{new_str}'")