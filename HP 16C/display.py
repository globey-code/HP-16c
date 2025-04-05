"""
display.py
Pure UI component that shows the current entry, mode, and stack content.
Matches HP-16C display behavior per the Owner's Handbook.
Refactored to integrate base conversion logic and improve maintainability.
Author: GlobeyCode (original), refactored by ChatGPT
License: MIT
Date: 3/23/2025 (original), refactored 2025-04-01
Dependencies: Python 3.6+, tkinter, stack, logging_config
"""

from typing import Optional, Union, Tuple
import tkinter as tk
import tkinter.font as tkFont
from stack import Stack
from logging_config import logger

class Display:
    def __init__(self, master: tk.Tk, stack: Stack, x: int, y: int, width: int, height: int,
                 border_thickness: int = 1, font: Optional[tkFont.Font] = None,
                 stack_content_config: Optional[dict] = None,
                 word_size_config: Optional[dict] = None) -> None:
        self.stack = stack
        self.master = master
        self.current_entry = "0"
        self.raw_value = ""
        self.mode = "DEC"
        self.is_error_displayed = False
        self.current_value = 0
        self.full_width = width
        self.last_stack_info = ""
        self.error_displayed = False
        self.result_displayed = False
        self.show_stack = False
        self.max_display_chars = 16
        self.display_offset = 0
        self.full_entry = "0"
        self.is_digit_entry = False
        self.decimal_places = None

        self.font = font if font else tkFont.Font(family="Calculator", size=10)
        logger.info(f"Display font set to: family={self.font.actual()['family']}, size={self.font.actual()['size']}")

        self.frame = tk.Frame(master, bg="#9C9C9C", highlightthickness=border_thickness,
                              highlightbackground="white", relief="flat")
        self.frame.place(x=x, y=y, width=width+25, height=height)

        self.widget = tk.Label(self.frame, text=self.current_entry, bg="#9C9C9C", fg="black",
                               font=self.font, anchor="e")
        self.widget.place(x=-25, y=0, width=width-30, height=height-2)
        self.widget.bind("<Key>", lambda e: "break")

        self.float_widget = tk.Label(self.frame, text="", bg="#9C9C9C", fg="black",
                                     font=self.font, anchor="w")
        self.float_widget.place(x=0, y=0, width=width-30, height=height-2)
        self.float_widget.place_forget()

        self.mode_label = tk.Label(self.frame, text=self.get_mode_char(self.mode),
                                   bg="#9C9C9C", fg="black", font=self.font, anchor="center", width=3)
        self.mode_label.place(relx=1.0, rely=0.5, x=-5, anchor="e")

        stack_content_config = stack_content_config or {"relx": 0.01, "rely": 1, "anchor": "sw"}
        self.stack_content = tk.Label(self.frame, font=("Calculator", 12), bg="#9C9C9C", text="")
        self.stack_content.place(**stack_content_config)

        word_size_config = word_size_config or {"relx": 0.99, "rely": 0, "anchor": "ne"}
        self.word_size_label = tk.Label(self.frame, font=("Calculator", 12), bg="#9C9C9C")
        self.word_size_label.place(**word_size_config)
        self.word_size_config = word_size_config

        self.flag_4_label = tk.Label(self.frame, text="C", bg="#9C9C9C", fg="black",
                                     font=("Calculator", 12))
        self.flag_4_label.place(x=width-45, y=height-2, anchor="se")
        self.flag_4_label.place_forget()

        self.flag_5_label = tk.Label(self.frame, text="G", bg="#9C9C9C", fg="black",
                                     font=("Calculator", 12))
        self.flag_5_label.place(x=width-95, y=height-2, anchor="se")
        self.flag_5_label.place_forget()

        self.f_mode_label = tk.Label(self.frame, text="f", bg="#9C9C9C", fg="black",
                                     font=("Calculator", 12))
        self.f_mode_label.place(x=120, y=height-2, anchor="s")
        self.f_mode_label.place_forget()

        self.g_mode_label = tk.Label(self.frame, text="g", bg="#9C9C9C", fg="black",
                                     font=("Calculator", 12))
        self.g_mode_label.place(x=150, y=height-4, anchor="s")
        self.g_mode_label.place_forget()

        self.step_label = tk.Label(self.frame, text="", bg="#9C9C9C", fg="black",
                                   font=self.font, anchor="w")
        self.step_label.place(x=0, y=0, anchor="nw")
        self.step_label.place_forget()

        self.prgm_label = tk.Label(self.frame, text="PRGM", bg="#9C9C9C", fg="black",
                                   font=self.font)
        self.prgm_label.place(relx=0.99, rely=0.5, anchor="e")
        self.prgm_label.place_forget()

        self.master.after(10, lambda: self.set_entry("0"))
        self.update_stack_content()

    def set_base(self, new_base: str) -> None:
        """
        Set the display to a new base, converting the current stack value to the new base's format.
    
        Args:
            new_base (str): The new base to set ("FLOAT", "DEC", "HEX", "BIN", "OCT").
        """
        # Get the current numerical value from the stack (not the raw display value)
        num = self.stack.peek()  # Get the current X register value
        self.current_value = num
        self.set_mode(new_base)
        # Convert the numerical value to the new base's format
        formatted_value = self.stack.format_in_base(num, new_base, pad=False)
        self.raw_value = formatted_value
        self.set_entry(formatted_value, raw=True)
        logger.info(f"Base set to {new_base}, converted value to '{formatted_value}'")

    def set_entry(self, entry: Union[str, Tuple[int, str]], raw: bool = False,
                  program_mode: bool = False, blink: bool = True, is_error: bool = False) -> None:
        """
        Set the display entry, ensuring digits accumulate in raw mode and stack state is reflected otherwise.
        Limits display to max_display_chars (16), showing rightmost 16 digits with scrolling indicators.
        Logs mode indicator changes and the final displayed text.

        Args:
            entry: The value to display (string for raw mode, tuple for program mode, or value to format).
            raw: If True, treat entry as a digit to accumulate.
            program_mode: If True, display as a program step and instruction.
            blink: Whether to blink the display after updating.
            is_error: If True, display the full error message without truncation.
        """
        logger.info(f"Setting entry: value={entry}, raw={raw}, program_mode={program_mode}, blink={blink}, is_error={is_error}")

        if is_error:
            # Display the full error message without applying the character limit
            display_text = str(entry)
            self.widget.config(text=display_text, anchor="w")  # Left-align for readability
            # Optionally hide mode label during error
            self.mode_label.place_forget()
        else:
            if raw:
                # Raw mode: Accumulate digits and enforce rightmost 16-character display
                self.raw_value = str(entry)
                self.full_entry = self.raw_value
                if len(self.full_entry) > self.max_display_chars:
                    visible_text = self.full_entry[-self.max_display_chars:]
                    has_left = True
                    has_right = False  # No scrolling right during digit entry
                else:
                    visible_text = self.full_entry.rjust(self.max_display_chars)
                    has_left = False
                    has_right = False
                logger.info(f"Raw mode: full_entry={self.full_entry}, visible_text={visible_text}, "
                            f"has_left={has_left}, has_right={has_right}")
                self.widget.config(text=visible_text, anchor="e")
                self.widget.place(x=-25, y=0, width=self.full_width-30, height=self.frame.winfo_height()-2)
                self.mode_label.config(text=self.get_mode_char(self.mode, has_left, has_right))
                displayed_text = self.widget.cget("text")
                logger.info(f"Displayed text (widget): '{displayed_text}'")
            elif program_mode:
                # Program mode: Display step and instruction
                step, instruction = entry
                self.full_entry = f"{step:03d}-{instruction}"
                self.step_label.config(text=f"{step:03d}-")
                self.step_label.place(x=5, rely=0.5, anchor="w")
                visible_text = instruction[:self.max_display_chars]
                self.widget.config(text=visible_text, anchor="e")
                self.widget.place(x=0, y=0, width=self.full_width, height=self.frame.winfo_height()-2)
                self.float_widget.place_forget()
                self.prgm_label.config(font=("Calculator", 12))
                self.prgm_label.place(relx=0.99, rely=1, anchor="se")
                self.mode_label.place_forget()
                self.is_error_displayed = False
                self.error_displayed = False
                displayed_text = self.widget.cget("text")
                logger.info(f"Displayed text (widget): '{displayed_text}'")
            else:
                # Default mode: Format and display stack value or provided entry
                self.is_error_displayed = False
                self.error_displayed = False
                self.step_label.place_forget()
                self.prgm_label.place_forget()
                self.word_size_label.place(**self.word_size_config)

                # Determine value to display
                if isinstance(entry, (str, int, float)):
                    try:
                        val = self.stack.interpret_in_base(str(entry), self.mode) if isinstance(entry, str) else (float(entry) if self.mode == "FLOAT" else int(entry))
                    except (ValueError, TypeError):
                        val = self.stack.peek()  # Fallback to current stack value
                else:
                    val = self.stack.peek()  # Use stack's current value if entry is invalid

                self.current_value = val

                # Format based on mode
                if self.mode == "FLOAT":
                    if self.decimal_places is not None:
                        entry_str = f"{val:,.{self.decimal_places}f}"
                    else:
                        entry_str = f"{val:,.9f}".rstrip('0').rstrip('.')
                        if '.' not in entry_str:
                            entry_str += '.0'
                else:
                    val_int = self.stack.apply_word_size(int(val))
                    entry_str = self.stack.format_in_base(val_int, self.mode, pad=False)

                self.full_entry = entry_str
                self.current_entry = entry_str
                self.display_offset = 0  # Reset offset for formatted entries
                visible_text = self.get_visible_text()  # Truncate if needed
                if self.mode == "FLOAT":
                    self.float_widget.config(text=visible_text)
                    self.float_widget.place(x=0, y=0, width=self.full_width-30, height=self.frame.winfo_height()-2)
                    self.widget.place_forget()
                    self.mode_label.place_forget()
                else:
                    self.widget.config(text=visible_text, anchor="e")
                    self.widget.place(x=-25, y=0, width=self.full_width-30, height=self.frame.winfo_height()-2)
                    self.float_widget.place_forget()
                    self.mode_label.place(relx=1.0, rely=0.5, x=-5, anchor="e")
                    has_left = len(self.full_entry) > self.max_display_chars
                    has_right = self.display_offset > 0
                    current_mode_text = self.mode_label.cget("text")
                    new_mode_text = self.get_mode_char(self.mode, has_left, has_right)
                    if current_mode_text != new_mode_text:
                        logger.info(f"Mode indicator changed from '{current_mode_text}' to '{new_mode_text}' "
                                   f"(has_left={has_left}, has_right={has_right})")
                    self.mode_label.config(text=new_mode_text)
                displayed_text = self.widget.cget("text") if not self.mode == "FLOAT" else self.float_widget.cget("text")
                logger.info(f"Displayed text (widget): '{displayed_text}'")
                self.widget.update_idletasks() if not self.mode == "FLOAT" else self.float_widget.update_idletasks()

        if blink and not self.is_digit_entry:
            self.blink()
        self.is_digit_entry = False
        self.update_stack_content()

    def get_visible_text(self) -> str:
        """Get the visible text, ensuring the rightmost max_display_chars are shown."""
        effective_start = len(self.full_entry) - self.max_display_chars - self.display_offset
        if effective_start >= len(self.full_entry):
            return " " * self.max_display_chars
        elif effective_start < 0:
            pad_spaces = -effective_start
            if pad_spaces >= self.max_display_chars:
                return " " * self.max_display_chars
            visible_chars = min(self.max_display_chars - pad_spaces, len(self.full_entry))
            visible_part = self.full_entry[-visible_chars:]  # Always take rightmost characters
            logger.debug(f"get_visible_text: full_entry={self.full_entry}, effective_start={effective_start}, "
                         f"pad_spaces={pad_spaces}, visible_chars={visible_chars}, visible_part={visible_part}")
            return visible_part.ljust(self.max_display_chars)  # Remove left padding, right-justify
        else:
            start = effective_start
            end = min(start + self.max_display_chars, len(self.full_entry))
            visible_text = self.full_entry[start:end]
            logger.debug(f"get_visible_text: full_entry={self.full_entry}, start={start}, end={end}, visible_text={visible_text}")
            return visible_text.ljust(self.max_display_chars)

    def show_f_mode(self) -> None:
        self.f_mode_label.place(x=120, y=self.frame.winfo_height()-2, anchor="s")
        logger.info("f-mode indicator shown")

    def hide_f_mode(self) -> None:
        self.f_mode_label.place_forget()
        self.master.update_idletasks()
        logger.info("f-mode indicator hidden")

    def show_g_mode(self) -> None:
        self.g_mode_label.place(x=150, y=self.frame.winfo_height()-4, anchor="s")
        logger.info("g-mode indicator shown")

    def hide_g_mode(self) -> None:
        self.g_mode_label.place_forget()
        logger.info("g-mode indicator hidden")

    def blink(self) -> None:
        if self.is_error_displayed:
            return
        current_text = self.widget.cget("text")
        current_anchor = self.widget.cget("anchor")
        mode_text = self.mode_label.cget("text") if self.mode_label.winfo_ismapped() else None
        prgm_text = self.prgm_label.cget("text") if self.prgm_label.winfo_ismapped() else None
        step_text = self.step_label.cget("text") if self.step_label.winfo_ismapped() else None
        flag_5_text = self.flag_5_label.cget("text") if self.flag_5_label.winfo_ismapped() else None
        flag_4_text = self.flag_4_label.cget("text") if self.flag_4_label.winfo_ismapped() else None
        word_size_text = self.word_size_label.cget("text") if self.word_size_label.winfo_ismapped() else None
        f_mode_text = self.f_mode_label.cget("text") if self.f_mode_label.winfo_ismapped() else None
        g_mode_text = self.g_mode_label.cget("text") if self.g_mode_label.winfo_ismapped() else None

        self.widget.config(text="")
        if mode_text: self.mode_label.config(text="")
        if prgm_text: self.prgm_label.config(text="")
        if step_text: self.step_label.config(text="")
        if flag_5_text: self.flag_5_label.config(text="")
        if flag_4_text: self.flag_4_label.config(text="")
        if word_size_text: self.word_size_label.config(text="")
        if f_mode_text: self.f_mode_label.config(text="")
        if g_mode_text: self.g_mode_label.config(text="")

        def restore() -> None:
            self.widget.config(text=current_text, anchor=current_anchor)
            if mode_text: self.mode_label.config(text=mode_text)
            if prgm_text: self.prgm_label.config(text=prgm_text)
            if step_text: self.step_label.config(text=step_text)
            if flag_5_text: self.flag_5_label.config(text=flag_5_text)
            if flag_4_text: self.flag_4_label.config(text=flag_4_text)
            if word_size_text: self.word_size_label.config(text=word_size_text)
            if f_mode_text: self.f_mode_label.config(text=f_mode_text)
            if g_mode_text: self.g_mode_label.config(text=g_mode_text)
        self.master.after(100, restore)
        logger.info("All visible display elements blinked")

    def get_mode_char(self, mode: str, has_left: bool = False, has_right: bool = False) -> str:
        mode_map = {"HEX": "h", "DEC": "d", "OCT": "o", "BIN": "b", "FLOAT": "f"}
        base_char = mode_map.get(mode, "d")
        if has_left and has_right:
            return f".{base_char}."
        elif has_left:
            return f".{base_char} "
        elif has_right:
            return f" {base_char}."
        return f" {base_char} "

    def set_error(self, error_message: str) -> None:
        self.is_error_displayed = True
        self.error_displayed = True
        self.widget.config(text=error_message, anchor="e")
        self.mode_label.place_forget()
        self.step_label.place_forget()
        self.prgm_label.place_forget()
        self.flag_4_label.place_forget()
        self.flag_5_label.place_forget()
        self.widget.place(x=0, y=0, width=self.full_width-30, height=self.frame.winfo_height()-2)
        logger.info(f"Error displayed: {error_message}")
        self.master.after(3000, self.reset_error)

    def reset_error(self) -> None:
        if self.is_error_displayed:
            self.is_error_displayed = False
            self.error_displayed = False
            self.display_offset = len(self.full_entry) - self.max_display_chars if len(self.full_entry) > self.max_display_chars else 0
            visible_text = self.full_entry[:self.max_display_chars]
            if self.mode == "FLOAT":
                self.float_widget.config(text=visible_text)
                self.float_widget.place(x=0, y=0, width=self.full_width-30, height=self.frame.winfo_height()-2)
                self.widget.place_forget()
                self.mode_label.place_forget()
            else:
                self.widget.config(text=visible_text, anchor="e")
                self.widget.place(x=-25, y=0, width=self.full_width-30, height=self.frame.winfo_height()-2)
                self.float_widget.place_forget()
                self.mode_label.place(relx=1.0, rely=0.5, x=-5, anchor="e")
                has_left = len(self.full_entry) > self.max_display_chars and self.display_offset < (len(self.full_entry) - self.max_display_chars)
                has_right = self.display_offset > 0
                self.mode_label.config(text=self.get_mode_char(self.mode, has_left, has_right))
            self.update_stack_content()
            logger.info("Error cleared, display reset to previous value")

    def get_visible_text(self) -> str:
        effective_start = len(self.full_entry) - self.max_display_chars - self.display_offset
        if effective_start >= len(self.full_entry):
            return " " * self.max_display_chars
        elif effective_start < 0:
            pad_spaces = -effective_start
            if pad_spaces >= self.max_display_chars:
                return " " * self.max_display_chars
            else:
                visible_chars = self.max_display_chars - pad_spaces
                visible_part = self.full_entry[:min(len(self.full_entry), visible_chars)]
                return (" " * pad_spaces + visible_part).rjust(self.max_display_chars)
        else:
            start = effective_start
            end = min(start + self.max_display_chars, len(self.full_entry))
            visible_text = self.full_entry[start:end]
            return visible_text.rjust(self.max_display_chars)

    def scroll_right(self) -> None:
        self.display_offset += 1
        visible_text = self.get_visible_text()
        anchor = "e" if self.mode != "FLOAT" else "w"
        self.widget.config(text=visible_text, anchor=anchor)
        self.widget.place(x=-25, y=0, width=self.full_width-30, height=self.frame.winfo_height()-2)
        has_left = len(self.full_entry) > self.max_display_chars and self.display_offset < (len(self.full_entry) - self.max_display_chars)
        has_right = self.display_offset > 0
        self.mode_label.config(text=self.get_mode_char(self.mode, has_left, has_right))
        logger.info(f"Scrolled right: offset={self.display_offset}, text='{visible_text}'")

    def scroll_left(self) -> None:
        if self.display_offset > 0:
            self.display_offset -= 1
            visible_text = self.get_visible_text()
            anchor = "e" if self.mode != "FLOAT" else "w"
            self.widget.config(text=visible_text, anchor=anchor)
            self.widget.place(x=-25, y=0, width=self.full_width-30, height=self.frame.winfo_height()-2)
            has_left = len(self.full_entry) > self.max_display_chars and self.display_offset < (len(self.full_entry) - self.max_display_chars)
            has_right = self.display_offset > 0
            self.mode_label.config(text=self.get_mode_char(self.mode, has_left, has_right))
            logger.info(f"Scrolled left: offset={self.display_offset}, text='{visible_text}'")

    def clear_entry(self) -> None:
        logger.info("Clearing entry")
        self.current_entry = "0"
        self.raw_value = ""
        self.current_value = 0
        self.widget.config(text=self.current_entry, anchor="e")
        self.error_displayed = False
        self.result_displayed = False

    def append_entry(self, ch: str) -> None:
        logger.info(f"Appending character: {ch}")
        if self.error_displayed:
            self.clear_entry()
        if self.result_displayed or not self.raw_value:
            self.raw_value = ch
        else:
            self.raw_value += ch
        self.is_digit_entry = True
        self.set_entry(self.raw_value, raw=True, blink=False)

    def get_entry(self) -> str:
        return self.current_entry

    def set_mode(self, mode_str: str) -> None:
        """Set the display mode."""
        logger.info(f"Setting mode: {mode_str}")
        self.mode = mode_str
        self.mode_label.config(text=self.get_mode_char(mode_str))
        self.update_stack_content()

    def update(self) -> None:
        start = self.display_offset
        end = start + self.max_display_chars
        visible_text = self.full_entry[start:end]
        self.widget.config(text=visible_text)

    def update_stack_content(self) -> None:
        complement_mode = self.stack.get_complement_mode()
        word_size = self.stack.get_word_size()
        flags_bitfield = self.stack.get_flags_bitfield()
        complement_code = {"UNSIGNED": "00", "1S": "01", "2S": "02"}
        comp_str = complement_code.get(complement_mode, "00")
        stack_info = f"{comp_str}-{word_size:02d}-{flags_bitfield:04b}"
        self.word_size_label.config(text=stack_info)
        self.word_size_label.place(**self.word_size_config)
        if stack_info != self.last_stack_info:
            logger.info(f"Stack info updated: {stack_info}")
            self.last_stack_info = stack_info
        # Show Carry flag (C)
        if self.stack.test_flag(4):
            self.flag_4_label.place(x=self.full_width-45, y=self.frame.winfo_height()-2, anchor="se")
        else:
            self.flag_4_label.place_forget()
        if self.stack.test_flag(5):
            self.flag_5_label.place(x=self.full_width-95, y=self.frame.winfo_height()-2, anchor="se")
        else:
            self.flag_5_label.place_forget()

    def toggle_stack_display(self, mode: Optional[str] = None) -> None:
        logger.info(f"Toggling stack display: show={not self.show_stack}, mode={mode}")
        self.show_stack = not self.show_stack
        if self.show_stack and mode:
            stack_state = self.stack.get_state()
            word_size = self.stack.get_word_size()
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
                    if self.stack.get_complement_mode() == "1S" and x_int & (1 << (word_size - 1)):
                        x_display = -((~x_int) & mask)
                    elif self.stack.get_complement_mode() == "2S" and x_int & (1 << (word_size - 1)):
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