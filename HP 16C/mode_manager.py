CURRENT_MODE = "DEC"

VALID_CHARS = {
    "BIN": {"0", "1"},
    "OCT": set("01234567"),
    "DEC": set("0123456789"),
    "HEX": set("0123456789ABCDEF"),
}

def set_mode(mode, display):
    global CURRENT_MODE
    CURRENT_MODE = mode
    display.set_mode(mode)
    print(f"Mode changed to: {mode}")

def is_input_allowed(char):
    global CURRENT_MODE
    return char.upper() in VALID_CHARS.get(CURRENT_MODE, set())
