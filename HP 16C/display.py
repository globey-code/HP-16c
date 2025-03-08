import tkinter as tk
import stack
from keyboard_input import restrict_input

class Display:
    def __init__(self, master, x, y, width, height, font=None, stack_label_config=None):
        self.master = master
        self.current_entry = ""
        self.raw_value = ""          # Store the original decimal entry here.
        self.mode = "DEC"            # Current mode: DEC by default.
        self.font = font if font is not None else ("Courier", 18)

        self.frame = tk.Frame(master, bg="#9C9C9C")
        self.frame.place(x=x, y=y, width=width, height=height)

        self.widget = tk.Text(self.frame, bg="#9C9C9C", fg="black", font=self.font)
        self.widget.place(x=0, y=0, width=width, height=height)
        self.widget.bind("<Key>", lambda e: "break")  # Prevent direct keyboard input

        self.mode_label = tk.Label(self.frame, font=("Courier", 10), bg="#9C9C9C")
        self.mode_label.place(x=2, rely=1.0, anchor="sw")

        # Use the provided configuration, or default to placing in the southeast.
        if stack_label_config is None:
            stack_label_config = {"relx": 1.0, "rely": 1.0, "anchor": "se"}
        self.stack_content = tk.Label(self.frame, font=("Courier", 10), bg="#9C9C9C")
        self.stack_content.place(**stack_label_config)

    def append_entry(self, ch):
        self.raw_value += ch        # Append to raw_value (assumed to be in decimal).
        self.current_entry = self.raw_value  # In DEC mode, display raw_value.
        self.update()

    def set_entry(self, entry):
        # When setting a new entry from a conversion, do not change raw_value.
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

    def show_error(self, title, message):
        print(f"{title}: {message}")

    def update_stack_content(self):
        # Get the current stack state from the stack module.
        s = stack.get_state()  # Returns a list, e.g., [0.0, 0.0, 0.0, 0.0]
        # Format the text as desired:
        text = f"stack = {s}"
        self.stack_content.config(text=text)

    def schedule_stack_updates(self, interval=100):
        self.update_stack_content()
        self.master.after(interval, lambda: self.schedule_stack_updates(interval))
