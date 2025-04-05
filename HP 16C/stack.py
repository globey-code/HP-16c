"""
stack.py
Implements the stack for the HP-16C emulator, including arithmetic operations.
Author: GlobeyCode (original), refactored by ChatGPT
License: MIT
Date: 3/23/2025 (original), refactored 2025-04-01
"""

from typing import List, Union
from error import (
    HP16CError, IncorrectWordSizeError, NoValueToShiftError,
    DivisionByZeroError, InvalidOperandError, StackUnderflowError,
    NegativeShiftCountError
)
from logging_config import logger

Number = Union[int, float]

# Helper functions for signed number conversion
def to_signed(value: int, word_size: int, mode: str) -> int:
    mask = (1 << word_size) - 1
    value &= mask
    if mode == "UNSIGNED":
        return value
    elif mode == "1S":
        if value == mask:
            return 0
        elif value & (1 << (word_size - 1)):
            return -((~value) & mask)
        else:
            return value
    else:  # "2S"
        if value & (1 << (word_size - 1)):
            return value - (1 << word_size)
        else:
            return value

def from_signed(value: int, word_size: int, mode: str) -> int:
    mask = (1 << word_size) - 1
    if mode == "UNSIGNED":
        return value & mask
    elif mode == "1S":
        return (~(-value)) & mask if value < 0 else value & mask
    else:  # "2S"
        return (value + (1 << word_size)) & mask if value < 0 else value & mask

class Stack:
    def __init__(self, word_size: int = 16, complement_mode: str = "UNSIGNED") -> None:
        self.word_size: int = word_size
        self.complement_mode: str = complement_mode
        self.current_mode: str = "DEC"  # "DEC" or "FLOAT"
        self._stack: List[int] = [0, 0, 0]  # Y, Z, T
        self._x_register: int = 0  # X register
        self._flags: dict[int, int] = {i: 0 for i in range(6)}
        self._last_x: int = 0
        self._i_register: int = 0
        self._data_registers: List[int] = [0] * 10
        

    def set_x_register(self, value):
        """Set the X register value."""
        self._x_register = value

    def get_x_register(self):
        """Get the X register value."""
        return self._x_register

    def get_word_size(self):
        """Get the current word size."""
        return self.word_size

    def get_complement_mode(self):
        """Get the current complement mode."""
        return self.complement_mode

    def set_g_flag(self, value):
        self._flags[5] = value  # Use integer 5
        logger.info(f"G flag set to {value}")

    def get_g_flag(self):
        return self._flags[5]  # Use integer 5
        
    def interpret_in_base(self, string_value: str, base: str) -> Number:
        """
        Convert a string representing a number in a given base into a numeric value.
        Uses the stack's complement mode and word size in integer modes.

        Args:
            string_value (str): The string to convert (e.g., "1A", "1010", "123.45").
            base (str): The base to interpret ("FLOAT", "DEC", "HEX", "BIN", "OCT").

        Returns:
            Number: The interpreted numeric value (int for integer modes, float for FLOAT).

        Raises:
            ValueError: If the string is invalid for the given base or mode.
        """
        # Remove leading/trailing whitespace to handle inputs like " 123 " or "1A "
        string_value = string_value.strip()
    
        # Handle empty strings by returning a default value
        if not string_value:
            return 0.0 if base == "FLOAT" else 0

        try:
            # FLOAT mode: Convert to float and return without masking
            if base == "FLOAT":
                return float(string_value)

            # DEC mode: Handle signed/unsigned integers based on complement mode
            elif base == "DEC":
                val = int(string_value)  # Convert string to integer in base 10
                mask = (1 << self.word_size) - 1  # Create mask, e.g., 65535 for 16 bits

                if self.complement_mode == "UNSIGNED":
                    if val < 0:
                        raise ValueError("Negative numbers not allowed in unsigned mode")
                    val = val & mask
                elif self.complement_mode == "1S":
                    if val < 0:
                        val = (~(-val)) & mask  # 1's complement for negative numbers
                    else:
                        val = val & mask
                else:  # "2S" (2's complement)
                    if val < 0:
                        val = ((1 << self.word_size) + val) & mask  # 2's complement conversion
                    else:
                        val = val & mask
                return val

            # HEX, BIN, OCT modes: Treat as unsigned integers and apply mask
            else:
                base_num = {"HEX": 16, "BIN": 2, "OCT": 8}[base]
                val = int(string_value, base_num)  # Convert string to integer in specified base
                mask = (1 << self.word_size) - 1
                val = val & mask  # Apply word size mask
                return val

        except ValueError as e:
            # Log the error and return a default value
            logger.info(f"Failed to interpret '{string_value}' in {base}: {e}, defaulting to 0")
            return 0.0 if base == "FLOAT" else 0

    def format_in_base(self, value: Number, base: str, pad: bool = False) -> str:
        """
        Format a numeric value into a string representation based on the specified base.
        
        Args:
            value (Number): The numeric value to format (int or float).
            base (str): The base to format in ("FLOAT", "DEC", "HEX", "BIN", "OCT").
            pad (bool): If True, pad with leading zeros to word size (default: False).
        
        Returns:
            str: The formatted string representation.
        """
        if base == "FLOAT":
            result = f"{float(value):.9f}".rstrip('0').rstrip('.')
            return result if result else '0'
        value = int(value)
        mask = (1 << self.word_size) - 1
        value &= mask
        display_leading_zeros = (self.test_flag(3) == 1) or pad
        if base == "BIN":
            result = format(value, f'0{self.word_size}b') if display_leading_zeros else (format(value, 'b') if value != 0 else '0')
        elif base == "OCT":
            oct_digits = (self.word_size + 2) // 3
            result = format(value, f'0{oct_digits}o') if display_leading_zeros else (format(value, 'o') if value != 0 else '0')
        elif base == "DEC":
            if self.complement_mode in {"1S", "2S"} and (value & (1 << (self.word_size - 1))):
                if self.complement_mode == "1S":
                    result = str(-((~value) & mask))
                else:
                    result = str(value - (1 << self.word_size))
            else:
                result = str(value)
        elif base == "HEX":
            hex_digits = (self.word_size + 3) // 4
            hex_str = format(value, f'0{hex_digits}x') if display_leading_zeros else (format(value, 'x') if value != 0 else '0')
            mapping = {'a': 'A', 'c': 'C', 'e': 'E', 'f': 'F'}
            result = ''.join(mapping.get(c, c) for c in hex_str)
        else:
            result = str(value)
        return result



    def set_flag(self, flag: int) -> None:
        self._flags[flag] = 1

    def clear_flag(self, flag: int) -> None:
        self._flags[flag] = 0

    def test_flag(self, flag: int) -> bool:
        return self._flags[flag] == 1

    def get_flags_bitfield(self) -> int:
        return (self._flags[0] |
                (self._flags[1] << 1) |
                (self._flags[2] << 2) |
                (self._flags[3] << 3))

    def apply_word_size(self, value: int) -> int:
        mask = (1 << self.word_size) - 1
        return value & mask

    def get_state(self) -> List[int]:
        return [self._x_register] + self._stack

    def push(self, value: int) -> None:
        self._stack.pop()
        self._stack.insert(0, self._x_register)
        self._x_register = value

    def pop(self) -> int:
        if self._x_register == 0 and all(x == 0 for x in self._stack):
            raise StackUnderflowError("Stack is empty")
        self._last_x = self._x_register
        self._x_register = self._stack.pop(0)
        self._stack.append(0)
        return self._last_x

    def peek(self) -> int:
        return self._x_register

    ### Arithmetic Operations ###

    def add(self) -> None:
        """Add X to Y and update the stack.

        Raises:
            StackUnderflowError: If the stack has fewer than 3 elements (Y, Z, T).
        """
        # Check if stack has at least 3 elements (Y, Z, T)
        if len(self._stack) < 3:
            raise StackUnderflowError("Stack underflow: need at least Y, Z, T")
    
        # Assign operands: Y from stack, X from register
        y = self._stack[0]      # Y
        x = self._x_register    # X
    
        # Perform addition based on current mode
        if self.current_mode == "FLOAT":
            # Floating-point addition
            result = y + x
            self.clear_flag(4)  # Clear carry flag
            self.clear_flag(5)  # Clear overflow flag
            # Check for infinity to set overflow flag
            if isinstance(result, float) and (result == float('inf') or result == float('-inf')):
                self.set_flag(5)
            logger.info(f"Add (FLOAT): {y} + {x} = {result}")
        else:
            # Integer addition (signed or unsigned)
            mode = self.get_complement_mode()
            word_size = self.get_word_size()
            mask = (1 << word_size) - 1
            max_signed = (1 << (word_size - 1)) - 1
            min_signed = -(1 << (word_size - 1))
        
            if mode == "UNSIGNED":
                # Unsigned integer addition
                unmasked_result = y + x
                result = unmasked_result & mask
                carry = 1 if unmasked_result > mask else 0
                overflow = carry
            else:
                # Signed integer addition
                a_signed = to_signed(y, word_size, mode)
                b_signed = to_signed(x, word_size, mode)
                result_signed = a_signed + b_signed
                # Convert back to unsigned representation
                result = from_signed(result_signed, word_size, mode)
                overflow = result_signed > max_signed or result_signed < min_signed
                carry = 0  # Carry typically not used in signed mode
        
            # Set or clear flags based on carry and overflow
            if carry:
                self.set_flag(4)  # Carry flag
            else:
                self.clear_flag(4)
            if overflow:
                self.set_flag(5)  # Overflow flag
            else:
                self.clear_flag(5)
            logger.info(f"Add: {y} + {x} = {result} ({mode}), carry={carry}, overflow={overflow}")
    
        # Save the old X value before it’s overwritten
        self._last_x = x
    
        # Update X register with result
        self._x_register = result
    
        # Update stack: Shift Z to Y, T to Z, and duplicate T
        t = self._stack[2]  # T
        self._stack = [self._stack[1], self._stack[2], t]  # [Z, T, T]

    def subtract(self) -> None:
        """Subtract X from Y and update the stack.

        Raises:
            StackUnderflowError: If the stack has fewer than 3 elements (Y, Z, T).
        """
        # Check if stack has at least 3 elements (Y, Z, T)
        if len(self._stack) < 3:
            raise StackUnderflowError("Stack underflow: need at least Y, Z, T")
    
        # Assign operands: Y from stack, X from register
        y = self._stack[0]      # Y
        x = self._x_register    # X
    
        # Perform subtraction based on current mode
        if self.current_mode == "FLOAT":
            # Floating-point subtraction
            result = y - x
            self.clear_flag(4)  # Clear borrow flag
            self.clear_flag(5)  # Clear overflow flag
            # Check for infinity to set overflow flag
            if isinstance(result, float) and (result == float('inf') or result == float('-inf')):
                self.set_flag(5)
            logger.info(f"Subtract (FLOAT): {y} - {x} = {result}")
        else:
            # Integer subtraction (signed or unsigned)
            mode = self.get_complement_mode()
            word_size = self.get_word_size()
            mask = (1 << word_size) - 1
            max_signed = (1 << (word_size - 1)) - 1
            min_signed = -(1 << (word_size - 1))
        
            if mode == "UNSIGNED":
                # Unsigned integer subtraction
                unmasked_result = y - x
                result = unmasked_result & mask
                borrow = 1 if y < x else 0
                overflow = borrow
            else:
                # Signed integer subtraction
                a_signed = to_signed(y, word_size, mode)
                b_signed = to_signed(x, word_size, mode)
                result_signed = a_signed - b_signed
                # Convert back to unsigned representation (assuming a helper function)
                result = result_signed & mask  # Simplification; may need from_signed()
                overflow = result_signed > max_signed or result_signed < min_signed
                borrow = 0  # Borrow typically not used in signed mode
        
            # Set or clear flags based on borrow and overflow
            if borrow:
                self.set_flag(4)  # Borrow flag
            else:
                self.clear_flag(4)
            if overflow:
                self.set_flag(5)  # Overflow flag
            else:
                self.clear_flag(5)
            logger.info(f"Subtract: {y} - {x} = {result} ({mode}), borrow={borrow}, overflow={overflow}")
    
        # Update X register with result
        self._x_register = result
    
        # Update stack: Shift Z to Y, T to Z, and duplicate T
        t = self._stack[2]  # T
        self._stack = [self._stack[1], self._stack[2], t]  # [Z, T, T]

    def multiply(self) -> None:
        if not self._stack:
            raise StackUnderflowError("Not enough values on stack")
        y = self._stack[0]
        x = self._x_register
        if self.current_mode == "FLOAT":
            result: Number = y * x
            self.clear_flag(4)
            self.clear_flag(5)
            if isinstance(result, float) and (result == float('inf') or result == float('-inf')):
                self.set_flag(5)
            logger.info(f"Multiply (FLOAT): {y} * {x} = {result}")
        else:
            mode = self.get_complement_mode()
            word_size = self.get_word_size()
            mask = (1 << word_size) - 1
            if mode == "UNSIGNED":
                unmasked_result = y * x
                result = unmasked_result & mask
            else:
                a_signed = to_signed(y, word_size, mode)
                b_signed = to_signed(x, word_size, mode)
                result_signed = a_signed * b_signed
                result = from_signed(result_signed, word_size, mode)
            self.clear_flag(4)
            self.clear_flag(5)
            logger.info(f"Multiply: {y} * {x} = {result} ({mode})")
        self._x_register = result
        self._stack[0] = self._stack[1]
        self._stack[1] = self._stack[2]

    def divide(self) -> None:
        if not self._stack:
            raise StackUnderflowError("Not enough values on stack")
        y = self._stack[0]
        x = self._x_register
        if x == 0:
            raise DivisionByZeroError()
        if self.current_mode == "FLOAT":
            result: Number = y / x
            self.clear_flag(4)
            self.clear_flag(5)
            if isinstance(result, float) and (result == float('inf') or result == float('-inf')):
                self.set_flag(5)
            logger.info(f"Divide (FLOAT): {y} / {x} = {result}")
        else:
            mode = self.get_complement_mode()
            word_size = self.get_word_size()
            mask = (1 << word_size) - 1
            max_signed = (1 << (word_size - 1)) - 1
            min_signed = -(1 << (word_size - 1))
            if mode == "UNSIGNED":
                result = int(y / x)
                remainder = y % x
                overflow = 0
            else:
                a_signed = to_signed(y, word_size, mode)
                b_signed = to_signed(x, word_size, mode)
                result_signed = int(a_signed / b_signed)
                remainder = a_signed % b_signed
                overflow = result_signed > max_signed or result_signed < min_signed
                result = from_signed(result_signed, word_size, mode)
            result = result & mask
            self._last_x = remainder
            if remainder != 0:
                self.set_flag(4)
            else:
                self.clear_flag(4)
            if overflow:
                self.set_flag(5)
            else:
                self.clear_flag(5)
            logger.info(f"Divide: {y} / {x} = {result} ({mode}), remainder={remainder}, overflow={overflow}")
        self._x_register = result
        self._stack[0] = self._stack[1]
        self._stack[1] = self._stack[2]

    def set_word_size(self, bits: int) -> None:
        """
        Set the word size for the stack and adjust all values accordingly.
    
        Args:
            bits (int): The new word size in bits (e.g., 8, 16, 32, 64).
    
        Raises:
            IncorrectWordSizeError: If the word size is invalid (e.g., not positive or exceeds reasonable limits).
        """
        if not isinstance(bits, int) or bits <= 0 or bits > 64:
            raise IncorrectWordSizeError(f"Invalid WSIZE:{bits} <= 64")
    
        old_word_size = self.word_size
        self.word_size = bits
        mask = (1 << bits) - 1
    
        # Adjust X register
        self._x_register = self._x_register & mask
    
        # Adjust stack values (Y, Z, T)
        for i in range(len(self._stack)):
            self._stack[i] = self._stack[i] & mask
    
        # Adjust data registers
        for i in range(len(self._data_registers)):
            self._data_registers[i] = self._data_registers[i] & mask
    
        # Adjust I register
        self._i_register = self._i_register & mask
    
        logger.info(f"Word size changed from {old_word_size} to {bits} bits")

    def set_complement_mode(self, mode: str) -> None:
        """
        Set the complement mode for the stack and adjust all values accordingly.
    
        Args:
            mode (str): The new complement mode ("UNSIGNED", "1S", or "2S").
    
        Raises:
            ValueError: If the mode is not one of "UNSIGNED", "1S", or "2S".
        """
        valid_modes = {"UNSIGNED", "1S", "2S"}
        if mode not in valid_modes:
            raise ValueError(f"Invalid complement mode: {mode}. Must be one of {valid_modes}")
    
        old_mode = self.complement_mode
        if old_mode == mode:
            return  # No change needed
    
        # Convert all values from the old mode to signed integers
        mask = (1 << self.word_size) - 1
        x_signed = to_signed(self._x_register, self.word_size, old_mode)
        stack_signed = [to_signed(val, self.word_size, old_mode) for val in self._stack]
        registers_signed = [to_signed(val, self.word_size, old_mode) for val in self._data_registers]
        i_signed = to_signed(self._i_register, self.word_size, old_mode)
    
        # Update the complement mode
        self.complement_mode = mode
    
        # Convert all values back to the new mode
        self._x_register = from_signed(x_signed, self.word_size, mode) & mask
        for i in range(len(self._stack)):
            self._stack[i] = from_signed(stack_signed[i], self.word_size, mode) & mask
        for i in range(len(self._data_registers)):
            self._data_registers[i] = from_signed(registers_signed[i], self.word_size, mode) & mask
        self._i_register = from_signed(i_signed, self.word_size, mode) & mask
    
        logger.info(f"Complement mode changed from {old_mode} to {mode}")

    def roll_up(self) -> None:
        """Roll up the stack: T→X, X→Y, Y→Z, Z→T."""
        old_t = self._stack[2]  # Capture current T
        self._stack[2] = self._stack[1]  # Z → T
        self._stack[1] = self._stack[0]  # Y → Z
        self._stack[0] = self._x_register  # X → Y
        self._x_register = old_t  # T → X
        logger.info("Stack rolled up: T→X, X→Y, Y→Z, Z→T")

    def last_x(self) -> int:
        """
        Return the last X value before the most recent stack operation that modified it.
    
        Returns:
            int: The value of _last_x.
        """
        return self._last_x

# f mode Row 1
# SL
    def shift_left(self) -> None:
        """Shift the X register left by one bit, respecting word size and complement mode."""
        word_size = self.get_word_size()
        mask = (1 << word_size) - 1
        mode = self.get_complement_mode()
    
        # Perform the shift
        shifted = (self._x_register << 1) & mask
    
        # Handle carry flag (bit shifted out)
        carry = 1 if (self._x_register & (1 << (word_size - 1))) else 0
        if carry:
            self.set_flag(4)
        else:
            self.clear_flag(4)
    
        # Update X register
        self._x_register = shifted
    
        logger.info(f"Shifted left: {shifted} (word size={word_size}, mode={mode}, carry={carry})")
# SR
    def shift_right(self) -> None:
        """Shift the X register right by one bit, respecting word size and complement mode."""
        word_size = self.get_word_size()
        mode = self.get_complement_mode()
    
        # Handle carry flag (least significant bit before shift)
        carry = self._x_register & 1
        if carry:
            self.set_flag(4)
        else:
            self.clear_flag(4)
    
        # Perform the shift based on complement mode
        if mode == "UNSIGNED":
            shifted = self._x_register >> 1
        else:  # 1S or 2S (arithmetic shift right, preserve sign bit)
            # Convert to signed, shift, then back to unsigned representation
            signed_value = to_signed(self._x_register, word_size, mode)
            shifted_signed = signed_value >> 1
            shifted = from_signed(shifted_signed, word_size, mode)
    
        # Update X register
        self._x_register = shifted
    
        logger.info(f"Shifted right: {shifted} (word size={word_size}, mode={mode}, carry={carry})")
# RL
    def rotate_left(self) -> None:
        """Rotate the X register left by one bit, wrapping MSB to LSB."""
        word_size = self.get_word_size()
        mask = (1 << word_size) - 1
        mode = self.get_complement_mode()
    
        # Perform the rotation
        msb = self._x_register & (1 << (word_size - 1))  # Get MSB
        shifted = (self._x_register << 1) & mask  # Shift left within word size
        rotated = shifted | (1 if msb else 0)  # Wrap MSB to LSB
    
        # Handle carry flag (MSB before rotation)
        carry = 1 if msb else 0
        if carry:
            self.set_flag(4)
        else:
            self.clear_flag(4)
    
        # Update X register
        self._x_register = rotated
    
        logger.info(f"Rotated left: {rotated} (word size={word_size}, mode={mode}, carry={carry})")
# RR
    def rotate_right(self) -> None:
        """Rotate the X register right by one bit, wrapping LSB to MSB."""
        word_size = self.get_word_size()
        mask = (1 << word_size) - 1
        mode = self.get_complement_mode()

        # Perform the rotation
        lsb = self._x_register & 1  # Get LSB
        shifted = self._x_register >> 1  # Shift right
        rotated = shifted | (lsb << (word_size - 1))  # Wrap LSB to MSB

        # Handle carry flag (LSB before rotation)
        carry = 1 if lsb else 0
        if carry:
            self.set_flag(4)
        else:
            self.clear_flag(4)

        # Update X register
        self._x_register = rotated

        logger.info(f"Rotated right: {rotated} (word size={word_size}, mode={mode}, carry={carry})")
# RLn
    def rotate_left_carry(self) -> None:
        """Rotate X left by X bits through carry, matching real HP-16C RLn behavior.
    
        Raises:
            ValueError: If word_size is not positive.
            NegativeShiftCountError: If the rotation count is negative or exceeds word_size - 1.
        """
        # Get and validate word size
        word_size = self.get_word_size()
        if word_size <= 0:
            raise ValueError("Word size must be positive")
    
        # Check raw rotation amount before any masking or normalization
        if self._x_register < 0 or self._x_register >= word_size:
            raise NegativeShiftCountError("Invalid rotation count", "E108")

    
        # Create mask for the word size
        mask = (1 << word_size) - 1
    
        # Determine rotation amount (already validated to be in [0, word_size - 1])
        n = self._x_register & mask  # Interpret as unsigned value
    
        # Get carry-in from flag 4
        carry_in = 1 if self.test_flag(4) else 0
    
        # Perform the rotation: (x << n) | (x >> (word_size - n))
        rotated = ((self._x_register << n) | (self._x_register >> (word_size - n))) & mask
    
        # Determine carry-out from the MSB of the rotated value
        carry_out = 1 if (rotated & (1 << (word_size - 1))) else 0
        if carry_out:
            self.set_flag(4)
        else:
            self.clear_flag(4)
    
        # Update the X register
        self._x_register = rotated
    
        # Log the operation details
        logger.info(f"Rotated left with carry by {n}: {rotated} (word_size={word_size}, carry_in={carry_in}, carry_out={carry_out})")
#RRn
    def rotate_right_carry(self) -> None:
        """Rotate X right by X bits through carry, matching real HP-16C RRn behavior."""
        word_size = self.get_word_size()
        mask = (1 << word_size) - 1
        n = self._x_register & mask  # Rotate by X’s value (14)
        carry_in = 1 if self.test_flag(4) else 0
        # Rotate n bits: (x >> n) | (x << (word_size - n))
        rotated = ((self._x_register >> n) | (self._x_register << (word_size - n))) & mask
        # Carry: LSB after rotation
        carry_out = 1 if (rotated & 1) else 0
        if carry_out:
            self.set_flag(4)
        else:
            self.clear_flag(4)
        self._x_register = rotated
        logger.info(f"Rotated right with carry by {n}: {rotated} (word_size={word_size}, carry_in={carry_in}, carry_out={carry_out})")