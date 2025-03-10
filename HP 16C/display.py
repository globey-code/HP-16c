"""
display.py

Pure UI component that shows the current entry, mode, and stack content.
"""

import tkinter as tk
import stack  # If you need stack access for update_stack_content()

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
        self.font = font if font else ("Courier", 18)

        # 1) Outer frame with a white border
        self.frame = tk.Frame(
            master,
            bg="#9C9C9C",
            highlightthickness=border_thickness,  # The thickness of the white border
            highlightbackground="white",          # The color of the border
            relief="flat"
        )
        # Place the frame using the constructor args (x, y, width, height)
        self.frame.place(x=x, y=y, width=width, height=height)

        # 2) Inner text widget, sized to match the frame exactly
        self.widget = tk.Text(
            self.frame,
            bg="#9C9C9C",
            fg="black",
            font=self.font,
            bd=0,                 # No extra border inside
            highlightthickness=0  # No highlight inside the text
        )
        self.widget.place(x=0, y=0, width=width, height=height)
        self.widget.bind("<Key>", lambda e: "break")  # Prevent direct typing

        # (Optional) A mode label at bottom-left
        self.mode_label = tk.Label(self.frame, font=("Courier", 10), bg="#9C9C9C")
        self.mode_label.place(x=3, rely=1.0, anchor="sw", y=-8)

        # (Optional) A stack content label at bottom-right
        if stack_content_config is None:
            stack_content_config = {"relx": 0.99, "rely": 0.92, "anchor": "se"}
        self.stack_content = tk.Label(self.frame, font=("Courier", 10), bg="#9C9C9C")
        self.stack_content.place(**stack_content_config)

        # (Optional) A word size label at top-right
        if word_size_config is None:
            word_size_config = {"relx": 0.99, "rely": 0.02, "anchor": "ne"}
        self.word_size_label = tk.Label(self.frame, font=("Courier", 10), bg="#9C9C9C")
        self.word_size_label.place(**word_size_config)

    def append_entry(self, ch):
        self.raw_value += ch
        self.current_entry = self.raw_value
        self.update()

    def set_entry(self, entry):
        self.current_entry = entry
        self.update()

    def get_entry(self):
        return self.current_entry

    def clear_entry(self):
        self.current_entry = ""
        self.raw_value = ""
        self.update()

    def update(self):
        self.widget.delete("1.0", "end")
        self.widget.insert("1.0", self.current_entry)

    def set_mode(self, mode_str):
        self.mode = mode_str
        self.mode_label.config(text=mode_str)

    def update_stack_content(self):
        """Example: show the current stack state if you have 'stack.py'."""
        s = stack.get_state()
        self.stack_content.config(text=f"Stack: {s}")
