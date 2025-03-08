import stack
from normal_state_function import display  # reuse existing global display

def g_action(button):
    sub_text = button.get("orig_sub_text", "").strip()
    if not sub_text:
        print("G action: No sub-label defined; executing default behavior.")
        return

    print("G action triggered for button with bottom label:", sub_text)

    if sub_text == "LJ":
        action_lj()
    elif sub_text == "RTN":
        action_rtn()
    elif sub_text == "P/R":
        action_pr()
    else:
        print("No specific G function defined for bottom label:", sub_text)

# Example meaningful implementations:

def action_lj():
    """Left justify the top stack value."""
    value = stack.pop()
    # Example: Left justify might be shifting until the highest bit is set
    justified_value = left_justify(value)
    stack.push(justified_value)
    display.set_entry(str(justified_value))
    print("Left justify executed:", justified_value)

def left_justify(value):
    """Helper function to left justify binary representation."""
    word_size = stack.get_word_size()
    shift = 0
    while shift < word_size and (value & (1 << (word_size - 1))) == 0:
        value <<= 1
        shift += 1
    return value

def action_rtn():
    """Perform a return operation, which might pop a value from stack without displaying it."""
    returned_value = stack.pop()
    display.set_entry(f"RTN: {returned_value}")
    print("Return executed:", returned_value)

def action_pr():
    """Toggle program/run mode (placeholder action)."""
    # Implement a toggle state or display mode change
    print("Program/Run mode toggled.")
    display.set_entry("P/R Mode toggled")
