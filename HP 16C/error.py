"""
error.py

Custom exceptions for HP16C. Stack or arithmetic code raises these;
the controller/UI catches and displays/logs them.
"""

from logging_config import logger

class HP16CError(Exception):
    """Base class for all HP16C errors."""
    def __init__(self, message="Generic HP16C Error", error_code="E000"):
        self.error_code = error_code
        self.message = message
        super().__init__(f"{self.error_code}: {self.message}")
        logger.warning(f"Raised {self.error_code}: {self.message}")
        
    @property
    def display_message(self):
        """Return the message to display on the calculator."""
        return f"ERROR {self.error_code}: {self.message}"

class StackUnderflowError(HP16CError):
    def __init__(self, message="Stack Underflow - Operation requires more values in the stack.", error_code="E101"):
        super().__init__(message, error_code)

class InvalidOperandError(HP16CError):
    def __init__(self, message="Invalid Operand - Operation cannot be performed on this type.", error_code="E102"):
        super().__init__(message, error_code)

class DivisionByZeroError(HP16CError):
    def __init__(self, message="Division by Zero - Cannot divide by zero.", error_code="E103"):
        super().__init__(message, error_code)

class IncorrectWordSizeError(HP16CError):
    def __init__(self):
        super().__init__("Incorrect WSIZE", "E104")

    @property
    def display_message(self):
        return "Incorrect WSIZE"

class ShiftExceedsWordSizeError(HP16CError):
    def __init__(self):
        super().__init__("Shift exceeds word size", "E105")

    @property
    def display_message(self):
        return "Shift exceeds word size"

class NoValueToShiftError(HP16CError):
    def __init__(self):
        super().__init__("No value to shift", "E106")

    @property
    def display_message(self):
        return "No value to shift"

class InvalidBitOperationError(HP16CError):
    def __init__(self, message="Invalid Bit Operation - Bit index or operation out of range.", error_code="E107"):
        super().__init__(message, error_code)

    @property
    def display_message(self):
        return "Invalid Bit Operation"
