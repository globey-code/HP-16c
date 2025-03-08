#arithmetic.py
#
# Provides integer-based arithmetic operations for the HP 16C emulator.
#
# Important: The HP 16C uses "second operand operator top operand" ordering.
# For example, if the stack has [2, 3] (2 is second, 3 is top), then:
# - Addition: 2 + 3
# - Subtraction: 2 - 3
# - Multiplication: 2 * 3
# - Division: 2 / 3
#
# Because the real HP 16C is primarily an integer (fixed-point) calculator, we
# use integer arithmetic here, including truncating division. For floating-point
# support or base conversion, see higher-level modules like stack.py or base_conversion.py.


def add(second_value, top_value):
    return second_value + top_value

def subtract(second_value, top_value):
    return second_value - top_value

def multiply(second_value, top_value):
    return second_value * top_value


# Perform integer division: second_value ÷ top_value, truncating toward zero.
# Raises ZeroDivisionError if top_value is zero.
#
# Example: if second_value=8 and top_value=3, result is 2 (integer division).
def divide(second_value, top_value):    
    if top_value == 0:
        raise ZeroDivisionError("Division by zero")
    # Truncate toward zero (Python's // floors if negatives are involved, so use int(...) for exact truncation).
    return int(second_value / top_value)