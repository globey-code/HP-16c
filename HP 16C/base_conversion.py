#base_conversion.py
#
# Module for handling conversions between HEX, DEC, OCT, and BIN.
#
# Provides functions to interpret a string as a number in a given base,
# format a number as a string in a given base, switch the current base,
# and convert values between bases.


# Global variable to track the current base mode.
current_base = "DEC"

# Convert the provided string_value from the specified base into a number.
# If no base is provided, uses the global current_base.
def interpret_in_current_base(string_value, base=None):
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

# Format the given numeric value as a string in the specified base.
# If no base is provided, uses the global current_base.
def format_in_current_base(value, base=None):
    if base is None:
        base = current_base
    if base == "DEC":
        # Use a format specifier to show many decimal places:
        return f"{value:.12g}"  # This shows up to 12 significant digits.
    elif base == "HEX":
        return hex(int(value))[2:].upper()
    elif base == "BIN":
        return bin(int(value))[2:]
    elif base == "OCT":
        return oct(int(value))[2:]
    else:
        return str(value)

# Change the global base mode to new_base.
#    
# Reads the current display content (using the old base),
# converts it to a number, then reformats and updates the display in the new base.
#   
# Parameters:
# new_base: The new base mode ("DEC", "HEX", "BIN", "OCT").
# display_text: The Tkinter Text widget to update.
def set_base(new_base, display):
    global current_base
    content = display.get_entry().strip() if display.get_entry() else ""
    if content:
        try:
            old_val = interpret_in_current_base(content, current_base)
        except ValueError:
            display.set_entry("ERROR")
            return
        current_base = new_base
        new_str = format_in_current_base(old_val, new_base)
        display.set_entry(new_str)
        display.set_mode(new_base)  # Update the mode indicator.
    else:
        current_base = new_base
        display.set_mode(new_base)


# Convert a given value from one base to another.
#    
# Parameters:
# value: The number to convert (either as a string or numeric type).
# from_base: The base of the input value ("DEC", "HEX", "OCT", or "BIN").
# to_base: The target base to convert to.
#    
# Returns:
# The converted value as a string.
def convert_value(value, from_base, to_base):
    # If value is provided as a string, interpret it first.
    if isinstance(value, str):
        number = interpret_in_current_base(value, from_base)
    else:
        number = value
    return format_in_current_base(number, to_base)
