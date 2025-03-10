# test_base_conversion.py

import sys, os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PARENT_DIR)

import unittest
import base_conversion

class MockDisplay:
    """
    A simple mock display to simulate get_entry(), set_entry(), set_mode().
    This avoids needing the full Tkinter UI for tests.
    """
    def __init__(self, initial_text=""):
        self._entry = initial_text
        self.raw_value = initial_text  # Make raw_value match the real display usage
        self.mode = "DEC"

    def get_entry(self):
        return self._entry

    def set_entry(self, new_text):
        self._entry = new_text
        self.raw_value = new_text  # Keep them in sync

    def set_mode(self, new_mode):
        self.mode = new_mode


class TestBaseConversion(unittest.TestCase):

    def setUp(self):
        """
        Reset the current_base to a known default before each test.
        """
        base_conversion.current_base = "DEC"

    def test_interpret_dec(self):
        """
        Test interpreting a decimal string in DEC mode.
        """
        base_conversion.current_base = "DEC"
        result = base_conversion.interpret_in_current_base("123")
        self.assertEqual(result, 123.0)

    def test_interpret_hex(self):
        """
        Test interpreting a hex string in HEX mode.
        """
        base_conversion.current_base = "HEX"
        result = base_conversion.interpret_in_current_base("C")  # hex C = 12 decimal
        self.assertEqual(result, 12)

    def test_format_hex(self):
        """
        Test formatting an integer as a hex string.
        """
        base_conversion.current_base = "HEX"
        result = base_conversion.format_in_current_base(255)
        self.assertEqual(result, "FF")  # 255 decimal = FF in hex

    def test_interpret_bin(self):
        """
        Test interpreting a binary string in BIN mode.
        """
        base_conversion.current_base = "BIN"
        result = base_conversion.interpret_in_current_base("1010")  # binary 1010 = 10 decimal
        self.assertEqual(result, 10)

    def test_format_oct(self):
        """
        Test formatting an integer as an octal string.
        """
        base_conversion.current_base = "OCT"
        result = base_conversion.format_in_current_base(64)
        self.assertEqual(result, "100")  # 64 decimal = 100 in oct

    def test_set_base_dec_to_hex(self):
        """
        Test set_base(...) from DEC to HEX using a mock display with '12'.
        '12' in decimal is 12, which should become 'C' in hex.
        """
        # Start in DEC
        base_conversion.current_base = "DEC"
        disp = MockDisplay("12")

        base_conversion.set_base("HEX", disp)
        self.assertEqual(disp.get_entry(), "C")  # 12 decimal -> C in hex
        self.assertEqual(disp.mode, "HEX")

    def test_set_base_hex_to_bin(self):
        """
        Test set_base(...) from HEX to BIN with 'FF'.
        'FF' hex is 255 decimal, which should become '11111111' in binary.
        """
        base_conversion.current_base = "HEX"
        disp = MockDisplay("FF")

        base_conversion.set_base("BIN", disp)
        self.assertEqual(disp.get_entry(), "11111111")
        self.assertEqual(disp.mode, "BIN")

    def test_interpret_empty_string(self):
        base_conversion.current_base = "DEC"
        result = base_conversion.interpret_in_current_base("")
        self.assertEqual(result, 0)

    def test_interpret_invalid_char(self):
        base_conversion.current_base = "HEX"
        with self.assertRaises(ValueError):
            base_conversion.interpret_in_current_base("G")  # invalid in HEX

    def test_format_negative_dec(self):
        base_conversion.current_base = "DEC"
        result = base_conversion.format_in_current_base(-15)
        self.assertEqual(result, "-15")  # or maybe something else if your code handles negatives differently

    def test_format_large_hex(self):
        base_conversion.current_base = "HEX"
        result = base_conversion.format_in_current_base(65535)
        self.assertEqual(result, "FFFF")

    def test_set_base_multiple_switches(self):
        base_conversion.current_base = "DEC"
        disp = MockDisplay("255")
        # DEC -> HEX
        base_conversion.set_base("HEX", disp)
        self.assertEqual(disp.get_entry(), "FF")
        # HEX -> BIN
        base_conversion.set_base("BIN", disp)
        self.assertEqual(disp.get_entry(), "11111111")
        # BIN -> OCT
        base_conversion.set_base("OCT", disp)
        self.assertEqual(disp.get_entry(), "377")

    def test_interpret_float_in_dec(self):
        base_conversion.current_base = "DEC"
        result = base_conversion.interpret_in_current_base("12.5")
        self.assertEqual(result, 12.5)  # if you allow floats

    def test_large_hex_number(self):
        base_conversion.current_base = "HEX"
        large_hex = "FFFFFFFFFFFFFFFF"  # 64-bit max
        result = base_conversion.interpret_in_current_base(large_hex)
        self.assertEqual(result, 0xFFFFFFFFFFFFFFFF)

if __name__ == "__main__":
    unittest.main()
