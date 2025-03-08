import tkinter as tk

# List of allowed key combinations that shouldn't be blocked.
ALLOWED_KEYS = [
    'Alt_L', 'Alt_R', 'F4', 'Super_L', 'Super_R', 'Escape', 'Control_L', 'Control_R'
]

def restrict_input(root):
    def key_handler(event):
        key_sym = event.keysym

        # Allow standard OS key combinations (Alt+F4, Ctrl+Esc, Windows key)
        if key_sym in ALLOWED_KEYS:
            return  # Do not block allowed keys

        # Block all other key inputs
        print(f"Blocked key: {key_sym}")
        return "break"  # Stops event propagation, blocking input

    # Bind all keyboard inputs
    root.bind_all('<Key>', key_handler)
