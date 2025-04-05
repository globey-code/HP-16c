"""
ui.py
Builds the UI components for the HP-16C emulator, including the display and button grid.
Refactored to include type hints, clearer docstrings, and improved layout calculations.
Author: GlobeyCode (original), refactored by ChatGPT
License: MIT
Date: 3/23/2025 (original), refactored 2025-04-01
Dependencies: Python 3.6+ with tkinter, and HP-16C emulator modules (buttons, display, controller)
"""

from typing import Tuple, List, Dict, Any
import tkinter as tk
import tkinter.font as tkFont
from display import Display
from stack import Stack
from button_config import BUTTONS_CONFIG
from logging_config import logger
from dataclasses import asdict


def show_user_guide() -> None:
    help_window = tk.Toplevel()
    help_window.title("User Guide")
    tk.Label(
        help_window,
        text=(
            "This is the user guide for the HP-16C emulator.\n"
            "Here you can find instructions on how to use the emulator."
        )
    ).pack()

def setup_ui(root: tk.Tk, stack: Stack, config: Dict[str, Any], Courier: tkFont.Font) -> Tuple[Display, List[Dict[str, Any]]]:
    total_width = 1049 + 2 * config["margin"]
    total_height = 560
    logger.info(
        f"Setting up UI: display at x={config.get('display_x', config['margin'])}, "
        f"y={config.get('display_y', config['margin'])}, width={config['display_width']}, "
        f"height={config['display_height']}, grid=4x10, total={total_width}x{total_height}"
    )

    # Initialize the display
    disp = Display(
        master=root,
        stack=stack,
        x=config.get("display_x", config["margin"]),
        y=config.get("display_y", config["margin"]),
        width=config["display_width"],
        height=config["display_height"],
        font=Courier
    )
    disp.set_mode("DEC")
    disp.update()

    # Define grid dimensions
    max_rows = 4
    max_cols = 10
    base_row_height = 75
    grid_width = 1045
    grid_height = (max_rows * base_row_height) + ((max_rows - 1) * 5) + (max_rows * 22)
    
    # Adjust grid height if any button in row 3 has rowspan of 2
    if any(cfg.row == 3 and cfg.rowspan == 2 for cfg in BUTTONS_CONFIG):
        grid_height += (175 - base_row_height)
    total_grid_width = grid_width + 4
    total_grid_height = grid_height + 17

    # Create bezel frame
    bezel_frame = tk.Frame(root, bg="#C0C0C0", highlightthickness=0, bd=0)
    bezel_x = (total_width - total_grid_width) / 2
    bezel_y = config.get("display_y", config["margin"]) + config["display_height"] + config["margin"]
    bezel_frame.place(x=bezel_x, y=bezel_y, width=total_grid_width, height=total_grid_height)

    # Create buttons frame
    buttons_frame = tk.Frame(bezel_frame, bg=config["bg_color"])
    buttons_frame.place(x=2, y=2, width=grid_width, height=grid_height)

    # Create buttons
    buttons_list: List[Dict[str, Any]] = []
    logger.info("Creating buttons from BUTTONS_CONFIG")
    for cfg in BUTTONS_CONFIG:
        # Convert ButtonConfig dataclass to dictionary for create_single_button
        btn_dict = create_single_button(buttons_frame, asdict(cfg))
        rowspan = cfg.rowspan  # Access rowspan directly from dataclass
        btn_dict["frame"].grid(
            row=cfg.row,       # Use dot notation
            column=cfg.col,    # Use dot notation
            rowspan=rowspan,
            padx=(25, 2),
            pady=(20, 2),
            sticky="nsew"
        )
        # Access text fields from btn_dict since they are added by create_single_button
        top_text = (btn_dict.get('orig_top_text') or '').replace('\n', '')
        main_text = (btn_dict.get('orig_main_text') or '').replace('\n', '')
        sub_text = (btn_dict.get('orig_sub_text') or '').replace('\n', '')
        logger.info(
            f"Button {cfg.row},{cfg.col}: {top_text}/{main_text}/{sub_text}, "
            f"{cfg.width}x{cfg.height}, rowspan={rowspan}"
        )
        buttons_list.append(btn_dict)
    logger.info(f"Total buttons created: {len(buttons_list)}")

    # Configure grid
    for col in range(max_cols):
        buttons_frame.grid_columnconfigure(col, uniform="col", minsize=75)
    for row in range(max_rows):
        buttons_frame.grid_rowconfigure(row, uniform="row", minsize=base_row_height)
    logger.info(f"Grid configured: {max_cols} cols, {max_rows} rows, minsize={base_row_height}")

    # Add branding label
    branding_label = tk.Label(
        bezel_frame,
        text=" H E W L E T T - P A C K A R D   E M U L A T O R ",
        font=("Courier", 14, "bold"),
        bg="#1e1818",
        fg="#A9A9A9"
    )
    branding_label.place(x=20, rely=1, y=6, anchor="sw")

    # Set window size
    root.update_idletasks()
    root.geometry(f"{total_width}x{total_height}")

    # Configure menu
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)
    help_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label="User Guide", command=show_user_guide)
    debug_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Debug", menu=debug_menu)
    debug_menu.add_command(label="Toggle Stack Display", command=disp.toggle_stack_display)
    root.bind('<F1>', lambda event: show_user_guide())

    # Add stack display
    stack_display = tk.Label(root, text="Y: 0 Z: 0 T: 0", font=Courier, bg=config["bg_color"], fg="white")
    disp.stack_display = stack_display
    disp.toggle_stack_display()

    return disp, buttons_list

def create_single_button(root: tk.Widget, cfg: Dict[str, Any]) -> Dict[str, Any]:
    orig_top = cfg.get("top_label", "")
    orig_main = cfg.get("main_label", "")
    orig_sub = cfg.get("sub_label", "")

    frame = tk.Frame(
        root,
        bg=cfg.get("bg", "#1e1818"),
        relief="flat",
        highlightthickness=1,
        highlightbackground="white",
        width=cfg["width"],
        height=cfg["height"]
    )

    cfg["frame"] = frame
    cfg["orig_top_text"] = orig_top
    cfg["orig_main_text"] = orig_main
    cfg["orig_sub_text"] = orig_sub
    cfg["orig_bg"] = cfg.get("bg", "#1e1818")
    cfg["orig_top_fg"] = cfg.get("fg", "#e3af01")
    cfg["orig_fg"] = "white"
    cfg["orig_sub_fg"] = "#59b7d1"

    if orig_top:
        top_widget = tk.Label(
            frame,
            text=orig_top,
            font=("Courier", 9),
            bg=cfg["orig_bg"],
            fg=cfg["orig_top_fg"]
        )
        top_widget.place(relx=0.5, rely=0, anchor="n")
        cfg["top_label"] = top_widget
    else:
        cfg["top_label"] = None

    main_widget = tk.Label(
        frame,
        text=orig_main,
        font=("Courier", 11),
        bg=cfg["orig_bg"],
        fg=cfg["orig_fg"]
    )
    main_widget.place(relx=0.5, rely=0.5, anchor="center")
    cfg["main_label"] = main_widget

    if orig_sub:
        sub_widget = tk.Label(
            frame,
            text=orig_sub,
            font=("Courier", 9),
            bg=cfg["orig_bg"],
            fg=cfg["orig_sub_fg"]
        )
        sub_widget.place(relx=0.5, rely=1, anchor="s")
        cfg["sub_label"] = sub_widget
    else:
        cfg["sub_label"] = None

    return cfg