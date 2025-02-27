"""
base_conversion.py
--------------------
Module for handling conversions between HEX, DEC, OCT, and BIN.

Provides functions to interpret a string as a number in a given base,
format a number as a string in a given base, switch the current base,
and convert values between bases.
"""

# Global variable to track the current base mode.
current_base = "DEC"

def interpret_in_current_base(string_value, base=None):
    """
    Convert the provided string_value from the specified base into a number.
    If no base is provided, uses the global current_base.
    """
    if base is None:
        base = current_base
    if not string_value:
        return 0
    try:
        if base == "DEC":
            # Interpret as a decimal (float) value.
            return float(string_value)
        elif base == "HEX":
            return int(string_value, 16)
        elif base == "BIN":
            return int(string_value, 2)
        elif base == "OCT":
            return int(string_value, 8)
        else:
            return float(string_value)
    except ValueError:
        raise ValueError(f"Invalid number for {base} base: {string_value}")

def format_in_current_base(value, base=None):
    """
    Format the given numeric value as a string in the specified base.
    If no base is provided, uses the global current_base.
    """
    if base is None:
        base = current_base
    if base == "DEC":
        return str(value)
    elif base == "HEX":
        return hex(int(value))[2:].upper()  # Remove the "0x" prefix and uppercase.
    elif base == "BIN":
        return bin(int(value))[2:]  # Remove the "0b" prefix.
    elif base == "OCT":
        return oct(int(value))[2:]  # Remove the "0o" prefix.
    else:
        return str(value)

def set_base(new_base, display_text):
    """
    Change the global base mode to new_base.
    
    Reads the current display content (using the old base),
    converts it to a number, then reformats and updates the display in the new base.
    
    Parameters:
      new_base: The new base mode ("DEC", "HEX", "BIN", "OCT").
      display_text: The Tkinter Text widget to update.
    """
    global current_base
    content = display_text.get("1.0", "end-1c").strip()
    if content:
        try:
            # Convert the current content using the old base.
            old_val = interpret_in_current_base(content, current_base)
        except ValueError:
            # Clear and display error if conversion fails.
            display_text.delete("1.0", "end")
            display_text.insert("end", "ERROR")
            return
        current_base = new_base
        new_str = format_in_current_base(old_val, new_base)
        display_text.delete("1.0", "end")
        display_text.insert("end", new_str)
    else:
        # If there's no content, simply update the base.
        current_base = new_base

def convert_value(value, from_base, to_base):
    """
    Convert a given value from one base to another.
    
    Parameters:
      value: The number to convert (either as a string or numeric type).
      from_base: The base of the input value ("DEC", "HEX", "OCT", or "BIN").
      to_base: The target base to convert to.
    
    Returns:
      The converted value as a string.
    """
    # If value is provided as a string, interpret it first.
    if isinstance(value, str):
        number = interpret_in_current_base(value, from_base)
    else:
        number = value
    return format_in_current_base(number, to_base)
