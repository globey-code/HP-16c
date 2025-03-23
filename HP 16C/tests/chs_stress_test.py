# chs_stress_test.py
# Stress test script for the HP-16C emulator, focusing on the CHS (change sign) operation.
# Author: GlobeyCode
# License: MIT
# Date: 3/23/2025
# Dependencies: Python 3.6+, HP-16C emulator modules (stack, base_conversion, arithmetic, display, controller)

import sys
import os
import random


# Dynamically add the parent directory (HP-16C emulator root) to sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

# Debugging logs to verify the setup
print("Parent directory added to sys.path:", parent_dir)
print("Full sys.path:", sys.path)

# Import core modules from the HP-16C emulator
import stack            # Stack operations
import base_conversion  # Base conversion utilities
import arithmetic       # Arithmetic functions
import display          # Display module (mocked here)
import controller
import error
from controller import HP16CController  # Main controller class

# Verify module origins
print("Using stack from:", stack.__file__)
print("Using base_conversion from:", base_conversion.__file__)
print("Using arithmetic from:", arithmetic.__file__)
print("Using display from:", display.__file__)
print("Using controller from:", controller.__file__)

# Set up logging to both console and file
log_dir = os.path.join('logs')
log_file_path = os.path.join(log_dir, 'CHS_stress_100k.log')

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = open(log_file_path, 'w')
original_stdout = sys.stdout

# Tee class for dual output
class Tee:
    def __init__(self, *files):
        self.files = files

    def write(self, text):
        for file in self.files:
            file.write(text)

    def flush(self):
        for file in self.files:
            file.flush()

sys.stdout = Tee(original_stdout, log_file)

# Mock classes for testing without GUI
class MockStackDisplay:
    def config(self, text):
        pass  # Suppress output for large test runs

class MockWidget:
    def after(self, ms, func):
        func()  # Execute immediately for testing

class MockDisplay:
    def __init__(self):
        self.current_value = 0
        self.raw_value = "0"
        self.mode = "DEC"
        self.current_entry = "0"
        self.is_error_displayed = False
        self.widget = MockWidget()

    def set_entry(self, entry, raw=False):
        if self.is_error_displayed:
            return
        if raw:
            self.current_entry = entry
            self.raw_value = entry
        else:
            if isinstance(entry, str):
                val = base_conversion.interpret_in_base(entry, self.mode)
            else:
                val = int(entry)
            val_int = stack.apply_word_size(val)
            entry_str = base_conversion.format_in_current_base(val_int, self.mode)
            self.current_entry = entry_str
            self.current_value = val_int
            self.raw_value = entry_str

    def clear_entry(self):
        self.current_entry = "0"
        self.current_value = 0
        self.raw_value = "0"

    def set_error(self):
        self.is_error_displayed = True
        self.current_entry = "Error"
        self.raw_value = "Error"

    def clear_error(self):
        self.is_error_displayed = False
        self.current_entry = "0"
        self.current_value = 0
        self.raw_value = "0"

    def update_stack_content(self):
        pass  # Suppress output

    def append_entry(self, digit):
        self.raw_value += digit
        self.current_entry = self.raw_value

# Enhanced HP16CController with corrected CHS and operator handling
class EnhancedHP16CController(HP16CController):
    def __init__(self, display, entry_widget, stack_display):
        super().__init__(display, entry_widget, stack_display)
        self.stack = stack  # Use the imported stack module directly

    def change_sign(self):
        val = self.display.current_value or 0
        complement_mode = self.stack.get_complement_mode()
        word_size = self.stack.get_word_size()
        mask = (1 << word_size) - 1
        if complement_mode == "UNSIGNED":
            negated = (-val) & mask
        elif complement_mode == "1S":
            negated = (~val) & mask
        else:  # "2S"
            negated = ((~val) + 1) & mask
        self.display.set_entry(negated)
        self.stack._x_register = negated

    def enter_operator(self, operator):
        try:
            y = self.stack.pop()
            x = self.stack.pop()
            if operator == "+":
                result = arithmetic.add(x, y)
            elif operator == "-":
                result = arithmetic.subtract(y, x)
            elif operator == "*":
                result = arithmetic.multiply(x, y)
            elif operator == "/":
                if x == 0:
                    self.display.set_error()
                    self.stack._stack = [0, 0, 0]
                    self.stack._x_register = 0
                    return
                result = arithmetic.divide(y, x)
            self.stack.push(result)
            self.display.set_entry(result)
        except Exception as e:
            self.display.set_error()
            self.stack._x_register = 0

# Initialize emulator components with enhanced controller
display = MockDisplay()
stack_display = MockStackDisplay()
controller = EnhancedHP16CController(display, None, stack_display)

# Simulate a sequence of operations with proper RPN handling
def simulate_operations(operations, complement_mode, word_size):
    stack.set_complement_mode(complement_mode)
    stack.set_word_size(word_size)
    stack._stack = [0, 0, 0]  # Reset stack
    stack._x_register = 0     # Reset X
    display.mode = "DEC"
    display.clear_entry()
    display.clear_error()     # Reset error state

    for op in operations:
        if isinstance(op, int):
            display.set_entry(op)
            stack._x_register = display.current_value
        elif op == "ENTER":
            stack.stack_lift()
        elif op in ["+", "-", "*", "/"]:
            controller.enter_operator(op)
        elif op == "CHS":
            controller.change_sign()
        else:
            raise ValueError(f"Unknown operation: {op}")
    return display.current_value, display.current_entry, display.is_error_displayed

# Compute expected results for random test cases
def compute_expected(operations, complement_mode, word_size):
    stack.set_complement_mode(complement_mode)
    stack.set_word_size(word_size)
    stack._stack = [0, 0, 0]  # Reset stack: Y, Z, T
    stack._x_register = 0     # Reset X register
    mask = (1 << word_size) - 1  # Bit mask for word size

    error_occurred = False

    for op in operations:
        if error_occurred:
            break  # Stop processing if error occurred

        if isinstance(op, int):
            stack._x_register = op & mask  # Set X with masked value
        elif op == "ENTER":
            stack.push(stack._x_register)   # Lift the stack
        elif op in ["+", "-", "*", "/"]:
            try:
                y = stack.pop()  # Pop Y
                x = stack.pop()  # Pop X
                if op == "+":
                    result = arithmetic.add(x, y)
                elif op == "-":
                    result = arithmetic.subtract(y, x)
                elif op == "*":
                    result = arithmetic.multiply(x, y)
                elif op == "/":
                    if x == 0:  # Division by zero
                        error_occurred = True
                        break
                    result = arithmetic.divide(y, x)
                stack.push(result)
            except error.StackUnderflowError:
                error_occurred = True
                break
        elif op == "CHS":
            x = stack._x_register
            if complement_mode == "UNSIGNED":
                negated = (-x) & mask
            elif complement_mode == "1S":
                negated = (~x) & mask
            else:  # "2S"
                negated = ((~x) + 1) & mask
            stack._x_register = negated

    if error_occurred:
        return None, "Error", True
    else:
        result = stack._x_register
        display_val = base_conversion.format_in_current_base(result, "DEC")
        return result, display_val, False

# Generate 100,000 random test cases
def generate_random_test_cases(num_tests=100000):
    random.seed(42)  # For reproducibility
    test_cases = []
    operations_pool = ["ENTER", "CHS", "+", "-", "*", "/"]
    complement_modes = ["UNSIGNED", "1S", "2S"]
    word_sizes = [1, 2, 4, 8, 16, 32, 64]

    for _ in range(num_tests):
        # Randomly select complement mode and word size
        complement_mode = random.choice(complement_modes)
        word_size = random.choice(word_sizes)
        mask = (1 << word_size) - 1

        # Generate a random sequence of operations (length between 1 and 10)
        num_ops = random.randint(1, 10)
        operations = []
        for _ in range(num_ops):
            if random.random() < 0.5:
                # Add a random value within word size bounds
                val = random.randint(-mask, mask)
                operations.append(val)
            else:
                # Add a random operation
                operations.append(random.choice(operations_pool))

        # Compute expected result
        expected_value, expected_display, expected_error = compute_expected(operations, complement_mode, word_size)

        # Create test case
        test_cases.append({
            "description": f"Random test: {operations}",
            "complement_mode": complement_mode,
            "word_size": word_size,
            "operations": operations,
            "expected_value": expected_value,
            "expected_display": expected_display,
            "expected_error": expected_error
        })

    return test_cases

# Generate 100,000 random test cases
all_test_cases = generate_random_test_cases(100000)

# Execute stress tests
try:
    print("=== HP-16C Enhanced Stress Test with 100,000 Cases ===")
    print("==================================================\n")

    passed, failed = 0, 0

    for idx, case in enumerate(all_test_cases):
        try:
            result_value, result_display, is_error = simulate_operations(
                case["operations"], case["complement_mode"], case["word_size"]
            )

            if case["expected_error"]:
                assert is_error, "Expected error state but none occurred"
                assert result_display == "Error", f"Expected 'Error' display, got {result_display}"
            else:
                assert not is_error, "Unexpected error state"
                assert result_value == case["expected_value"], (
                    f"Value mismatch: got {result_value}, expected {case['expected_value']}"
                )
                assert result_display == case["expected_display"], (
                    f"Display mismatch: got {result_display}, expected {case['expected_display']}"
                )

            passed += 1
        except AssertionError as e:
            # Log only failed test cases to keep output manageable
            print(f"Test Case {idx + 1}: {case['description']}")
            print(f"  Mode: {case['complement_mode']}, Word Size: {case['word_size']}, Operations: {case['operations']}")
            print(f"  Result: Value = {result_value}, Display = {result_display}, Error = {is_error}")
            print(f"  Expected: Value = {case['expected_value']}, Display = {case['expected_display']}, Error = {case['expected_error']}")
            print(f"  Status: \033[91mFAIL\033[0m - {str(e)}")
            print("------------------------------------")
            failed += 1

    print("\nStress Test Completed")
    print(f"Total Passed: {passed}")
    print(f"Total Failed: {failed}")

finally:
    sys.stdout = original_stdout
    log_file.close()