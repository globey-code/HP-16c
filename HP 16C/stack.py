"""
stack.py
---------
Module to handle stack-based operations for the HP 16C emulator.

The HP 16C uses a four-level stack. The top of the stack is at index 0.
When a new value is pushed, the existing values are shifted down (with the bottom value dropped).
Arithmetic operations will pop the top two values, perform the operation,
and then push the result back onto the stack.

This version also logs every stack change to a file named stack_log.txt.
"""

from arithmetic import add, subtract, multiply, divide

# Initialize a four-level stack (R0, R1, R2, R3)
stack = [0.0, 0.0, 0.0, 0.0]

def log_stack_to_file(action=""):
    """
    Append the current stack state to stack_log.txt, along with an optional action label.
    This is called behind the scenes so the user doesn't see the stack in the UI.
    """
    with open("stack_log.txt", "a") as f:
        f.write(f"[{action}] Stack state: {stack}\n")

def push(value):
    """
    Push a new value onto the stack.
    The new value becomes the top of the stack. The existing values are shifted down,
    and the bottom element is dropped.
    Then log the new stack state.
    """
    global stack
    stack = [value] + stack[:-1]
    log_stack_to_file("PUSH")

def pop():
    """
    Pop the top value from the stack and return it.
    After popping, the remaining values shift up and a 0.0 is appended at the bottom.
    Then log the new stack state.
    """
    global stack
    top = stack[0]
    stack = stack[1:] + [0.0]
    log_stack_to_file("POP")
    return top

def peek():
    """
    Return the top value of the stack without removing it.
    """
    return stack[0]

def clear_stack():
    """
    Reset the stack to all zeros, then log the new state.
    """
    global stack
    stack = [0.0, 0.0, 0.0, 0.0]
    log_stack_to_file("CLEAR")

def perform_operation(operator):
    """
    Perform an arithmetic operation using the top two values of the stack.
    The operation is performed as: second_operand operator top_operand.

    Supported operators: '+', '-', '*', '/'

    The function pops the top two values, applies the operation, pushes the result back,
    and returns the result.

    Then log the final stack state after pushing the result.
    """
    a = pop()  # Top of the stack
    b = pop()  # Second operand
    result = 0.0

    if operator == "+":
        result = add(b, a)
    elif operator == "-":
        result = subtract(a, b)
    elif operator == "*":
        result = multiply(b, a)
    elif operator == "/":
        try:
            result = divide(a, b)
        except ZeroDivisionError:
            result = 0.0  # or handle division by zero differently
    else:
        raise ValueError(f"Unsupported operator: {operator}")

    push(result)
    log_stack_to_file(f"OPERATOR {operator}")
    return result

def duplicate():
    """
    Duplicate the top value of the stack.
    The duplicated value is pushed onto the stack, then log the stack state.
    """
    push(peek())
    # push() already logs

def swap():
    """
    Swap the top two values of the stack, then log the stack state.
    """
    global stack
    if len(stack) >= 2:
        stack[0], stack[1] = stack[1], stack[0]
        log_stack_to_file("SWAP")

def roll():
    """
    Roll the stack upward.
    The bottom element becomes the top element,
    and all other elements shift down by one, then log the stack state.
    """
    global stack
    stack = [stack[-1]] + stack[:-1]
    log_stack_to_file("ROLL")
