"""
program.py
Manages program execution for the HP-16C emulator, including instruction parsing and subroutine handling.
Author: GlobeyCode
License: MIT
Created: 3/23/2025
Last Modified: 4/06/2025
Dependencies: Python 3.6+, error
"""

from logging_config import logger
from error import (
    HP16CError, IncorrectWordSizeError, NoValueToShiftError, 
    ShiftExceedsWordSizeError, InvalidBitOperationError, 
    StackUnderflowError, DivisionByZeroError, InvalidOperandError
)

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
    """Execute the program instructions stored in program_memory."""
    global current_line
    instr = program_memory[current_line]
    increment = True

    if instr.isdigit():
        stack.push(int(instr))  # Push decimal digits (0-9)
    elif instr in "ABCDEF":
        stack.push(int(instr, 16))  # Push hexadecimal letters (A-F as 10-15)
    elif instr in {"+", "-", "×", "÷"}:
        y = stack.pop()
        x = stack.pop()
        if instr == "+":
            result = x + y
        elif instr == "-":
            result = x - y
        elif instr == "×":
            result = x * y
        elif instr == "÷":
            if y == 0:
                raise HP16CError("Division by zero", "E02")
            result = x // y  # Integer division for HP-16C
        stack.push(result)
    elif instr == "ENTER":
        stack.stack_lift()
    elif instr in {"HEX", "DEC", "OCT", "BIN"}:
        # Execute base change by setting stack mode (no UI update)
        stack.current_mode = "DEC" if instr == "DEC" else instr  # Default to DEC for consistency
        logger.info(f"Program mode: Set stack base to {stack.current_mode}")
    elif instr.startswith("LBL "):
        pass  # Skip label during execution
    elif instr.startswith("GSB "):
        label = instr.split()[1]
        if label in labels:
            return_stack.append(current_line + 1)
            current_line = labels[label]
            increment = False
        else:
            raise HP16CError(f"Label {label} not found", "E04")
    elif instr == "RTN":
        if return_stack:
            current_line = return_stack.pop()
            increment = False
        else:
            current_line = len(program_memory)  # End program
            increment = False

    return increment