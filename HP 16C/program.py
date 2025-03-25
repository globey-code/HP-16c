# program.py

from error import HP16CError

program_memory = []
current_line = 0
labels = {}
return_stack = []

def load_program(instructions):
    """Load a program into memory and map labels to their line numbers."""
    global program_memory, labels
    program_memory = instructions
    labels.clear()
    for i, instr in enumerate(program_memory):
        if instr.startswith("LBL "):
            label = instr.split()[1]
            labels[label] = i

def execute(stack):
    global current_line
    instr = program_memory[current_line]
    increment = True  # Default to incrementing the program counter

    if instr.isdigit():
        stack.push(int(instr))
    elif instr == "/":
        y = stack._stack[0]
        x = stack._x_register
        if x == 0:
            raise HP16CError("Division by zero", "E02")
        result = y / x
        stack._x_register = result
        stack._stack[0] = stack._stack[1]
        stack._stack[1] = stack._stack[2]
    elif instr.startswith("GSB "):
        label = instr.split()[1]
        if label in labels:
            return_stack.append(current_line + 1)
            current_line = labels[label]
            increment = False  # GSB sets current_line directly
        else:
            raise HP16CError(f"Label {label} not found", "E04")
    elif instr == "RTN":
        if return_stack:
            current_line = return_stack.pop()
            increment = False  # RTN sets current_line directly
        else:
            current_line = len(program_memory)  # End of program
            increment = False
    # Add other instructions (e.g., +, -, *, x<>y, R↓) as needed

    return increment