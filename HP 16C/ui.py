# ui.py
# Builds the UI components for the HP-16C emulator, including the display and button grid.
# Author: GlobeyCode
# License: MIT
# Date: 3/23/2025
# Dependencies: Python 3.6+ with tkinter, HP-16C emulator modules (buttons, display, controller)

import tkinter as tk
import buttons
from display import Display
from button_config import BUTTONS_CONFIG
from controller import HP16CController
from logging_config import logger

def setup_ui(root, config, custom_font):
    """Set up the UI components: display and buttons."""
    # Log UI setup details
    logger.info(f"Setting up UI: display at x={config.get('display_x', config['margin'])}, "
                f"y={config.get('display_y', config['margin'])}, width={config['display_width']}, "
                f"height={config['display_height']}, grid=4x10, total={1049 + 2 * config['margin']}x560")

    # Create Display object (no widget parameter needed after Display class fix)
    disp = Display(
        master=root,
        x=config.get("display_x", config["margin"]),
        y=config.get("display_y", config["margin"]),
        width=config["display_width"],
        height=config["display_height"],
        font=custom_font
    )
    disp.set_mode("DEC")
    disp.update()

    # Define grid dimensions for buttons
    max_rows = 4
    max_cols = 10
    base_row_height = 75
    grid_width = 1045
    grid_height = (max_rows * base_row_height) + ((max_rows - 1) * 5) + (max_rows * 22)

    # Adjust grid height if any button in row 3 has rowspan=2
    if any(cfg["row"] == 3 and cfg.get("rowspan", 1) == 2 for cfg in BUTTONS_CONFIG):
        grid_height += (175 - base_row_height)
    total_grid_width = grid_width + 4
    total_grid_height = grid_height + 17

    # Create bezel and button frames
    bezel_frame = tk.Frame(root, bg="#C0C0C0", highlightthickness=0, bd=0)
    bezel_frame.place(
        x=(1049 + 2 * config["margin"] - total_grid_width) / 2,
        y=config.get("display_y", config["margin"]) + config["display_height"] + config["margin"],
        width=total_grid_width,
        height=total_grid_height
    )
    buttons_frame = tk.Frame(bezel_frame, bg=config["bg_color"])
    buttons_frame.place(x=2, y=2, width=grid_width, height=grid_height)

    # Create buttons from BUTTONS_CONFIG
    buttons_list = []
    logger.info("Creating buttons from BUTTONS_CONFIG")
    for cfg in BUTTONS_CONFIG:
        btn_dict = create_single_button(buttons_frame, cfg)
        rowspan = cfg.get("rowspan", 1)
        btn_dict["frame"].grid(
            row=cfg["row"],
            column=cfg["col"],
            rowspan=rowspan,
            padx=(25, 2),
            pady=(20, 2),
            sticky="nsew"
        )
        top_text = cfg['orig_top_text'].replace('\n', '')
        main_text = cfg['orig_main_text'].replace('\n', '')
        sub_text = cfg['orig_sub_text'].replace('\n', '')
        logger.info(f"Button {cfg['row']},{cfg['col']}: {top_text}/{main_text}/{sub_text}, "
                    f"{cfg['width']}x{cfg['height']}, row={cfg['row']}, col={cfg['col']}, rowspan={rowspan}")
        buttons_list.append(btn_dict)
    logger.info(f"Total buttons created: {len(buttons_list)}")

    # Configure grid layout
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

    # Set window geometry
    root.update_idletasks()
    root.geometry(f"{1049 + 2 * config['margin']}x560")
    return disp, buttons_list

def create_single_button(root, cfg):
    """Create a single button with labels."""
    orig_top = cfg.get("top_label", "")
    orig_main = cfg.get("main_label", "")
    orig_sub = cfg.get("sub_label", "")

    # Create button frame
    frame = tk.Frame(
        root,
        bg=cfg.get("bg", "#1e1818"),
        relief="flat",
        highlightthickness=1,
        highlightbackground="white",
        width=cfg["width"],
        height=cfg["height"]
    )

    # Store original values in config
    cfg["frame"] = frame
    cfg["orig_top_text"] = orig_top
    cfg["orig_main_text"] = orig_main
    cfg["orig_sub_text"] = orig_sub
    cfg["orig_bg"] = cfg.get("bg", "#1e1818")
    cfg["orig_top_fg"] = cfg.get("fg", "#e3af01")
    cfg["orig_fg"] = "white"
    cfg["orig_sub_fg"] = cfg.get("fg", "#59b7d1")

    # Add top label if present
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

    # Add main label
    main_widget = tk.Label(
        frame,
        text=orig_main,
        font=("Courier", 11),
        bg=cfg["orig_bg"],
        fg=cfg["orig_fg"]
    )
    main_widget.place(relx=0.5, rely=0.5, anchor="center")
    cfg["main_label"] = main_widget

    # Add sub label if present
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