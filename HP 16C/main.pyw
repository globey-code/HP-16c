"""
main.pyw
Serves as the main entry point for the HP-16C emulator, initializing the UI and core components.
Author: GlobeyCode
License: MIT
Created: 3/23/2025
Last Modified: 4/07/2025
Dependencies: Python 3.6+, tkinter, tkinter.font, ui, controller, buttons, stack, logging_config, user_guide
"""

import os
import tkinter as tk
import tkinter.font as tkFont
from typing import Dict, Any
from ui import setup_ui
from buttons import bind_buttons
from stack import Stack
from logging_config import logger
from user_guide import show_user_guide  # Import directly from user_guide.py
import ctypes

logger.info("Loading controller module (no reload)")

def load_config() -> Dict[str, Any]:
    logger.info("Entering function: load_config")
    config: Dict[str, Any] = {
        "display_width": 400,
        "display_height": 100,
        "margin": 20,
        "bg_color": "#1e1818",
        "display_font_family": "Calculator",
        "display_font_size": 28,
        "show_stack_display": False
    }
    config["display_x"] = 125
    config["display_y"] = 20
    config["display_width"] = 575
    config["display_height"] = 80
    logger.info(f"Config loaded and updated: {config}")
    return config

def show_user_guide_placeholder() -> None:
    logger.info("User guide requested")
    show_user_guide()  # Call the imported function directly

# Set DPI awareness
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-monitor DPI awareness
except:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # System DPI awareness (fallback)
    except:
        pass

def main() -> None:
    logger.info("Entering function: main")
    root = tk.Tk()
    root.title("HP 16C Emulator")
    root.configure(bg="#1e1818")
    root.resizable(False, False)

    # Load calculator.ttf from the font folder using Windows API
    base_path = os.path.dirname(os.path.abspath(__file__))  # Directory of main.pyw
    font_path = os.path.join(base_path, "font", "calculator.ttf")
    
    try:
        # Use AddFontResourceEx to load the font for this process only
        FR_PRIVATE = 0x10  # Font is private to the process, not installed system-wide
        if ctypes.windll.gdi32.AddFontResourceExW(font_path, FR_PRIVATE, 0) > 0:
            custom_font = tkFont.Font(family="Calculator", size=28)
            logger.info(f"Using font: family=Calculator, size=28 from {font_path}")
        else:
            raise OSError("Failed to add font resource")
    except (OSError, tk.TclError) as e:
        # Fallback to Courier New if loading fails
        custom_font = tkFont.Font(family="Courier New", size=28)
        logger.warning(f"Failed to load Calculator font from {font_path}: {e}, using Courier New")

    config = load_config()
    stack_instance = Stack()
    disp, buttons = setup_ui(root, stack_instance, config, custom_font)

    logger.info("Creating stack display Label")
    stack_display = tk.Label(root, text="Y: 0 Z: 0 T: 0", font=custom_font, bg="#1e1818", fg="white")
    if config.get("show_stack_display", False):
        stack_display.place(x=125, y=110, width=575, height=40)
        logger.info("Stack display placed in layout")
    else:
        logger.info("Stack display created but not placed (hidden)")

    # Force reload of controller module
    logger.info("Reloading controller module")
    import controller
    import importlib
    importlib.reload(controller)
    from controller import HP16CController
    logger.info("Initializing HP16CController")
    controller = HP16CController(stack_instance, disp, buttons, stack_display)

    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)
    help_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label="User Guide", command=show_user_guide_placeholder)
    debug_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Debug", menu=debug_menu)
    debug_menu.add_command(label="Toggle Stack Display", command=controller.toggle_stack_display)

    root.bind('<F2>', lambda event: controller.toggle_stack_display())
    bind_buttons(buttons, disp, controller)

    def update_stack() -> None:
        logger.debug("Periodic stack update")
        controller.update_stack_display()
        root.after(100, update_stack)

    logger.info("Starting periodic stack updates")
    update_stack()

    root.update()
    logger.info(f"Root window size: {root.winfo_geometry()}")
    root.mainloop()
    logger.info("Exiting function: main")

if __name__ == "__main__":
    logger.info("Script started: main.pyw")
    main()
    logger.info("Script ended: main.pyw")