"""
error.py
Defines custom exception classes for error handling in the HP-16C emulator.
Author: GlobeyCode
License: MIT
Created: 3/23/2025
Last Modified: 4/06/2025
Dependencies: Python 3.6+, typing, logging_config
"""

from typing import Optional
from logging_config import logger

class HP16CError(Exception):
    def __init__(self, message: str = "Generic HP16C Error", error_code: str = "E000", display: Optional[object] = None) -> None:
        self.error_code = error_code
        self.message = message
        self.display = display
        super().__init__(f"{self.error_code}: {self.message}")
        logger.info(f"Raising error: {self.display_message}")
        if self.display and hasattr(self.display, 'mode_label'):
            self.display.mode_label.place_forget()

    @property
    def display_message(self) -> str:
        return f"ERROR {self.error_code}: {self.message}"

class StackUnderflowError(HP16CError):
    def __init__(self, message: str = "Stack Underflow - Operation requires more values in the stack.", error_code: str = "E101", display: Optional[object] = None) -> None:
        super().__init__(message, error_code, display)

class InvalidOperandError(HP16CError):
    def __init__(self, message: str = "Invalid Operand - Operation cannot be performed on this type.", error_code: str = "E102", display: Optional[object] = None) -> None:
        super().__init__(message, error_code, display)

class DivisionByZeroError(HP16CError):
    def __init__(self, message: str = "Division by Zero", error_code: str = "E103", display: Optional[object] = None) -> None:
        super().__init__(message, error_code, display)

class IncorrectWordSizeError(HP16CError):
    def __init__(self, message: str = "Incorrect WORDSIZE", error_code: str = "E104", display: Optional[object] = None) -> None:
        super().__init__(message, error_code, display)

    @property
    def display_message(self) -> str:
        return "Incorrect WORDSIZE"

class ShiftExceedsWordSizeError(HP16CError):
    def __init__(self, message: str = "Shift exceeds word size", error_code: str = "E105", display: Optional[object] = None) -> None:
        super().__init__(message, error_code, display)

    @property
    def display_message(self) -> str:
        return "Shift exceeds word size"

class NoValueToShiftError(HP16CError):
    def __init__(self, message: str = "No value to shift", error_code: str = "E106", display: Optional[object] = None) -> None:
        super().__init__(message, error_code, display)

    @property
    def display_message(self) -> str:
        return "No value to shift"

class InvalidBitOperationError(HP16CError):
    def __init__(self, message: str = "Invalid Bit Operation - Bit index or operation out of range.", error_code: str = "E107", display: Optional[object] = None) -> None:
        super().__init__(message, error_code, display)

    @property
    def display_message(self) -> str:
        return "Invalid Bit Operation"

class NegativeShiftCountError(HP16CError):
    def __init__(self, message: str = "Negative shift count not allowed", error_code: str = "E108", display: Optional[object] = None) -> None:
        super().__init__(message, error_code, display)

    @property
    def display_message(self) -> str:
        return "Negative shift count"
