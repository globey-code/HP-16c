"""
ui.py

Builds the main window geometry, places the display, and creates button frames.
Uses a grid layout for buttons based on row and col from BUTTONS_CONFIG.
Ensures all columns and rows are fully visible.
Adds a silver bezel around the buttons with HEWLETT-PACKARD branding, with dynamic sizing and button padding.
"""

import tkinter as tk
import buttons
from display import Display
from button_config import BUTTONS_CONFIG
from controller import HP16CController  # Import the controller class

def setup_ui(root, config, custom_font):
    margin = config["margin"]
    display_x = config.get("display_x", margin)
    display_y = config.get("display_y", margin)
    display_width = config["display_width"]
    display_height = config["display_height"]

    # Create display
    disp = Display(master=root, x=display_x, y=display_y, width=display_width, height=display_height, font=custom_font)
    disp.set_mode("DEC")
    disp.update()

    # Calculate total rows and columns
    max_rows = max(cfg["row"] + cfg.get("rowspan", 1) for cfg in BUTTONS_CONFIG)  # Should be 5
    max_cols = max(cfg["col"] for cfg in BUTTONS_CONFIG) + 1  # Should be 10

    # Dynamic button padding (use your original values)
    button_padding_top = 20    # Padding above buttons
    button_padding_bottom = 2  # Padding below buttons
    button_padding_left = 25   # Padding to the left of buttons
    button_padding_right = 2   # Padding to the right of buttons (original value)

    # Calculate button grid dimensions with padding, but override grid_width
    base_row_height = 75
    grid_width = 1045  # Keep your hardcoded value
    grid_height = (max_rows * base_row_height) + ((max_rows - 1) * 5) + (max_rows * (button_padding_top + button_padding_bottom))
    if max_rows >= 2 and any(cfg["row"] == 3 and cfg.get("rowspan", 1) == 2 for cfg in BUTTONS_CONFIG):
        grid_height += (175 - base_row_height)  # Account for ENTER button’s extra height

    # Dynamic bezel border sizes
    bezel_top_border = 2
    bezel_bottom_border = 15
    bezel_left_border = 2
    bezel_right_border = 2

    # Adjust total width and height with bezel borders
    total_grid_width = grid_width + bezel_left_border + bezel_right_border
    # Ensure symmetrical margins by calculating total_width with equal margins on both sides
    total_width = total_grid_width + 2 * margin  # Symmetrical margins on both sides
    total_grid_height = grid_height + bezel_top_border + bezel_bottom_border
    total_height = display_height + total_grid_height + 3 * margin

    # Create bezel frame and center it within the window
    bezel_frame = tk.Frame(
        root,
        bg="#C0C0C0",  # Silver color
        highlightthickness=0,
        bd=0
    )
    # Center the bezel_frame by calculating the x position
    bezel_x = (total_width - total_grid_width) / 2  # This ensures equal margins on both sides
    bezel_frame.place(
        x=bezel_x,
        y=display_y + display_height + margin,
        width=total_grid_width,
        height=total_grid_height
    )

    # Button grid inside the bezel
    buttons_frame = tk.Frame(bezel_frame, bg=config["bg_color"])
    buttons_frame.place(x=bezel_left_border, y=bezel_top_border, width=grid_width, height=grid_height)

    buttons = []
    for cfg in BUTTONS_CONFIG:
        btn_dict = create_single_button(buttons_frame, cfg)
        rowspan = cfg.get("rowspan", 1)
        btn_dict["frame"].grid(row=cfg["row"], column=cfg["col"], rowspan=rowspan,
                              padx=(button_padding_left, button_padding_right),
                              pady=(button_padding_top, button_padding_bottom),
                              sticky="nsew")
        buttons.append(btn_dict)
        #print(f"Button at row={cfg['row']}, col={cfg['col']}, rowspan={rowspan}, label={cfg.get('main_label', 'None')}")

    # Set uniform sizing for grid
    for col in range(max_cols):
        buttons_frame.grid_columnconfigure(col, uniform="col", minsize=75)
    for row in range(max_rows):
        buttons_frame.grid_rowconfigure(row, uniform="row", minsize=base_row_height)

    # Add HEWLETT-PACKARD label at the bottom-left of the bezel
    branding_label = tk.Label(
        bezel_frame,
        text=" H E W L E T T - P A C K A R D - E M U L A T O R ",
        font=("Courier", 14, "bold"),
        bg="#1e1818",
        fg="#A9A9A9"
    )
    branding_label.place(x=20, rely=1, y=6, anchor="sw")

    # Debugging output
    root.update_idletasks()
    bezel_width = bezel_frame.winfo_width()
    bezel_height = bezel_frame.winfo_height()
    left_margin = bezel_frame.winfo_x()
    right_margin = total_width - (bezel_frame.winfo_x() + bezel_frame.winfo_width())
    print(f"Calculated window size: {total_width}x{total_height} px")
    print(f"Max rows: {max_rows}, Max cols: {max_cols}")
    print(f"Grid width: {grid_width}, Grid height: {grid_height}")
    print(f"Button padding - Top: {button_padding_top}, Bottom: {button_padding_bottom}, "
          f"Left: {button_padding_left}, Right: {button_padding_right}")
    print(f"Bezel borders - Top: {bezel_top_border}, Bottom: {bezel_bottom_border}, "
          f"Left: {bezel_left_border}, Right: {bezel_right_border}")
    print(f"Bezel size: {bezel_width}x{bezel_height} px")
    print(f"Left margin: {left_margin}, Right margin: {right_margin}")

    # Set window size
    root.geometry(f"{total_width}x{total_height}")
    root.resizable(False, False)

    return disp, buttons

def create_single_button(root, cfg):
    orig_top = cfg.get("top_label", "")
    orig_main = cfg.get("main_label", "")
    orig_sub = cfg.get("sub_label", "")

    # Create frame without absolute positioning
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
    cfg["orig_top_text"] = orig_top  # Store originals for buttons.py
    cfg["orig_main_text"] = orig_main
    cfg["orig_sub_text"] = orig_sub
    cfg["orig_bg"] = cfg.get("bg", "#1e1818")
    cfg["orig_top_fg"] = cfg.get("fg", "#e3af01")
    cfg["orig_fg"] = "white"
    cfg["orig_sub_fg"] = cfg.get("fg", "#59b7d1")

    if orig_top:
        top_widget = tk.Label(
            frame, text=orig_top, font=("Courier", 9),
            bg=cfg["orig_bg"], fg=cfg["orig_top_fg"]
        )
        top_widget.place(relx=0.5, rely=0, anchor="n")
        cfg["top_label"] = top_widget
    else:
        cfg["top_label"] = None

    main_widget = tk.Label(
        frame, text=orig_main, font=("Courier", 11),
        bg=cfg["orig_bg"], fg=cfg["orig_fg"]
    )
    main_widget.place(relx=0.5, rely=0.5, anchor="center")
    cfg["main_label"] = main_widget

    if orig_sub:
        sub_widget = tk.Label(
            frame, text=orig_sub, font=("Courier", 9),
            bg=cfg["orig_bg"], fg=cfg["orig_sub_fg"]
        )
        sub_widget.place(relx=0.5, rely=1, anchor="s")
        cfg["sub_label"] = sub_widget
    else:
        cfg["sub_label"] = None

    return cfg