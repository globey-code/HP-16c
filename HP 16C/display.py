import tkinter as tk
import stack
from keyboard_input import restrict_input

class Display:
    def __init__(self, master, x, y, width, height, font=None, 
                 stack_content_config=None, word_size_config=None):
        self.master = master
        self.current_entry = ""
        self.raw_value = ""          # Store the original decimal entry here.
        self.mode = "DEC"            # Current mode: DEC by default.
        self.font = font if font is not None else ("Courier", 18)

        # Create the main frame for the display.
        self.frame = tk.Frame(master, bg="#9C9C9C")
        self.frame.place(x=x, y=y, width=width, height=height)

        # Create a Text widget to show the calculator entry.
        self.widget = tk.Text(self.frame, bg="#9C9C9C", fg="black", font=self.font)
        self.widget.place(x=0, y=0, width=width, height=height)
        self.widget.bind("<Key>", lambda e: "break")  # Prevent direct keyboard input

        # Create a label for the mode indicator (bottom left by default).
        self.mode_label = tk.Label(self.frame, font=("Courier", 10), bg="#9C9C9C")
        self.mode_label.place(x=3, rely=1.0, anchor="sw", y=-8)

        # Configure stack content label (default: southeast)
        if stack_content_config is None:
            stack_content_config = {"relx": 0.99, "rely": 0.92, "anchor": "se"}
        self.stack_content = tk.Label(self.frame, font=("Courier", 10), bg="#9C9C9C")
        self.stack_content.place(**stack_content_config)

        # Configure word size label (default: northeast)
        if word_size_config is None:
            word_size_config = {"relx": 0.99, "rely": 0.02, "anchor": "ne"}
        self.word_size_label = tk.Label(self.frame, font=("Courier", 10), bg="#9C9C9C")
        self.word_size_label.place(**word_size_config)

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

    # Updates the stack content label with the current stack state.
    def update_stack_content(self):
        state = stack.get_state()  # E.g., [0.0, 0.0, 0.0, 0.0]
        text = f"stack = {state}"
        self.stack_content.config(text=text)

    # Schedules periodic updates for the stack content label.
    def schedule_stack_updates(self, interval=200):
        self.update_stack_content()
        self.master.after(interval, lambda: self.schedule_stack_updates(interval))
