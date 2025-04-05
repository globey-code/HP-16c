"""
main.pyw
Main entry point for the HP-16C emulator.
This module builds the UI, sets up the controller, and binds buttons.
Refactored to include type hints, detailed docstrings, and improved structure.
Author: GlobeyCode (original), refactored by ChatGPT
License: MIT
Date: 3/23/2025 (original), refactored 2025-04-01
Dependencies: Python 3.6+ with tkinter, and HP-16C emulator modules (ui, controller, buttons, logging_config)
"""

import tkinter as tk
import tkinter.font as tkFont
from typing import Dict, Any, List, Tuple
from ui import setup_ui, show_user_guide
from controller import HP16CController
from buttons import bind_buttons
from button_config import BUTTONS_CONFIG
from stack import Stack
from logging_config import logger

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
    logger.info("User guide requested (placeholder)")
    show_user_guide()

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

    available_fonts = tkFont.families()
    font_family = "Calculator" if "Calculator" in available_fonts else "Courier"
    custom_font = tkFont.Font(family=font_family, size=28)
    logger.info(f"Using font: family={font_family}, size=28")
    if font_family == "Courier":
        logger.warning("Calculator font not found, using Courier")

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