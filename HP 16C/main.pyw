"""
main.pyw

The main entry point. Builds the UI, sets up the controller, binds buttons.
No references to stack or display from other modules = no circular imports.
"""

import tkinter as tk
import tkinter.font as tkFont
from ui import setup_ui
from configuration import load_config
from controller import HP16CController
# from button_state_manager import ButtonStateManager  # Uncomment if needed
from buttons import bind_buttons
from button_config import BUTTONS_CONFIG

def main():
    root = tk.Tk()
    root.title("HP 16C Emulator")
    root.configure(bg="#1e1818")
    root.resizable(False, False)

    config = load_config()

    # Override display size from config
    config["display_x"] = 125
    config["display_y"] = 20
    config["display_width"] = 575
    config["display_height"] = 80

    try:
        custom_font = tkFont.Font(
            family=config["display_font_family"], 
            size=config["display_font_size"]
        )
    except Exception:
        custom_font = tkFont.Font(family="Courier", size=18)

    # Setup UI and controller
    disp, buttons = setup_ui(root, config, custom_font)
    controller = HP16CController(disp, buttons)
    bind_buttons(buttons, disp, controller)  # Bind buttons here

    # Periodic stack updates (every 100ms)
    def update_stack():
        disp.update_stack_content()
        root.after(100, update_stack)

    update_stack()
    
    print("Running HP 16C Emulator")
    root.mainloop()

if __name__ == "__main__":
    main()