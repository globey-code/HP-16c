import sys
import os
import logging
from datetime import datetime
import stack
import f_mode
from controller import HP16CController
from error import HP16CError, DivisionByZeroError, StackUnderflowError

# Define logs directory and file BEFORE configuring logging
logs_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(logs_dir, exist_ok=True)
log_file = os.path.join(logs_dir, "rmd_xor_detailed.log")

# Configure logging with the correct filename
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger()

# Mock Display class (unchanged)
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
            logger.debug(f"Set entry (raw): {value}")
        else:
            self.current_entry = str(value)
            logger.debug(f"Set entry: {value}")

    def update_stack_content(self):
        logger.debug("Updating stack content (mocked)")

    @property
    def widget(self):
        class MockWidget:
            def after(self, ms, func):
                logger.debug(f"Scheduling function after {ms}ms")
                func()
        return MockWidget()

# Mock Button class (unchanged)
class MockButton:
    def __init__(self, top_label):
        self.config = {"orig_top_text": top_label}

    def get(self, key, default=None):
        return self.config.get(key, default)

# Rest of the functions remain unchanged
def log_test_case(description):
    logger.info(f"--- Test Case: {description} ---")

def setup_controller():
    mock_display = MockDisplay()
    controller = HP16CController(mock_display, None)
    logger.debug("Controller initialized")
    return controller

def reset_emulator(controller):
    logger.debug("Resetting emulator")
    stack.clear_stack()
    logger.debug(f"Stack cleared: {stack.get_state()}")
    stack.set_word_size(16)  # Default
    logger.debug(f"Word size set to default: {stack.get_word_size()}")
    stack.set_complement_mode("UNSIGNED")
    logger.debug(f"Complement mode set to: {stack.get_complement_mode()}")
    stack.set_carry_flag(0)
    logger.debug(f"Carry flag set to: {stack.get_carry_flag()}")
    controller.display.current_entry = "0"
    controller.display.raw_value = "0"
    logger.debug(f"Display reset: current_entry={controller.display.current_entry}, raw_value={controller.display.raw_value}")

def test_rmd(controller, x_value, y_value, word_size=4, carry_flag=0, complement_mode="UNSIGNED"):
    log_test_case(f"Double Remainder (RMD) - X: {x_value}, Y: {y_value}, Word Size: {word_size}, Carry Flag: {carry_flag}, Complement Mode: {complement_mode}")
    reset_emulator(controller)
    
    stack.set_word_size(word_size)
    stack.set_complement_mode(complement_mode)
    stack.set_carry_flag(carry_flag)
    
    button = MockButton("RMD")
    
    try:
        stack.clear_stack()
        logger.debug(f"Pushing X: {x_value}")
        stack.push(int(x_value))
        logger.debug(f"Stack after X: {stack.get_state()}")
        logger.debug(f"Pushing Y: {y_value}")
        stack.push(int(y_value))
        logger.debug(f"Stack after Y: {stack.get_state()}")
        controller.display.raw_value = str(x_value)
        
        logger.info(f"Stack before RMD: {stack.get_state()}")
        f_mode.f_action(button, controller.display, controller)
        
        logger.info(f"Result: Display = {controller.display.current_entry}, Stack = {stack.get_state()}, Carry Flag = {stack.get_carry_flag()}, Word Size = {stack.get_word_size()}, Complement Mode = {stack.get_complement_mode()}")
    except HP16CError as e:
        logger.info(f"Expected Error: {e.display_message}")

def test_xor(controller, x_value, y_value, word_size=4, carry_flag=0, complement_mode="UNSIGNED"):
    log_test_case(f"Logical XOR - X: {x_value}, Y: {y_value}, Word Size: {word_size}, Carry Flag: {carry_flag}, Complement Mode: {complement_mode}")
    reset_emulator(controller)
    
    stack.set_word_size(word_size)
    stack.set_complement_mode(complement_mode)
    stack.set_carry_flag(carry_flag)
    
    button = MockButton("XOR")
    
    try:
        stack.clear_stack()
        logger.debug(f"Pushing Y: {y_value}")
        stack.push(int(y_value))
        logger.debug(f"Stack after Y: {stack.get_state()}")
        logger.debug(f"Pushing X: {x_value}")
        stack.push(int(x_value))
        logger.debug(f"Stack after X: {stack.get_state()}")
        controller.display.raw_value = str(x_value)
        
        logger.info(f"Stack before XOR: {stack.get_state()}")
        f_mode.f_action(button, controller.display, controller)
        
        logger.info(f"Result: Display = {controller.display.current_entry}, Stack = {stack.get_state()}, Carry Flag = {stack.get_carry_flag()}, Word Size = {stack.get_word_size()}, Complement Mode = {stack.get_complement_mode()}")
    except HP16CError as e:
        logger.info(f"Expected Error: {e.display_message}")

if __name__ == "__main__":
    logger.info("Starting RMD and XOR Stress Tests")
    controller = setup_controller()

    word_sizes = [1, 4, 8, 16, 32, 64]
    complement_modes = ["UNSIGNED", "1S", "2S"]
    carry_flags = [0, 1]

    for word_size in word_sizes:
        for complement_mode in complement_modes:
            for carry_flag in carry_flags:
                test_rmd(controller, 10, 3, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_xor(controller, 10, 3, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_rmd(controller, 0, 0, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_xor(controller, 0, 0, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_rmd(controller, 10, 0, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                large_val = (1 << word_size) * 2
                test_rmd(controller, large_val, 3, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                test_xor(controller, large_val, 3, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                if complement_mode in ["1S", "2S"]:
                    min_val = -(1 << (word_size - 1))
                    test_rmd(controller, min_val, 3, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)
                    test_xor(controller, min_val, 3, word_size=word_size, carry_flag=carry_flag, complement_mode=complement_mode)

    logger.info("RMD and XOR Stress Tests Completed")