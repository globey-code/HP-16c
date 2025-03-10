"""
error.py

Custom exceptions for HP16C. Stack or arithmetic code raises these;
the controller/UI catches and displays/logs them.
"""

from logging_config import logger

class HP16CError(Exception):
    """Base class for all HP16C errors."""
    error_code = "E000"
    message = "Generic HP16C Error"

    def __init__(self):
        super().__init__(f"{self.error_code}: {self.message}")
        logger.warning(f"Raised {self.error_code}: {self.message}")

class StackUnderflowError(HP16CError):
    error_code = "E101"
    message = "Stack Underflow - Operation requires more values in the stack."

class InvalidOperandError(HP16CError):
    error_code = "E102"
    message = "Invalid Operand - Operation cannot be performed on this type."

class DivisionByZeroError(HP16CError):
    error_code = "E103"
    message = "Division by Zero - Cannot divide by zero."
