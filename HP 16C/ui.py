"""
ui.py

Builds the main window geometry, places the display, and creates button frames.
"""

import tkinter as tk
from display import Display
from buttons.buttons import bind_buttons  # the new single file
from buttons.button_config import BUTTONS_CONFIG

def setup_ui(root, config, custom_font):
    margin = config["margin"]

    # Pull display X/Y from config (fallback to margin if not set)
    display_x = config.get("display_x", margin)
    display_y = config.get("display_y", margin)

    display_width = config["display_width"]
    display_height = config["display_height"]

    btn_min_x = min(btn["x"] for btn in BUTTONS_CONFIG)
    btn_max_x = max(btn["x"] + btn["width"] for btn in BUTTONS_CONFIG)
    btn_min_y = min(btn["y"] for btn in BUTTONS_CONFIG)
    btn_max_y = max(btn["y"] + btn["height"] for btn in BUTTONS_CONFIG)

    btn_area_width = btn_max_x - btn_min_x
    btn_area_height = btn_max_y - btn_min_y

    final_width = max(display_width, btn_area_width) + 2 * margin
    final_height = margin + display_height + margin + btn_area_height + margin

    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x_coord = (screen_w - final_width) // 2
    y_coord = (screen_h - final_height) // 2
    root.geometry(f"{final_width}x{final_height}+{x_coord}+{y_coord}")

    # -- CHANGE HERE: use display_x and display_y --
    disp = Display(
        master=root,
        x=display_x,           # from config
        y=display_y,           # from config
        width=display_width,
        height=display_height,
        font=custom_font
    )
    disp.set_mode("DEC")
    disp.update()

    buttons = []
    offset_x = (final_width - btn_area_width) // 2 - btn_min_x
    offset_y = margin + display_height + margin - btn_min_y

    for cfg in BUTTONS_CONFIG:
        cfg_adjusted = cfg.copy()
        cfg_adjusted["x"] += offset_x
        cfg_adjusted["y"] += offset_y
        btn_dict = create_single_button(root, cfg_adjusted)
        buttons.append(btn_dict)

    return disp, buttons

def create_single_button(root, cfg):
    orig_top = cfg.get("top_label", "")
    orig_main = cfg.get("main_label", "")
    orig_sub = cfg.get("sub_label", "")

    frame = tk.Frame(
        root,
        bg=cfg.get("bg", "#1e1818"),
        relief="flat",
        highlightthickness=1,
        highlightbackground="white"
    )
    frame.place(x=cfg["x"], y=cfg["y"], width=cfg["width"], height=cfg["height"])

    cfg["frame"] = frame

    if orig_top:
        top_widget = tk.Label(
            frame, text=orig_top, font=("Courier", 9),
            bg=cfg.get("bg", "#1e1818"), fg=cfg.get("fg", "#e3af01")
        )
        top_widget.place(relx=0.5, rely=0, anchor='n')
        cfg["top_label"] = top_widget
    else:
        cfg["top_label"] = None

    main_widget = tk.Label(
        frame, text=orig_main, font=("Courier", 11),
        bg=cfg.get("bg", "#1e1818"), fg=cfg.get("fg", "white")
    )
    main_widget.place(relx=0.5, rely=0.5, anchor='center')
    cfg["main_label"] = main_widget

    if orig_sub:
        sub_widget = tk.Label(
            frame, text=orig_sub, font=("Courier", 9),
            bg=cfg.get("bg", "#1e1818"), fg=cfg.get("fg", "#59b7d1")
        )
        sub_widget.place(relx=0.5, rely=1, anchor='s')
        cfg["sub_label"] = sub_widget
    else:
        cfg["sub_label"] = None

    return cfg
