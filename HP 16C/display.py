# display.py
# Pure UI component that shows the current entry, mode, and stack content.
# Matches HP-16C display behavior per Owner's Handbook.
# Author: GlobeyCode
# License: MIT
# Date: 3/23/2025
# Dependencies: Python 3.6+, HP-16C emulator modules (tkinter, stack, traceback, error)

import tkinter as tk
import tkinter.font as tkFont
import stack
import traceback
import error
from base_conversion import interpret_in_base, format_in_current_base
from logging_config import logger

class Display:
    def __init__(self, master, x, y, width, height, border_thickness=1, font=None, stack_content_config=None, word_size_config=None):
        """Initialize the Display component."""
        logger.info(f"Initializing Display: x={x}, y={y}, width={width}, height={height}")
        self.master = master
        self.current_entry = "0"
        self.raw_value = "0"
        self.mode = "DEC"
        self.is_error_displayed = False
        self.current_value = 0
        self.full_width = width
        self.last_stack_info = ""  # To fix AttributeError
        self.error_displayed = False
        self.result_displayed = False
        self.show_stack = False
        self.max_display_chars = 32
        self.display_offset = 0
        self.full_entry = "0"

        if font is None:
            self.font = tkFont.Font(family="Courier", size=18)
        elif isinstance(font, tuple):
            self.font = tkFont.Font(family=font[0], size=font[1])
        else:
            self.font = font

        self.frame = tk.Frame(master, bg="#9C9C9C", highlightthickness=border_thickness, highlightbackground="white", relief="flat")
        self.frame.place(x=x, y=y, width=width+25, height=height)

        self.widget = tk.Label(self.frame, text=self.current_entry, bg="#9C9C9C", fg="black", font=self.font, anchor="e")
        self.widget.place(x=-25, y=0, width=width-30, height=height-2)
        self.widget.bind("<Key>", lambda e: "break")

        self.mode_label = tk.Label(self.frame, text=self.get_mode_char(self.mode), bg="#9C9C9C", fg="black", 
                                   font=("Courier", 16), anchor="center", width=3)
        self.mode_label.place(relx=1.0, rely=0.5, x=-5, anchor="e")

        stack_content_config = stack_content_config or {"relx": 0.01, "rely": 1, "anchor": "sw"}
        self.stack_content = tk.Label(self.frame, font=("Courier", 10), bg="#9C9C9C", text="")
        self.stack_content.place(**stack_content_config)

        word_size_config = word_size_config or {"relx": 0.99, "rely": 0, "anchor": "ne"}
        self.word_size_label = tk.Label(self.frame, font=("Courier", 10), bg="#9C9C9C")
        self.word_size_label.place(**word_size_config)

        self.master.after(10, lambda: self.set_entry("0"))
        self.update_stack_content()  # This should now work

        self.step_label = tk.Label(self.frame, text="", bg="#9C9C9C", fg="black", font=("Courier", 16), anchor="w")
        self.step_label.place(x=0, y=0, anchor="nw")
        self.step_label.place_forget()

        self.prgm_label = tk.Label(self.frame, text="PRGM", bg="#9C9C9C", fg="black", font=("Courier", 10))
        self.prgm_label.place(relx=0.99, rely=0.5, anchor="e")
        self.prgm_label.place_forget()

    def get_mode_char(self, mode, has_left=False, has_right=False):
        mode_map = {"HEX": "h", "DEC": "d", "OCT": "o", "BIN": "b", "FLOAT": "f"}
        base_char = mode_map.get(mode, "d")
        if has_left and has_right:
            return f".{base_char}."  # ".b."
        elif has_left:
            return f".{base_char} "  # ".b "
        elif has_right:
            return f" {base_char}."  # " b."
        return f" {base_char} "  # " b "

    def set_error(self, error_message):
        """Set the display to show an error message temporarily."""
        self.is_error_displayed = True
        self.error_displayed = True
        self.widget.config(text=error_message, anchor="e")
        self.mode_label.place_forget()
        self.step_label.place_forget()
        self.prgm_label.place_forget()
        self.widget.place(x=0, y=0, width=self.full_width-30, height=self.frame.winfo_height()-2)
        logger.info(f"Error displayed: {error_message}")
        self.master.after(3000, self.reset_error)

    def reset_error(self):
        """Reset the display to the previous value after an error."""
        if self.is_error_displayed:
            self.is_error_displayed = False
            self.error_displayed = False
            if len(self.full_entry) > self.max_display_chars:
                self.display_offset = len(self.full_entry) - self.max_display_chars
            else:
                self.display_offset = 0
            start = self.display_offset
            end = start + self.max_display_chars
            visible_text = self.full_entry[start:end]
            anchor = "e" if self.mode != "FLOAT" else "w"
            self.widget.config(text=visible_text, anchor=anchor)
            self.widget.place(x=-5, y=0, width=self.full_width-30, height=self.frame.winfo_height()-2)
            self.mode_label.place(relx=1.0, rely=0.5, x=-5, anchor="e")
            self.step_label.place_forget()
            self.prgm_label.place_forget()
            has_left = self.display_offset > 0
            has_right = end < len(self.full_entry)
            self.mode_label.config(text=self.get_mode_char(self.mode, has_left, has_right))
            logger.info("Error cleared, display reset to previous value")

    def get_visible_text(self):
        """Calculate the visible text based on the current display offset."""
        effective_start = len(self.full_entry) - self.max_display_chars - self.display_offset
        if effective_start >= len(self.full_entry):
            # Entire display is past the string (all spaces)
            return " " * self.max_display_chars
        elif effective_start < 0:
            # Display window is partially or fully before the string
            pad_spaces = -effective_start
            if pad_spaces >= self.max_display_chars:
                # Entire display is before the string (all spaces)
                return " " * self.max_display_chars
            else:
                # Show leading spaces followed by the start of the string
                visible_chars = self.max_display_chars - pad_spaces
                visible_part = self.full_entry[:min(len(self.full_entry), visible_chars)]
                return (" " * pad_spaces + visible_part).rjust(self.max_display_chars)
        else:
            # Display window is within the string
            start = effective_start
            end = min(start + self.max_display_chars, len(self.full_entry))
            visible_text = self.full_entry[start:end]
            return visible_text.rjust(self.max_display_chars)

    def set_entry(self, entry, raw=False, program_mode=False):
        """Set the display entry and initialize the visible text."""
        logger.info(f"Setting entry: value={entry}, raw={raw}, program_mode={program_mode}")
        if raw:
            self.is_error_displayed = True
            self.error_displayed = True
            self.full_entry = entry
            self.display_offset = 0
            visible_text = entry[:self.max_display_chars]
            self.widget.config(text=visible_text, anchor="w")
            self.widget.place(x=-5, y=0, width=self.full_width-30, height=self.frame.winfo_height()-2)
            self.mode_label.place_forget()
            self.step_label.place_forget()
            self.prgm_label.place_forget()
            self.master.after(3000, self.reset_error)
        elif program_mode:
            step, instruction = entry
            self.full_entry = f"{step:03d}-{instruction}"
            self.step_label.config(text=f"{step:03d}-")
            self.step_label.place(x=5, rely=0.5, anchor="w")
            visible_text = instruction[:self.max_display_chars]
            self.widget.config(text=visible_text, anchor="e")
            self.widget.place(x=-15, y=0, width=self.full_width, height=self.frame.winfo_height()-2)
            self.prgm_label.place(relx=0.99, rely=1, anchor="se")
            self.mode_label.place_forget()
            self.is_error_displayed = False
            self.error_displayed = False
        else:
            self.is_error_displayed = False
            self.error_displayed = False
            self.step_label.place_forget()
            self.prgm_label.place_forget()
            self.mode_label.place(relx=1.0, rely=0.5, x=-5, anchor="e")

            try:
                if isinstance(entry, str):
                    val = interpret_in_base(entry, self.mode)
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
                self.current_value = val
            else:
                val_int = stack.apply_word_size(int(val))
                if val_int == 0:
                    entry_str = "0"
                else:
                    entry_str = format_in_current_base(val_int, self.mode, pad=False)
                anchor = "e"
                self.current_value = val_int

            self.full_entry = entry_str
            self.current_entry = entry_str
            self.display_offset = 0  # Start with no digits hidden on the right
            visible_text = self.get_visible_text()
            self.widget.config(text=visible_text, anchor=anchor)
            self.widget.place(x=-5, y=0, width=self.full_width-30, height=self.frame.winfo_height()-2)

            # Update mode label with scroll indicators
            has_left = len(self.full_entry) > self.max_display_chars and self.display_offset < (len(self.full_entry) - self.max_display_chars)
            has_right = self.display_offset > 0
            self.mode_label.config(text=self.get_mode_char(self.mode, has_left, has_right))

            self.raw_value = entry_str
            logger.info(f"Display in {self.mode} mode: '{self.full_entry}'")

    def scroll_right(self):
        """Scroll the display one character to the right (hides right digits, shifts left)."""
        self.display_offset += 1  # Allow indefinite scrolling right
        visible_text = self.get_visible_text()
        anchor = "e" if self.mode != "FLOAT" else "w"
        self.widget.config(text=visible_text, anchor=anchor)
        self.widget.place(x=-5, y=0, width=self.full_width-30, height=self.frame.winfo_height()-2)
        has_left = len(self.full_entry) > self.max_display_chars and self.display_offset < (len(self.full_entry) - self.max_display_chars)
        has_right = self.display_offset > 0
        self.mode_label.config(text=self.get_mode_char(self.mode, has_left, has_right))
        logger.info(f"Scrolled right: offset={self.display_offset}, text='{visible_text}'")

    def scroll_left(self):
        """Scroll the display one character to the left (reveals right digits, shifts right)."""
        if self.display_offset > 0:  # Stop at initial position
            self.display_offset -= 1
            visible_text = self.get_visible_text()
            anchor = "e" if self.mode != "FLOAT" else "w"
            self.widget.config(text=visible_text, anchor=anchor)
            self.widget.place(x=-5, y=0, width=self.full_width-30, height=self.frame.winfo_height()-2)
            has_left = len(self.full_entry) > self.max_display_chars and self.display_offset < (len(self.full_entry) - self.max_display_chars)
            has_right = self.display_offset > 0
            self.mode_label.config(text=self.get_mode_char(self.mode, has_left, has_right))
            logger.info(f"Scrolled left: offset={self.display_offset}, text='{visible_text}'")

    def clear_entry(self):
        """Clear the current entry."""
        logger.info("Clearing entry")
        self.current_entry = "0"
        self.raw_value = "0"
        self.current_value = 0
        self.widget.config(text=self.current_entry, anchor="e")
        self.error_displayed = False
        self.result_displayed = False

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
            self.current_value = interpret_in_base(self.raw_value, self.mode)
            self.set_entry(self.current_value)
        except ValueError:
            self.current_value = 0
            self.set_entry("0")

    def get_entry(self):
        """Get the current display entry."""
        return self.current_entry

    def set_mode(self, mode_str):
        """Set the display mode and refresh the entry."""
        logger.info(f"Setting mode: {mode_str}")
        self.mode = mode_str
        self.mode_label.config(text=self.get_mode_char(mode_str))
        self.set_entry(self.current_value or self.raw_value or 0)

    def update(self):
        """Refresh the display widget."""
        start = self.display_offset
        end = start + self.max_display_chars
        visible_text = self.full_entry[start:end]
        self.widget.config(text=visible_text)

    def update_stack_content(self):
        """Update the stack content display with word size, complement mode, and flags 0-3 as binary."""
        complement_mode = stack.get_complement_mode()
        word_size = stack.get_word_size()
        flags_bitfield = stack.get_flags_bitfield()  # This should now work
        complement_code = {"UNSIGNED": "00", "1S": "01", "2S": "02"}
        comp_str = complement_code.get(complement_mode, "00")
        # Format flags as 4-digit binary
        stack_info = f"{comp_str}-{word_size:02d}-{flags_bitfield:04b}"
    
        if stack_info != self.last_stack_info:
            self.word_size_label.config(text=stack_info)
            # Assuming logger is defined elsewhere
            logger.info(f"Stack info updated: {stack_info}")
            self.last_stack_info = stack_info

    def toggle_stack_display(self, mode=None):
        """Toggle the stack display visibility."""
        logger.info(f"Toggling stack display: show={not self.show_stack}, mode={mode}")
        self.show_stack = not self.show_stack
        if self.show_stack and mode:
            stack_state = stack.get_state()
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