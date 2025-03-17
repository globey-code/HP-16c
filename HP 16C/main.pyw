"""
main.pyw

The main entry point. Builds the UI, sets up the controller, and binds buttons.
"""

import tkinter as tk
import tkinter.font as tkFont
from ui import setup_ui
from controller import HP16CController
from buttons import bind_buttons
from button_config import BUTTONS_CONFIG
from logging_config import logger

def load_config():
    """Load the default configuration for the emulator."""
    logger.info("Entering function: load_config")
    config = {
        "display_width": 400, "display_height": 100, "margin": 20, "bg_color": "#1e1818",
        "display_font_family": "Courier", "display_font_size": 18
    }
    config["display_x"] = 125
    config["display_y"] = 20
    config["display_width"] = 575
    config["display_height"] = 80
    logger.info(f"Config loaded and updated: {config}")
    logger.info("Exiting function: load_config")
    return config

def main():
    """Initialize and run the HP-16C emulator."""
    logger.info("Entering function: main")
    logger.info("Creating Tk root window")
    root = tk.Tk()
    logger.info("Setting window title: HP 16C Emulator")
    root.title("HP 16C Emulator")
    logger.info("Configuring root background color: #1e1818")
    root.configure(bg="#1e1818")
    logger.info("Setting root resizable: False, False")
    root.resizable(False, False)

    config = load_config()
    try:
        custom_font = tkFont.Font(family=config["display_font_family"], size=config["display_font_size"])
        logger.info(f"Custom font created: family={config['display_font_family']}, size={config['display_font_size']}")
    except Exception as e:
        logger.info(f"Font creation failed: {str(e)}. Falling back to default")
        custom_font = tkFont.Font(family="Courier", size=18)

    disp, buttons = setup_ui(root, config, custom_font)
    logger.info("Initializing HP16CController with display and buttons")
    controller = HP16CController(disp, buttons)
    logger.info("Binding buttons to controller actions")
    bind_buttons(buttons, disp, controller)

    def update_stack():
        disp.update_stack_content()
        root.after(100, update_stack)

    logger.info("Starting periodic stack updates")
    update_stack()
    root.update()
    logger.info(f"Root window size: {root.winfo_geometry()}")
    logger.info("Entering Tkinter mainloop")
    root.mainloop()
    logger.info("Exiting function: main")

if __name__ == "__main__":
    logger.info("Script started: main.pyw")
    main()
    logger.info("Script ended: main.pyw")