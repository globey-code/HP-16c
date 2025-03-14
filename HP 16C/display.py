"""
display.py

Pure UI component that shows the current entry, mode, and stack content.
Matches HP-16C display behavior per Owner's Handbook (pages 17-19, 43-44).
"""

import tkinter as tk
import stack  # For word size and stack state

class Display:
    def __init__(self, master, x, y, width, height,
                 border_thickness=1,
                 font=None,
                 stack_content_config=None,
                 word_size_config=None):
        """
        Creates a display area with a white border around it.
        Move or resize by changing (x, y, width, height).
        """
        self.master = master
        self.current_entry = "0"
        self.raw_value = "0"
        self.mode = "DEC"
        self.current_value = None
        self.font = font if font else ("Courier", 18)
        self.result_displayed = False
        self.show_stack = False  # Toggle stack display with SHOW

        # Outer frame with a white border
        self.frame = tk.Frame(
            master,
            bg="#9C9C9C",
            highlightthickness=border_thickness,
            highlightbackground="white",
            relief="flat"
        )
        self.frame.place(x=x, y=y, width=width, height=height)

        # Inner text widget for main display
        self.widget = tk.Text(
            self.frame,
            bg="#9C9C9C",
            fg="black",
            font=self.font,
            bd=0,
            highlightthickness=0
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

    def append_entry(self, ch):
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

    def set_entry(self, entry):
        """Set display entry with HP-16C formatting (pages 17-19, 43-44)."""
        try:
            # Interpret entry as a number based on current mode
            if isinstance(entry, str):
                from base_conversion import interpret_in_current_base
                val = interpret_in_current_base(entry, self.mode)
            else:
                val = float(entry) if entry else 0
        except (ValueError, TypeError):
            val = 0
            entry = "0"

        # Apply word size and complement mode
        val = stack.apply_word_size(val)
        self.current_value = val  # Store numeric value

        # Mode-specific formatting
        if self.mode == "FLOAT":
            entry_str = "{:.9f}".format(val).rstrip("0").rstrip(".")
        elif self.mode in ["HEX", "BIN", "OCT"]:
            val_int = int(val)
            word_size = stack.get_word_size()
            val_int = val_int & ((1 << word_size) - 1)  # Mask to word size
            if self.mode == "HEX":
                padding = max(0, (word_size + 3) // 4)
                entry_str = format(val_int, f"0{padding}X")
            elif self.mode == "BIN":
                padding = word_size
                entry_str = format(val_int, f"0{padding}b")
            elif self.mode == "OCT":
                padding = max(0, (word_size + 2) // 3)
                entry_str = format(val_int, f"0{padding}o")
        else:  # DEC mode
            entry_str = str(int(val)) if val.is_integer() else "{:.9f}".format(val).rstrip("0").rstrip(".")
            if len(entry_str) > 10:
                entry_str = "9.999999999"
            elif entry_str.startswith("-0"):
                entry_str = "-" + entry_str[2:].lstrip("0") or "0"
            elif entry_str.startswith("0"):
                entry_str = entry_str.lstrip("0") or "0"

        self.current_entry = entry_str
        self.widget.delete("1.0", "end")
        self.widget.insert("1.0", self.current_entry)

    def get_entry(self):
        return self.current_entry

    def clear_entry(self):
        self.current_entry = "0"
        self.raw_value = "0"
        self.current_value = None
        self.widget.delete("1.0", "end")
        self.widget.insert("1.0", self.current_entry)

    def set_mode(self, mode_str):
        self.mode = mode_str
        self.mode_label.config(text=mode_str)
        # Reformat the current value immediately
        self.set_entry(self.current_value or self.raw_value or 0)

    def update(self):
        self.widget.delete("1.0", "end")
        self.widget.insert("1.0", self.current_entry)

    def update_stack_content(self):
        """Show stack state if enabled by SHOW (page 43)."""
        if self.show_stack:
            stack_state = stack.get_state()
            self.stack_content.config(text=f"Stack: {stack_state}")
        self.word_size_label.config(text=f"WS: {stack.get_word_size()} bits")
        self.mode_label.config(text=self.mode)

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