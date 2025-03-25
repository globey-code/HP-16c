# error.py
# Custom exceptions for the HP-16C emulator, raised by stack or arithmetic code and caught by the controller or UI.
# Author: GlobeyCode
# License: MIT
# Date: 3/23/2025
# Dependencies: Python 3.6+, HP-16C emulator modules (logging_config)

from logging_config import logger

class HP16CError(Exception):
    """Base exception class for HP-16C errors."""
    def __init__(self, message="Generic HP16C Error", error_code="E000", display=None):
        self.error_code = error_code
        self.message = message
        self.display = display  # Reference to display for UI access
        super().__init__(f"{self.error_code}: {self.message}")
        logger.info(f"Raising error: {self.display_message}")
        # Hide mode_label if display is provided and has mode_label
        if self.display and hasattr(self.display, 'mode_label'):
            self.display.mode_label.place_forget()  # Use place_forget() instead of grid_remove()

    @property
    def display_message(self):
        """Message formatted for display."""
        return f"ERROR {self.error_code}: {self.message}"

class StackUnderflowError(HP16CError):
    """Raised when stack has insufficient values."""
    def __init__(self, message="Stack Underflow - Operation requires more values in the stack.", error_code="E101", display=None):
        super().__init__(message, error_code, display)

class InvalidOperandError(HP16CError):
    """Raised when an operand is invalid for an operation."""
    def __init__(self, message="Invalid Operand - Operation cannot be performed on this type.", error_code="E102", display=None):
        super().__init__(message, error_code, display)

class DivisionByZeroError(HP16CError):
    """Raised when division by zero is attempted."""
    def __init__(self, message="Division by Zero", error_code="E103", display=None):
        super().__init__(message, error_code, display)

class IncorrectWordSizeError(HP16CError):
    """Raised when an invalid word size is set."""
    def __init__(self, message="Incorrect WORDSIZE", error_code="E104", display=None):
        super().__init__(message, error_code, display)

    @property
    def display_message(self):
        """Override display message for specific format."""
        return "Incorrect WORDSIZE"

class ShiftExceedsWordSizeError(HP16CError):
    """Raised when a shift exceeds the word size."""
    def __init__(self, message="Shift exceeds word size", error_code="E105", display=None):
        super().__init__(message, error_code, display)

    @property
    def display_message(self):
        """Override display message for specific format."""
        return "Shift exceeds word size"

class NoValueToShiftError(HP16CError):
    """Raised when there's no value to shift."""
    def __init__(self, message="No value to shift", error_code="E106", display=None):
        super().__init__(message, error_code, display)

    @property
    def display_message(self):
        """Override display message for specific format."""
        return "No value to shift"

class InvalidBitOperationError(HP16CError):
    """Raised when a bit operation is invalid."""
    def __init__(self, message="Invalid Bit Operation - Bit index or operation out of range.", error_code="E107", display=None):
        super().__init__(message, error_code, display)
    
    @property
    def display_message(self):
        """Override display message for specific format."""
        return "Invalid Bit Operation"