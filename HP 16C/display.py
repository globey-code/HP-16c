"""
display.py

Pure UI component that shows the current entry, mode, and stack content.
Matches HP-16C display behavior per Owner's Handbook (pages 17-19, 43-44).
"""

import tkinter as tk
import tkinter.font as tkFont
import stack  # For word size and stack state

class Display:
    def __init__(self, master, x, y, width, height,
                 border_thickness=1,
                 font=None,
                 stack_content_config=None,
                 word_size_config=None):
        """
        Creates a display area with a white border around it.
        """
        # Define attributes before using them
        self.master = master
        self.current_entry = "0"        # Main display value as a string
        self.raw_value = "0"            # Raw input value as a string
        self.mode = "DEC"               # Display mode ("DEC", "FLOAT", etc.)
        self.current_value = None       # Numeric interpretation of the current entry
        self.error_displayed = False    # Flag to indicate if an error message is displayed
        self.result_displayed = False   # Flag to track if the result has just been shown
        self.show_stack = False         # Toggle for showing stack contents

        # Convert font to a tkFont.Font instance if needed
        if font is None:
            self.font = tkFont.Font(family="Courier", size=18)
        elif isinstance(font, tuple):
            self.font = tkFont.Font(family=font[0], size=font[1])
        else:
            self.font = font

        # Outer frame with a white border
        self.frame = tk.Frame(
            master,
            bg="#9C9C9C",
            highlightthickness=border_thickness,
            highlightbackground="white",
            relief="flat"
        )
        self.frame.place(x=x, y=y, width=width, height=height)

        # Use a Label widget for the main display.
        # This label will always be vertically centered.
        # We set the anchor to "e" to right-align the text.
        self.widget = tk.Label(
            self.frame,
            text=self.current_entry,
            bg="#9C9C9C",
            fg="black",
            font=self.font,
            anchor="e"  # Right aligned horizontally; vertical centering is automatic
        )
        self.widget.place(x=0, y=0, width=width, height=height)
        self.widget.bind("<Key>", lambda e: "break")

        # Mode label at bottom-left
        self.mode_label = tk.Label(self.frame, font=("Courier", 10), bg="#9C9C9C")
        self.mode_label.place(x=3, rely=1.0, anchor="sw", y=-8)

        # Stack content label at bottom-right (hidden by default)
        if stack_content_config is None:
            stack_content_config = {"relx": 0.99, "rely": 0.92, "anchor": "se"}
        self.stack_content = tk.Label(self.frame, font=("Courier", 10), bg="#9C9C9C", text="")
        self.stack_content.place(**stack_content_config)

        # Word size label at top-right
        if word_size_config is None:
            word_size_config = {"relx": 0.99, "rely": 0.02, "anchor": "ne"}
        self.word_size_label = tk.Label(self.frame, font=("Courier", 10), bg="#9C9C9C")
        self.word_size_label.place(**word_size_config)

        # Delay setting the entry until after layout is complete
        self.master.after(10, lambda: self.set_entry("0"))

    def set_entry(self, entry, raw=False):
        """
        Set the display entry.
        If raw is True, treat entry as a literal string (e.g., for error messages)
        and update the display accordingly.
        """
        if raw:
            self.current_entry = entry
            self.widget.config(text=entry, anchor="e")
            self.error_displayed = True
            return

        try:
            if isinstance(entry, str):
                from base_conversion import interpret_in_current_base
                val = interpret_in_current_base(entry, self.mode)
            else:
                val = float(entry) if entry else 0
        except (ValueError, TypeError):
            val = 0
            entry = "0"

        # Apply word size if available; otherwise leave unchanged.
        if hasattr(stack, 'apply_word_size'):
            val = stack.apply_word_size(val)
    
        self.current_value = val  # Store numeric value

        # Format the number based on mode
        if self.mode == "FLOAT":
            entry_str = "{:.9f}".format(val).rstrip("0").rstrip(".")
            if "." not in entry_str:
                entry_str += ".0"
            anchor = "w"  # Left align in FLOAT mode
        elif self.mode in ["HEX", "BIN", "OCT"]:
            val_int = int(val)
            word_size = stack.get_word_size()
            val_int = val_int & ((1 << word_size) - 1)
            if self.mode == "HEX":
                padding = max(0, (word_size + 3) // 4)
                entry_str = format(val_int, f"0{padding}X")
            elif self.mode == "BIN":
                padding = word_size
                entry_str = format(val_int, f"0{padding}b")
            elif self.mode == "OCT":
                padding = max(0, (word_size + 2) // 3)
                entry_str = format(val_int, f"0{padding}o")
            anchor = "e"
        else:  # DEC mode
            entry_str = str(int(val)) if val.is_integer() else "{:.9f}".format(val).rstrip("0").rstrip(".")
            if len(entry_str) > 10:
                entry_str = "9.999999999"
            elif entry_str.startswith("-0"):
                entry_str = "-" + entry_str[2:].lstrip("0") or "0"
            elif entry_str.startswith("0"):
                entry_str = entry_str.lstrip("0") or "0"
            anchor = "e"

        self.current_entry = entry_str
        self.widget.config(text=entry_str, anchor=anchor)
        self.error_displayed = False

    def append_entry(self, ch):
        """
        Append a character to the current entry.
        If an error message is currently displayed, clear it first.
        """
        if self.error_displayed:
            self.clear_entry()
            self.error_displayed = False

        print(f"[DEBUG] append_entry called, result_displayed: {self.result_displayed}, raw_value: {self.raw_value}")
        if self.result_displayed:
            self.raw_value = ch
            self.result_displayed = False
        elif self.raw_value == "0":
            self.raw_value = ch
        else:
            self.raw_value += ch
        self.current_entry = self.raw_value
        self.current_value = None  # Force reinterpretation
        self.set_entry(self.current_entry)

    def get_entry(self):
        return self.current_entry

    def clear_entry(self):
        self.current_entry = "0"
        self.raw_value = "0"
        self.current_value = None
        self.widget.config(text=self.current_entry, anchor="e")

    def set_mode(self, mode_str):
        self.mode = mode_str
        self.mode_label.config(text=mode_str)
        self.set_entry(self.current_value or self.raw_value or 0)

    def update(self):
        self.widget.config(text=self.current_entry, anchor="e")

    def update_stack_content(self):
        complement_mode = stack.get_complement_mode()
        word_size = stack.get_word_size()
        carry_flag = stack.get_carry_flag()

        complement_code = {"UNSIGNED": "00", "1S": "01", "2S": "02"}
        comp_str = complement_code.get(complement_mode, "00")
    
        # Format: "CompCode - WS - Carry"
        formatted_status = f"{comp_str} - {word_size:02d} - {'{:04b}'.format(carry_flag)}"
        self.word_size_label.config(text=comp_str + "-" + str(word_size) + "-" + "{:04b}".format(carry_flag))

    def toggle_stack_display(self, mode=None):
        """Toggle stack display with SHOW command (page 43)."""
        self.show_stack = not self.show_stack
        if self.show_stack and mode:
            stack_state = stack.get_state()
            if mode == "BIN":
                formatted_stack = [format(int(x) & ((1 << stack.get_word_size()) - 1), "b") for x in stack_state]
            elif mode == "OCT":
                formatted_stack = [format(int(x) & ((1 << stack.get_word_size()) - 1), "o") for x in stack_state]
            elif mode == "DEC":
                formatted_stack = [str(int(x)) if x.is_integer() else str(x) for x in stack_state]
            elif mode == "HEX":
                formatted_stack = [format(int(x) & ((1 << stack.get_word_size()) - 1), "X") for x in stack_state]
            else:
                formatted_stack = stack_state
            self.stack_content.config(text=f"Stack: {formatted_stack}")
        else:
            self.stack_content.config(text="")
