import tkinter as tk
from display import Display
from button_config import BUTTONS_CONFIG

def setup_ui(root, config, custom_font):
    # Calculate window size from BUTTONS_CONFIG
    margin = config["margin"]
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

    # Set window geometry
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x_coord = (screen_w - final_width) // 2
    y_coord = (screen_h - final_height) // 2
    root.geometry(f"{final_width}x{final_height}+{x_coord}+{y_coord}")

    # Create display.
    # (Using defaults: stack content in southeast, word size in northeast.)
    disp = Display(root,
                   x=margin + 25,
                   y=margin + 25,
                   width=display_width - 50,
                   height=display_height - 50,
                   font=custom_font)
    disp.set_mode("DEC")
    disp.update()

    # Buttons creation with adjusted offset.
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

def create_buttons(root, config):
    # Calculate offsets and positions based on BUTTONS_CONFIG
    buttons = []
    for cfg in BUTTONS_CONFIG:
        btn = create_single_button(root, cfg)
        buttons.append(btn)
    return buttons

def create_single_button(root, cfg):
    # Save original texts before creating widgets
    orig_top = cfg.get("top_label", "")
    orig_main = cfg.get("main_label", "")
    orig_sub = cfg.get("sub_label", "")

    frame = tk.Frame(root,
                     bg=cfg.get("bg", "#1e1818"),
                     relief="flat",
                     highlightthickness=1,
                     highlightbackground="white")
    frame.place(x=cfg["x"], y=cfg["y"], width=cfg["width"], height=cfg["height"])

    cfg["frame"] = frame

    # Create top label widget if there is an original text
    if orig_top:
        top_widget = tk.Label(frame, text=orig_top, font=("Courier", 9),
                              bg=cfg.get("bg", "#1e1818"), fg=cfg.get("fg", "#e3af01"))
        top_widget.place(relx=0.5, rely=0, anchor='n')
        cfg["top_label"] = top_widget
    else:
        cfg["top_label"] = None

    # Create main label widget
    main_widget = tk.Label(frame, text=orig_main, font=("Courier", 11),
                           bg=cfg.get("bg", "#1e1818"), fg=cfg.get("fg", "white"))
    main_widget.place(relx=0.5, rely=0.5, anchor='center')
    cfg["main_label"] = main_widget

    # Create sub label widget if there is an original text
    if orig_sub:
        sub_widget = tk.Label(frame, text=orig_sub, font=("Courier", 9),
                              bg=cfg.get("bg", "#1e1818"), fg=cfg.get("fg", "#59b7d1"))
        sub_widget.place(relx=0.5, rely=1, anchor='s')
        cfg["sub_label"] = sub_widget
    else:
        cfg["sub_label"] = None

    # Save the original texts separately so they are not overwritten by the widget objects
    cfg["orig_top_text"] = orig_top
    cfg["orig_main_text"] = orig_main
    cfg["orig_sub_text"] = orig_sub

    return cfg
