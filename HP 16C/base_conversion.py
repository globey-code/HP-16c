current_base = "DEC"

def interpret_in_current_base(string_value, base=None):
    global current_base
    if base is None:
        base = current_base

    if not string_value:
        return 0

    if base == "DEC":
        return float(string_value)
    elif base == "HEX":
        return int(string_value, 16)
    elif base == "BIN":
        return int(string_value, 2)
    elif base == "OCT":
        return int(string_value, 8)
    else:
        # fallback
        return float(string_value)

def format_in_current_base(value, base=None):
    global current_base
    if base is None:
        base = current_base

    # We'll handle the DEC logic separately, 
    # then handle HEX/BIN/OCT below
    if base == "DEC":
        # Import from stack to read complement mode
        from stack import current_complement_mode, current_word_size

        if current_complement_mode in {"1S", "2S"}:
            # show the signed decimal as-is
            return str(value)
        else:
            # UNSIGNED mode: mask off bits
            mask = (1 << current_word_size) - 1
            # Convert negative or large positive => 0..65535 etc.
            unsigned_val = value & mask
            return str(unsigned_val)

    elif base == "HEX":
        return hex(int(value))[2:].upper()
    elif base == "BIN":
        return bin(int(value))[2:]
    elif base == "OCT":
        return oct(int(value))[2:]
    else:
        # fallback
        return str(value)

def set_base(new_base, display):
    """
    Convert display.raw_value from old base -> numeric -> new base,
    then store & show that new string in display.
    """
    global current_base

    old_val_str = display.raw_value  # the old raw string in old base
    old_num = interpret_in_current_base(old_val_str, current_base)

    # Now switch to the new base
    current_base = new_base

    # Format old_num in the new base
    new_str = format_in_current_base(old_num, new_base)

    # Update the display
    display.raw_value = new_str
    display.set_entry(new_str)
    display.set_mode(new_base)

    print(f"[base_conversion] Changed base to {new_base}. Now display shows '{new_str}'")
