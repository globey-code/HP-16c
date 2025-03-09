from stack import stack, push, pop, apply_word_size
from normal_state_function import display  # reuse existing global display
from word_size import set_word_size_from_input, ALLOWED_WORD_SIZES
from error import show_error

def f_action(button, display_widget):
    top_text = button.get("orig_top_text", "").replace("\n", "").strip()
    print("f action triggered for button with top label:", top_text)
    
    if top_text == "SL":
        action_sl(display_widget)
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

def action_sl(display_widget):
    """Shift the top stack value left by one bit."""
    
    global stack  # Ensure we're using the correct stack reference

    print(f"[DEBUG] Before SL - Stack Reference ID: {id(stack)}, Contents: {stack}")

    # Stack Underflow Check
    if len(stack) == 0 or stack[0] == 0.0:
        show_error(display_widget, "E101")  # Stack Underflow Error
        return

    value = stack[0]  # Get top of stack (T)

    # Convert whole-number floats to integers
    if isinstance(value, float) and value.is_integer():
        value = int(value)

    # Invalid Operand Check (Only integers can be shifted)
    if not isinstance(value, int):
        show_error(display_widget, "E102")  # Invalid Operand Error
        return

    # Perform Shift Left
    result = value << 1
    result = apply_word_size(result)  # Apply word-size limit

    # Update stack correctly
    pop()  # Remove old top
    push(result)  # Push new top

    # Update Display
    display_widget.set_entry(str(result))

    print(f"[DEBUG] After SL - Stack Reference ID: {id(stack)}, Contents: {stack}")
    print(f"Shift Left executed: {value} << 1 = {result}")


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
    # Add custom logic here as needed.

def action_wsize():
    """Set the word size using the current display entry.
    This emulates the real HP-16C: you enter the word size (e.g., '16'),
    press the yellow f key to enter f-mode, and then press the WSIZE key.
    If the input is invalid, the word size label is updated with the allowed sizes.
    """
    from normal_state_function import get_display
    disp = get_display()
    if disp:
        input_value = disp.raw_value  # The raw value holds what the user entered.
        new_size = set_word_size_from_input(input_value)
        if new_size is not None:
            print(f"Word size set to {new_size} bits.")
            disp.word_size_label.config(text=f"WS: {new_size} bits")
            disp.clear_entry()
        else:
            valid_sizes = ', '.join(map(str, ALLOWED_WORD_SIZES))
            error_message = f"Invalid WS! Must be one of: {valid_sizes}"
            print(error_message)
            disp.word_size_label.config(text=error_message)
    else:
        print("Display not found in action_wsize().")
