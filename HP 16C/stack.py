# stack.py
#
# Module to handle stack-based operations for the HP 16C emulator, including word-size
# and two's complement logic.
#
# The HP 16C uses a four-level stack. The top of the stack is at index 0.
# When a new value is pushed, the existing values are shifted down (with the bottom value dropped).
# Arithmetic operations pop the top two values, perform the operation, then push the result.
#
# This version also logs every stack change to a file named stack_log.txt and
# applies two's complement masking based on a user-configurable word size.


from arithmetic import add, subtract, multiply, divide

# Initialize a four-level stack (T, Z, Y, X)
stack = [0.0, 0.0, 0.0, 0.0]

# Default word size (1..64). The real HP 16C typically defaults to 16 bits.
current_word_size = 16

# Append the current stack state to stack_log.txt, along with an optional action label.
def log_stack_to_file(action=""):    
    with open("stack_log.txt", "a") as f:
        f.write(f"[{action}] Stack state: {stack}\n")

# Set the global word size for two's complement operations (1..64).
def set_word_size(bits):
    global current_word_size
    if bits < 1 or bits > 64:
        raise ValueError("Word size must be between 1 and 64 bits.")
    current_word_size = bits
    print(f"Word size set to {bits} bits.")

# Return the current word size.
def get_word_size():
    return current_word_size

# Apply the current word size to 'value':
# 1) Mask off bits above current_word_size.
# 2) Interpret as signed if the sign bit is set (two's complement).
def apply_word_size(value):
    # If value is a float with a fractional part, return it unchanged.
    # (The two's complement logic is only meaningful for whole numbers.)
    if isinstance(value, float) and not value.is_integer():
        return value

    # Otherwise, for whole numbers, apply word-size masking.
    value = int(value)
    mask = (1 << current_word_size) - 1
    value &= mask
    sign_bit = 1 << (current_word_size - 1)
    if value & sign_bit:
        value -= (1 << current_word_size)
    return value

# Push a new value onto the stack, applying word-size and two's complement rules.
# The new value goes to T; T->Z, Z->Y, Y->X, X is dropped off.
def push(value):
    """Push a value onto the stack and shift the rest down."""
    global stack
    value = apply_word_size(value)  # Apply word-size limit
    stack[:] = [value] + stack[:-1]  # Keep reference while shifting
    print(f"[DEBUG] Pushed value: {value}. New stack state: {stack}")




# Pop the top value (T) from the stack and return it.
# After popping, Z->T, Y->Z, X->Y, and a 0.0 is appended at X.
def pop():
    """Removes and returns the top value of the stack, shifting the rest up."""
    global stack
    if not stack:
        return 0
    top_val = stack[0]
    stack[:] = stack[1:] + [0.0]  # Maintain reference while shifting
    print(f"[DEBUG] Popped value: {top_val}. New stack state: {stack}")
    return top_val



def get_state():
    # Return a copy of the stack to prevent accidental modification.
    return stack.copy()

# Return the top value of the stack (T) without removing it.
def peek():
    return stack[0]

# Clear the stack by setting all values to 0.0.
def clear_stack():
    global stack
    stack = [0.0, 0.0, 0.0, 0.0]
    log_stack_to_file("CLEAR")

# Perform an arithmetic operation using the top two values of the stack.
# The operation is performed as: second_operand operator top_operand.
#
# Supported operators: '+', '-', '*', '/'
#
# - Pop the top value (T) -> top_value
# - Pop the second value (T) -> second_value
# - Perform second_value operator top_value
# - Apply word-size logic
# - Push the result back onto the stack
# - Return the final result

def perform_operation(operator):
    top_value = pop()        # was T
    second_value = pop()     # was Z after the first pop

    # Convert them to integers if they're floats.
    top_value = int(top_value)
    second_value = int(second_value)

    if operator == "+":
        result = add(second_value, top_value)
    elif operator == "-":
        result = subtract(second_value, top_value)
    elif operator == "*":
        result = multiply(second_value, top_value)
    elif operator == "/":
        try:
            result = divide(second_value, top_value)
        except ZeroDivisionError:
            print("Division by zero encountered. Result set to 0.")
            result = 0
    else:
        raise ValueError(f"Unsupported operator: {operator}")

    # Apply word-size logic to the result before pushing
    result = apply_word_size(result)

    push(result)
    log_stack_to_file(f"OPERATOR {operator}")
    return result

# Duplicate the top value of the stack (T -> T, Z->T, Y->Z, X->Y).
def duplicate():
    push(peek())

# Swap the top two values of the stack (T <-> Z).
def swap():
    global stack
    if len(stack) >= 2:
        stack[0], stack[1] = stack[1], stack[0]
        log_stack_to_file("SWAP")

# Roll the stack up (T -> X, Z -> T, Y -> Z, X -> Y).
def roll():
    global stack
    stack = [stack[-1]] + stack[:-1]
    log_stack_to_file("ROLL")

# Print the current contents of the stack in a formatted manner.
# T is the top of the stack, X is the bottom.
def print_stack():
    print("Current stack:")
    for i, value in enumerate(stack):
        print(f"R{i}: {value}")
