# main.pyw
# Main entry point for the HP-16C emulator, responsible for building the UI, setting up the controller, and binding buttons.
# Author: GlobeyCode
# License: MIT
# Date: 3/23/2025
# Dependencies: Python 3.6+ with tkinter, HP-16C emulator modules (ui, controller, buttons, logging_config)

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
        "display_font_family": "Courier", "display_font_size": 18, "show_stack_display": False
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

    # Set up the main display (X register) and buttons
    disp, buttons = setup_ui(root, config, custom_font)

    # Create a stack display (Y, Z, T registers) using a Tkinter Label
    if config["show_stack_display"]:
        stack_display = tk.Label(root, text="Y: 0 Z: 0 T: 0", font=custom_font, bg="#1e1818", fg="white")
        stack_display.place(x=125, y=110, width=575, height=40)  # Position below the main display
    else:
        stack_display = None

    # Initialize the controller with display, buttons, and stack_display
    logger.info("Initializing HP16CController with display, buttons, and stack_display")
    controller = HP16CController(disp, buttons, stack_display)

    # Bind buttons to controller actions
    logger.info("Binding buttons to controller actions")
    bind_buttons(buttons, disp, controller)

    # Periodic stack update function
    def update_stack():
        controller.update_stack_display()  # Call the controller's method to update stack display
        root.after(100, update_stack)

    # Start periodic stack updates
    logger.info("Starting periodic stack updates")
    update_stack()
    root.update()
    logger.info(f"Root window size: {root.winfo_geometry()}")

    # Enter the Tkinter mainloop
    logger.info("Entering Tkinter mainloop")
    root.mainloop()
    logger.info("Exiting function: main")

if __name__ == "__main__":
    logger.info("Script started: main.pyw")
    main()
    logger.info("Script ended: main.pyw")