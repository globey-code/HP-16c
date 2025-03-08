import stack
from normal_state_function import display  # reuse existing global display
from word_size import set_word_size_from_input

def f_action(button):
    top_text = button.get("orig_top_text", "").replace("\n", "").strip()
    print("f action triggered for button with top label:", top_text)
    
    if top_text == "SL":
        action_sl()
    elif top_text == "x><(i)":
        action_x_exchange_i()
    elif top_text == "(i)":
        action_i()
    elif top_text == "SR":
        action_sr()
    elif top_text in {"WS", "WSIZE"}:
        action_wsize()
    else:
        print("No f function defined for top label:", top_text)

def action_sl():
    """Shift the top stack value left by one bit."""
    value = stack.pop()
    result = value << 1
    stack.push(result)
    display.set_entry(str(result))
    print("Shift Left executed:", result)

def action_sr():
    """Shift the top stack value right by one bit."""
    value = stack.pop()
    result = value >> 1
    stack.push(result)
    display.set_entry(str(result))
    print("Shift Right executed:", result)

def action_x_exchange_i():
    """Exchange the contents of X (R0) with a predefined index register (for example R1)."""
    stack.swap()  # assuming swap() swaps R0 and R1
    top_val = stack.peek()
    display.set_entry(str(top_val))
    print("Exchange X with I executed:", top_val)

def action_i():
    """Perform a specific action related to (i). You can define this explicitly."""
    print("Executing (i) specific function.")
    # Add custom logic here.

def action_wsize():
    """Set the word size using the current display entry.
    This emulates the real HP-16C: you enter the word size (e.g., '16'),
    press the yellow f key to enter f-mode, and then press the WSIZE key.
    """
    from normal_state_function import get_display
    disp = get_display()
    if disp:
        input_value = disp.raw_value  # The raw value holds what the user entered.
        new_size = set_word_size_from_input(input_value)
        if new_size is not None:
            print(f"Word size set to {new_size} bits.")
            # Update the status area (we assume display.stack_label is used for status).
            disp.stack_label.config(text=f"Word Size: {new_size} bits")
            # Optionally clear the display after setting the word size.
            disp.clear_entry()
        else:
            print("Failed to set word size: invalid input.")
    else:
        print("Display not found in action_wsize().")
