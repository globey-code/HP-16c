"""
display.py

Pure UI component that shows the current entry, mode, and stack content.
Matches HP-16C display behavior per Owner's Handbook.
"""

import tkinter as tk
import tkinter.font as tkFont
import stack
from base_conversion import interpret_in_current_base, current_base
from logging_config import logger

class Display:
    def __init__(self, master, x, y, width, height, border_thickness=1, font=None, stack_content_config=None, word_size_config=None):
        logger.info(f"Initializing Display: x={x}, y={y}, width={width}, height={height}")
        self.master = master
        self.current_entry = "0"
        self.raw_value = "0"
        self.mode = "DEC"
        self.current_value = None
        self.error_displayed = False
        self.result_displayed = False
        self.show_stack = False
        self.last_stack_info = None

        if font is None:
            self.font = tkFont.Font(family="Courier", size=18)
        elif isinstance(font, tuple):
            self.font = tkFont.Font(family=font[0], size=font[1])
        else:
            self.font = font

        self.frame = tk.Frame(master, bg="#9C9C9C", highlightthickness=border_thickness, highlightbackground="white", relief="flat")
        self.frame.place(x=x, y=y, width=width, height=height)

        self.widget = tk.Label(self.frame, text=self.current_entry, bg="#9C9C9C", fg="black", font=self.font, anchor="e")
        self.widget.place(x=0, y=0, width=width-30, height=height-2)
        self.widget.bind("<Key>", lambda e: "break")

        self.mode_label = tk.Label(self.frame, text=self.get_mode_char(self.mode), bg="#9C9C9C", fg="black", font=("Courier", 16), anchor="e")
        self.mode_label.place(relx=1.0, rely=0.5, x=-5, anchor="e")

        stack_content_config = stack_content_config or {"relx": 0.99, "rely": 1, "anchor": "se"}
        self.stack_content = tk.Label(self.frame, font=("Courier", 10), bg="#9C9C9C", text="")
        self.stack_content.place(**stack_content_config)

        word_size_config = word_size_config or {"relx": 0.99, "rely": 0, "anchor": "ne"}
        self.word_size_label = tk.Label(self.frame, font=("Courier", 10), bg="#9C9C9C")
        self.word_size_label.place(**word_size_config)

        self.master.after(10, lambda: self.set_entry("0"))
        self.update_stack_content()
        logger.info(f"Display initialized: mode={self.mode}, entry={self.current_entry}")

    def get_mode_char(self, mode):
        """Return the mode character for display."""
        mode_map = {"HEX": "h", "DEC": "d", "OCT": "o", "BIN": "b", "FLOAT": "f"}
        return mode_map.get(mode, "d")

    def set_entry(self, entry, raw=False):
        """Set the display entry, formatting based on mode."""
        logger.info(f"Setting entry: value={entry}, raw={raw}")
        if raw:
            self.current_entry = entry
            self.widget.config(text=entry, anchor="e")
            self.error_displayed = True
            logger.info(f"Raw entry set: {entry}")
            logger.info("Scheduling reset in 1 second")
            self.master.after(1000, lambda: self.clear_entry())
            return

        try:
            if isinstance(entry, str):
                val = interpret_in_current_base(entry, self.mode)
            else:
                val = float(entry) if self.mode == "FLOAT" else int(entry or 0)
        except (ValueError, TypeError):
            val = 0
            entry = "0"

        if self.mode == "FLOAT":
            entry_str = "{:.9f}".format(val).rstrip("0").rstrip(".")
            if "." not in entry_str:
                entry_str += ".0"
            anchor = "w"
        else:
            val_int = stack.apply_word_size(int(val))
            word_size = stack.get_word_size()
            if self.mode == "HEX":
                padding = max(0, (word_size + 3) // 4)
                entry_str = format(val_int, f"0{padding}X").lower()
            elif self.mode == "BIN":
                entry_str = format(val_int, f"0{word_size}b")
            elif self.mode == "OCT":
                padding = max(0, (word_size + 2) // 3)
                entry_str = format(val_int, f"0{padding}o")
            else:  # DEC
                complement_mode = stack.get_complement_mode()
                if complement_mode == "UNSIGNED":
                    entry_str = str(val_int)
                elif complement_mode == "1S" and val_int & (1 << (word_size - 1)):
                    entry_str = str(-((~val_int) & ((1 << word_size) - 1)))
                elif complement_mode == "2S" and val_int & (1 << (word_size - 1)):
                    entry_str = str(val_int - (1 << word_size))
                else:
                    entry_str = str(val_int)
            anchor = "e"

            max_length = word_size if self.mode in ("BIN", "OCT") else (word_size // 4 if self.mode == "HEX" else 10)
            if len(entry_str) > max_length and self.mode != "FLOAT":
                entry_str = "Error"
                self.error_displayed = True
                logger.info("Scheduling reset in 1 second")
                self.master.after(1000, lambda: self.clear_entry())
            else:
                self.error_displayed = False

        self.current_entry = entry_str
        self.current_value = val if self.mode == "FLOAT" else val_int
        self.widget.config(text=entry_str, anchor=anchor)
        logger.info(f"Entry set: {entry_str}, value={self.current_value}")

    def append_entry(self, ch):
        """Append a character to the current entry."""
        logger.info(f"Appending character: {ch}")
        if self.error_displayed:
            self.clear_entry()
        if self.result_displayed or self.raw_value == "0":
            self.raw_value = ch
        else:
            self.raw_value += ch
        try:
            self.current_value = interpret_in_current_base(self.raw_value, self.mode)
            self.set_entry(self.current_value)
        except ValueError:
            self.current_value = 0
            self.set_entry("0")

    def get_entry(self):
        """Get the current display entry."""
        return self.current_entry

    def clear_entry(self):
        """Clear the current entry."""
        logger.info("Clearing entry")
        self.current_entry = "0"
        self.raw_value = "0"
        self.current_value = 0
        self.widget.config(text=self.current_entry, anchor="e")
        self.error_displayed = False
        self.result_displayed = False

    def set_mode(self, mode_str):
        """Set the display mode and refresh the entry."""
        logger.info(f"Setting mode: {mode_str}")
        self.mode = mode_str
        self.mode_label.config(text=self.get_mode_char(mode_str))
        self.set_entry(self.current_value or self.raw_value or 0)

    def update(self):
        """Refresh the display widget."""
        self.widget.config(text=self.current_entry)

    def update_stack_content(self):
        """Update the stack content display with word size, complement mode, and carry flag, logging only on change."""
        complement_mode = stack.get_complement_mode()
        word_size = stack.get_word_size()
        carry_flag = stack.get_carry_flag()
        complement_code = {"UNSIGNED": "00", "1S": "01", "2S": "02"}
        comp_str = complement_code.get(complement_mode, "00")
        stack_info = f"{comp_str}-{word_size:02d}-{carry_flag:04d}"
        if stack_info != self.last_stack_info:
            self.word_size_label.config(text=stack_info)
            logger.info(f"Stack info updated: {stack_info}")
            self.last_stack_info = stack_info

    def toggle_stack_display(self, mode=None):
        """Toggle the stack display visibility."""
        logger.info(f"Toggling stack display: show={not self.show_stack}, mode={mode}")
        self.show_stack = not self.show_stack
        if self.show_stack and mode:
            stack_state = stack.get_state()  # [X, Y, Z, T]
            word_size = stack.get_word_size()
            mask = (1 << word_size) - 1
            if mode == "BIN":
                formatted_stack = [format(int(x) & mask, f"0{word_size}b") for x in stack_state]
            elif mode == "OCT":
                padding = max(0, (word_size + 2) // 3)
                formatted_stack = [format(int(x) & mask, f"0{padding}o") for x in stack_state]
            elif mode == "DEC":
                formatted_stack = []
                for x in stack_state:
                    x_int = int(x) & mask
                    if stack.get_complement_mode() == "1S" and x_int & (1 << (word_size - 1)):
                        x_display = -((~x_int) & mask)
                    elif stack.get_complement_mode() == "2S" and x_int & (1 << (word_size - 1)):
                        x_display = x_int - (1 << word_size)
                    else:
                        x_display = x_int
                    formatted_stack.append(str(x_display))
            elif mode == "HEX":
                padding = max(0, (word_size + 3) // 4)
                formatted_stack = [format(int(x) & mask, f"0{padding}X").lower() for x in stack_state]
            elif mode == "FLOAT":
                formatted_stack = [f"{float(x):.9f}".rstrip("0").rstrip(".") for x in stack_state]
            else:
                formatted_stack = [str(x) for x in stack_state]
            self.stack_content.config(text=f"Stack: {formatted_stack}")
            logger.info(f"Stack displayed: {formatted_stack}")
        else:
            self.stack_content.config(text="")
            logger.info("Stack display hidden")