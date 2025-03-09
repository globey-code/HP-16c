import unittest
from unittest.mock import MagicMock
from stack import stack, push, pop, apply_word_size, set_word_size
from f_function import action_sl
from error import show_error

class TestShiftLeft(unittest.TestCase):

    def setUp(self):
        """Ensure stack is cleared properly without losing its reference."""
        global stack
        stack[:] = [0.0, 0.0, 0.0, 0.0]  # Keep the reference, clear values
        print(f"[TEST] Stack Reset to: {stack}")  # Debugging
        self.display_mock = MagicMock()

    def test_basic_shift(self):
        """Test shifting a basic number left (1 -> 2)."""
        push(1)
        action_sl(self.display_mock)
        self.assertEqual(stack[0], 2)

    def test_multiple_shifts(self):
        """Test shifting a larger number left (4 -> 8)."""
        push(4)
        action_sl(self.display_mock)
        self.assertEqual(stack[0], 8)

    def test_large_value_shift(self):
        """Test shifting a large number left (128 -> 256)."""
        push(128)
        action_sl(self.display_mock)
        self.assertEqual(stack[0], 256)

    def test_word_size_limit(self):
        """Test shifting a number left in an 8-bit system (should wrap)."""
        set_word_size(8)
        push(128)  # 0b10000000 in 8-bit
        action_sl(self.display_mock)
        self.assertEqual(stack[0], 0)  # Expected result: wrap-around

    def test_negative_number_shift(self):
        """Test shifting a negative number left (-1 -> -2)."""
        set_word_size(8)
        push(-1)
        action_sl(self.display_mock)
        self.assertEqual(stack[0], -2)

    def test_stack_underflow(self):
        """Test shifting left when stack is empty (should show error)."""
        action_sl(self.display_mock)
        self.display_mock.set_entry.assert_called_with("ERROR E101: Stack Underflow - Operation requires more values in the stack.")

    def test_invalid_operand(self):
        """Test shifting left on a float (should show error)."""
        push(3.5)
        action_sl(self.display_mock)
        self.display_mock.set_entry.assert_called_with("ERROR E102: Invalid Operand - Operation cannot be performed on this type.")

    def test_basic_shift(self):
        """Test shifting a basic number left (1 -> 2)."""
        push(1)
        print(f"[TEST] Stack before SL: {stack}")  # Debugging
        action_sl(self.display_mock)
        print(f"[TEST] Stack after SL: {stack}")  # Debugging
        self.assertEqual(stack[0], 2)

if __name__ == "__main__":
    unittest.main()
