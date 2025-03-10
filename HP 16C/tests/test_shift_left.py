"""
test_shift_left.py

Example unit test for shift-left logic in f_function.py.

Reason for change:
- Demonstrates how to test a single function in isolation (like action_sl).
- No UI or display references needed if we design well.
"""

import sys, os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PARENT_DIR)

import unittest
from unittest.mock import MagicMock
import stack
from f_function import action_sl

class TestShiftLeft(unittest.TestCase):
    def setUp(self):
        stack.stack[:] = [0.0, 0.0, 0.0, 0.0]  # clear but keep reference
        self.display_mock = MagicMock()
        self.display_mock.set_entry = MagicMock()
        self.display_mock.raw_value = ""

    def test_shift_left_basic(self):
        stack.push(1)
        action_sl(self.display_mock)
        self.assertEqual(stack.peek(), 2)
        self.display_mock.set_entry.assert_called_with("2")

    def test_shift_left_invalid_operand(self):
        stack.push(3.5)  # float with fraction
        with self.assertRaises(Exception):
            # or specifically InvalidOperandError if we wanted
            action_sl(self.display_mock)

if __name__ == "__main__":
    unittest.main()
