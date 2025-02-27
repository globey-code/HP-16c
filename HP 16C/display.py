"""
display.py
-----------
Provides a modular Display class for the HP 16C Emulator.

This class encapsulates the Tkinter Text widget used to display the
calculator’s stack and current entry, along with helper methods for updating
the display and showing errors.
"""

import tkinter as tk
import stack
import base_conversion

class Display:
    def __init__(self, master, x=20, y=10, width=440, height=100, font=None):
        """
        Initialize the Display widget.

        Parameters:
          master: The parent Tkinter widget.
          x, y, width, height: Geometry parameters.
          font: Optional font setting; defaults to ("Courier", 18) if not provided.
        """
        self.font = font if font is not None else ("Courier", 18)
        self.widget = tk.Text(master, font=self.font, bg="#9C9C9C", fg="#1A1A1A", wrap="none")
        self.widget.tag_configure("right", justify="right")
        self.widget.place(x=x, y=y, width=width, height=height)
        self.current_entry = ""

    def update(self):
        """
        Update the display to show the current four-level stack and the active entry.
        
        The stack is displayed as four registers (R0 to R3), and if there's an active
        entry (i.e. a number being entered), it is shown below the stack.
        """
        self.widget.delete("1.0", "end")
        #regs = stack.stack  # The four-level stack from stack.py
        #for i in range(4):
        #    reg_value = base_conversion.format_in_current_base(regs[i])
        #    self.widget.insert("end", f"R{i}: {reg_value}\n")
        if self.current_entry:
            self.widget.insert("end", "\nEntry: " + self.current_entry)

    def set_entry(self, entry):
        """
        Set the current entry to the given string and update the display.
        """
        self.current_entry = entry
        self.update()

    def append_entry(self, ch):
        self.current_entry += ch
        print("Updated current_entry:", self.current_entry)
        self.update()


    def clear_entry(self):
        """
        Clear the current entry and update the display.
        """
        self.current_entry = ""
        self.update()

    def show_error(self, message, log_message=""):
        """
        Clear the display and show an error message.

        Parameters:
          message: The error message to display.
          log_message: Optional log message to print to the console.
        """
        self.widget.delete("1.0", "end")
        self.widget.insert("end", message)
        if log_message:
            print("Error:", log_message)
