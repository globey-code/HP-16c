"""
f_mode_row_1_test.py

Comprehensive unit tests for Row 1 f-mode operations in the HP 16C emulator.
Logs detailed results to logs/row_1.log.
"""

import os
import logging
from datetime import datetime
import stack
import f_mode
from controller import HP16CController
from error import HP16CError

# Mock Display class for testing without Tkinter
class MockDisplay:
    def __init__(self):
        self.current_entry = "0"
        self.raw_value = "0"
        self.mode = "DEC"
        self.error_displayed = False

    def set_entry(self, value, raw=False):
        if raw:
            self.current_entry = value
            self.error_displayed = True
        else:
            self.current_entry = str(value)

    def update_stack_content(self):
        pass

    @property
    def widget(self):
        class MockWidget:
            def after(self, ms, func):
                func()
        return MockWidget()

# Mock Buttons class for testing
class MockButtons:
    def __init__(self):
        self.buttons = {}

    def bind_buttons(self, controller):
        pass

# Mock Button class for f_action
class MockButton:
    def __init__(self, top_label):
        self.config = {"orig_top_text": top_label}

    def get(self, key, default=None):
        return self.config.get(key, default)

# Setup logging
logs_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(logs_dir, exist_ok=True)
log_file = os.path.join(logs_dir, "row_1.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger()

def log_test_case(description):
    logger.info(f"--- Test Case: {description} ---")

def setup_controller():
    mock_display = MockDisplay()
    mock_buttons = MockButtons()
    controller = HP16CController(mock_display, mock_buttons)
    return controller

def reset_emulator(controller):
    stack.clear_stack()
    stack.set_word_size(16)
    stack.set_complement_mode("UNSIGNED")
    stack.set_carry_flag(0)
    controller.display.current_entry = "0"
    controller.display.raw_value = "0"

# Test functions
def test_sl(controller, display_value, word_size=4, carry_flag=0, complement_mode="UNSIGNED"):
    log_test_case(f"Shift Left (SL) - Display: {display_value}, Word Size: {word_size}, Carry Flag: {carry_flag}, Complement Mode: {complement_mode}")
    reset_emulator(controller)
    stack.set_word_size(word_size)
    stack.set_complement_mode(complement_mode)
    stack.set_carry_flag(carry_flag)
    controller.display.raw_value = str(display_value)
    stack.push(int(display_value))
    button = MockButton("SL")
    try:
        f_mode.f_action(button, controller.display, controller)
        logger.info(f"Result: Display = {controller.display.current_entry}, Stack = {stack.get_state()}, Carry Flag = {stack.get_carry_flag()}, Word Size = {stack.get_word_size()}, Complement Mode = {stack.get_complement_mode()}")
    except HP16CError as e:
        logger.error(f"Error: {e.display_message}")

def test_sr(controller, display_value, word_size=4, carry_flag=0, complement_mode="UNSIGNED"):
    log_test_case(f"Shift Right (SR) - Display: {display_value}, Word Size: {word_size}, Carry Flag: {carry_flag}, Complement Mode: {complement_mode}")
    reset_emulator(controller)
    stack.set_word_size(word_size)
    stack.set_complement_mode(complement_mode)
    stack.set_carry_flag(carry_flag)
    controller.display.raw_value = str(display_value)
    stack.push(int(display_value))
    button = MockButton("SR")
    try:
        f_mode.f_action(button, controller.display, controller)
        logger.info(f"Result: Display = {controller.display.current_entry}, Stack = {stack.get_state()}, Carry Flag = {stack.get_carry_flag()}, Word Size = {stack.get_word_size()}, Complement Mode = {stack.get_complement_mode()}")
    except HP16CError as e:
        logger.error(f"Error: {e.display_message}")

def test_rl(controller, display_value, word_size=4, carry_flag=0, complement_mode="UNSIGNED"):
    log_test_case(f"Rotate Left (RL) - Display: {display_value}, Word Size: {word_size}, Carry Flag: {carry_flag}, Complement Mode: {complement_mode}")
    reset_emulator(controller)
    stack.set_word_size(word_size)
    stack.set_complement_mode(complement_mode)
    stack.set_carry_flag(carry_flag)
    controller.display.raw_value = str(display_value)
    stack.push(int(display_value))
    button = MockButton("RL")
    try:
        f_mode.f_action(button, controller.display, controller)
        logger.info(f"Result: Display = {controller.display.current_entry}, Stack = {stack.get_state()}, Carry Flag = {stack.get_carry_flag()}, Word Size = {stack.get_word_size()}, Complement Mode = {stack.get_complement_mode()}")
    except HP16CError as e:
        logger.error(f"Error: {e.display_message}")

def test_rr(controller, display_value, word_size=4, carry_flag=0, complement_mode="UNSIGNED"):
    log_test_case(f"Rotate Right (RR) - Display: {display_value}, Word Size: {word_size}, Carry Flag: {carry_flag}, Complement Mode: {complement_mode}")
    reset_emulator(controller)
    stack.set_word_size(word_size)
    stack.set_complement_mode(complement_mode)
    stack.set_carry_flag(carry_flag)
    controller.display.raw_value = str(display_value)
    stack.push(int(display_value))
    button = MockButton("RR")
    try:
        f_mode.f_action(button, controller.display, controller)
        logger.info(f"Result: Display = {controller.display.current_entry}, Stack = {stack.get_state()}, Carry Flag = {stack.get_carry_flag()}, Word Size = {stack.get_word_size()}, Complement Mode = {stack.get_complement_mode()}")
    except HP16CError as e:
        logger.error(f"Error: {e.display_message}")

def test_rln(controller, display_value, word_size=4, carry_flag=0, complement_mode="UNSIGNED"):
    log_test_case(f"Rotate Left Carry (RLn) - Display: {display_value}, Word Size: {word_size}, Carry Flag: {carry_flag}, Complement Mode: {complement_mode}")
    reset_emulator(controller)
    stack.set_word_size(word_size)
    stack.set_complement_mode(complement_mode)
    stack.set_carry_flag(carry_flag)
    controller.display.raw_value = str(display_value)
    stack.push(int(display_value))
    button = MockButton("RLn")
    try:
        f_mode.f_action(button, controller.display, controller)
        logger.info(f"Result: Display = {controller.display.current_entry}, Stack = {stack.get_state()}, Carry Flag = {stack.get_carry_flag()}, Word Size = {stack.get_word_size()}, Complement Mode = {stack.get_complement_mode()}")
    except HP16CError as e:
        logger.error(f"Error: {e.display_message}")

def test_rrn(controller, display_value, word_size=4, carry_flag=0, complement_mode="UNSIGNED"):
    log_test_case(f"Rotate Right Carry (RRn) - Display: {display_value}, Word Size: {word_size}, Carry Flag: {carry_flag}, Complement Mode: {complement_mode}")
    reset_emulator(controller)
    stack.set_word_size(word_size)
    stack.set_complement_mode(complement_mode)
    stack.set_carry_flag(carry_flag)
    controller.display.raw_value = str(display_value)
    stack.push(int(display_value))
    button = MockButton("RRn")
    try:
        f_mode.f_action(button, controller.display, controller)
        logger.info(f"Result: Display = {controller.display.current_entry}, Stack = {stack.get_state()}, Carry Flag = {stack.get_carry_flag()}, Word Size = {stack.get_word_size()}, Complement Mode = {stack.get_complement_mode()}")
    except HP16CError as e:
        logger.error(f"Error: {e.display_message}")

def test_maskl(controller, display_value, bits, word_size=4, carry_flag=0, complement_mode="UNSIGNED"):
    log_test_case(f"Mask Left (MASKL) - Display: {display_value}, Bits: {bits}, Word Size: {word_size}, Carry Flag: {carry_flag}, Complement Mode: {complement_mode}")
    reset_emulator(controller)
    stack.set_word_size(word_size)
    stack.set_complement_mode(complement_mode)
    stack.set_carry_flag(carry_flag)
    controller.display.raw_value = str(bits)
    stack.push(int(display_value))
    button = MockButton("MASKL")
    try:
        f_mode.f_action(button, controller.display, controller)
        logger.info(f"Result: Display = {controller.display.current_entry}, Stack = {stack.get_state()}, Carry Flag = {stack.get_carry_flag()}, Word Size = {stack.get_word_size()}, Complement Mode = {stack.get_complement_mode()}")
    except HP16CError as e:
        logger.error(f"Error: {e.display_message}")

def test_maskr(controller, display_value, bits, word_size=4, carry_flag=0, complement_mode="UNSIGNED"):
    log_test_case(f"Mask Right (MASKR) - Display: {display_value}, Bits: {bits}, Word Size: {word_size}, Carry Flag: {carry_flag}, Complement Mode: {complement_mode}")
    reset_emulator(controller)
    stack.set_word_size(word_size)
    stack.set_complement_mode(complement_mode)
    stack.set_carry_flag(carry_flag)
    controller.display.raw_value = str(bits)
    stack.push(int(display_value))
    button = MockButton("MASKR")
    try:
        f_mode.f_action(button, controller.display, controller)
        logger.info(f"Result: Display = {controller.display.current_entry}, Stack = {stack.get_state()}, Carry Flag = {stack.get_carry_flag()}, Word Size = {stack.get_word_size()}, Complement Mode = {stack.get_complement_mode()}")
    except HP16CError as e:
        logger.error(f"Error: {e.display_message}")

def test_rmd(controller, x_value, y_value, word_size=4, carry_flag=0, complement_mode="UNSIGNED"):
    log_test_case(f"Double Remainder (RMD) - X: {x_value}, Y: {y_value}, Word Size: {word_size}, Carry Flag: {carry_flag}, Complement Mode: {complement_mode}")
    reset_emulator(controller)
    stack.set_word_size(word_size)
    stack.set_complement_mode(complement_mode)
    stack.set_carry_flag(carry_flag)
    button = MockButton("RMD")
    try:
        if x_value == 0 and y_value == 0:
            stack.clear_stack()  # Ensure stack is empty for underflow test
        else:
            stack.push(int(y_value))  # Push Y (divisor) first
            stack.push(int(x_value))  # Then X (dividend)
        controller.display.raw_value = str(x_value)
        logger.info(f"Stack before RMD: {stack.get_state()}")
        f_mode.f_action(button, controller.display, controller)
        logger.info(f"Result: Display = {controller.display.current_entry}, Stack = {stack.get_state()}, Carry Flag = {stack.get_carry_flag()}, Word Size = {stack.get_word_size()}, Complement Mode = {stack.get_complement_mode()}")
    except HP16CError as e:
        if isinstance(e, StackUnderflowError) and x_value == 0 and y_value == 0:
            logger.info(f"Expected StackUnderflowError: {e.display_message}")
        elif isinstance(e, DivisionByZeroError) and y_value == 0 and x_value != 0:
            logger.info(f"Expected DivisionByZeroError: {e.display_message}")
        else:
            logger.error(f"Unexpected Error: {e.display_message}")

def test_xor(controller, x_value, y_value, word_size=4, carry_flag=0, complement_mode="UNSIGNED"):
    log_test_case(f"Logical XOR - X: {x_value}, Y: {y_value}, Word Size: {word_size}, Carry Flag: {carry_flag}, Complement Mode: {complement_mode}")
    reset_emulator(controller)
    stack.set_word_size(word_size)
    stack.set_complement_mode(complement_mode)
    stack.set_carry_flag(carry_flag)
    button = MockButton("XOR")
    try:
        if x_value == 0 and y_value == 0:
            stack.clear_stack()  # Ensure stack is empty for underflow test
        else:
            stack.push(int(y_value))  # Push Y first
            stack.push(int(x_value))  # Then X
        controller.display.raw_value = str(x_value)
        f_mode.f_action(button, controller.display, controller)
        logger.info(f"Result: Display = {controller.display.current_entry}, Stack = {stack.get_state()}, Carry Flag = {stack.get_carry_flag()}, Word Size = {stack.get_word_size()}, Complement Mode = {stack.get_complement_mode()}")
    except HP16CError as e:
        if isinstance(e, StackUnderflowError) and x_value == 0 and y_value == 0:
            logger.info(f"Expected StackUnderflowError: {e.display_message}")
        else:
            logger.error(f"Unexpected Error: {e.display_message}")

# Main test execution
if __name__ == "__main__":
    logger.info("Starting Row 1 Tests")
    controller = setup_controller()

    # Test configurations
    word_sizes = [1, 4, 8, 16, 32, 64]
    complement_modes = ["UNSIGNED", "1S", "2S"]
    carry_flags = [0, 1]

    # Normal operation tests
    for word_size in word_sizes:
        for complement_mode in complement_modes:
            for carry_flag in carry_flags:
                # Positive value (8)
                test_sl(controller, 8, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_sr(controller, 8, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_rl(controller, 8, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_rr(controller, 8, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_rln(controller, 8, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_rrn(controller, 8, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_maskl(controller, 8, bits=2, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_maskr(controller, 8, bits=2, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_rmd(controller, 10, 3, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_xor(controller, 10, 3, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)

                # Zero value (empty stack equivalent)
                test_sl(controller, 0, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_sr(controller, 0, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_rl(controller, 0, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_rr(controller, 0, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_rln(controller, 0, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_rrn(controller, 0, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_maskl(controller, 0, bits=2, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_maskr(controller, 0, bits=2, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_rmd(controller, 0, 0, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_xor(controller, 0, 0, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)

                # Maximum positive value for word size
                max_val = (1 << word_size) - 1  # e.g., 15 for 4 bits
                test_sl(controller, max_val, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_sr(controller, max_val, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_rl(controller, max_val, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_rr(controller, max_val, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_rln(controller, max_val, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_rrn(controller, max_val, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_maskl(controller, max_val, bits=word_size//2, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_maskr(controller, max_val, bits=word_size//2, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_rmd(controller, max_val, 3, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_xor(controller, max_val, 3, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)

                # Negative value (only for 1S and 2S modes)
                if complement_mode in ["1S", "2S"]:
                    min_val = -(1 << (word_size - 1))  # e.g., -8 for 4 bits in 2S
                    test_sl(controller, min_val, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                    test_sr(controller, min_val, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                    test_rl(controller, min_val, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                    test_rr(controller, min_val, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                    test_rln(controller, min_val, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                    test_rrn(controller, min_val, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                    test_maskl(controller, min_val, bits=word_size//2, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                    test_maskr(controller, min_val, bits=word_size//2, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                    test_rmd(controller, min_val, 3, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                    test_xor(controller, min_val, 3, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)

                # Stress test (large value)
                large_val = (1 << word_size) * 2  # Exceeds word size
                test_sl(controller, large_val, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_sr(controller, large_val, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_rl(controller, large_val, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_rr(controller, large_val, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_rln(controller, large_val, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_rrn(controller, large_val, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_maskl(controller, large_val, bits=word_size//2, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_maskr(controller, large_val, bits=word_size//2, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_rmd(controller, large_val, 3, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_xor(controller, large_val, 3, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)

                # MASKL/MASKR with invalid bits
                invalid_bits = word_size + 1
                test_maskl(controller, 8, bits=invalid_bits, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_maskr(controller, 8, bits=invalid_bits, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_maskl(controller, 8, bits=-1, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_maskr(controller, 8, bits=-1, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)

                # RMD with zero divisor
                test_rmd(controller, 10, 0, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)

    logger.info("Row 1 Tests Completed")