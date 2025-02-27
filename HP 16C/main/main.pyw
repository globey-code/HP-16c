"""
main.pyw
---------
HP 16C Emulator main file using separate SCALE_X and SCALE_Y
to shrink or enlarge the layout only in one dimension if desired.
Also associates f-labels with buttons so the yellow f button toggles them.

If you only want to shrink the display's height, set SCALE_X = 1.0 and
SCALE_Y < 1.0, so everything compresses vertically but not horizontally.
If both are 1.0, you get the original layout (with the f-label toggle working).
"""

import tkinter as tk
import tkinter.font as tkFont
import os

import arithmetic
import base_conversion
import stack
import error
from display import Display
from f_labels import create_labels

# ----- SEPARATE SCALE FACTORS -----
SCALE_X = 1.0   # horizontal scale (1.0 = original width)
SCALE_Y = 1.0   # vertical scale   (1.0 = original height)
# ----------------------------------

all_buttons = []
root = tk.Tk()
root.title("HP 16C Emulator (Partial Scaling)")
root.iconbitmap("images/HP16C_Logo.ico")
root.configure(bg="#1e1818")

# 1) Create f_labels in absolute coords (from f_labels.py)
# We'll optionally re-place them after scaling if SCALE_X != 1 or SCALE_Y != 1.
f_labels_list = create_labels(root)

from button_config import BUTTONS_CONFIG
from command_map import get_command_map

# Attempt to load a custom font
try:
    font_path = os.path.join("DSEG14", "DSEG14Classic-Regular.ttf")
    custom_font = tkFont.Font(family="Courierl", size=12)
except Exception:
    custom_font = ("Courierl", 12)

# Original display size
display_width = 680
display_height = 200

# Scale the display dimensions
scaled_display_width = int(display_width * SCALE_X)
scaled_display_height = int(display_height * SCALE_Y)

# Compute bounding box for buttons from button_config
btn_min_x = min(cfg["x"] for cfg in BUTTONS_CONFIG)
btn_max_x = max(cfg["x"] + cfg["width"] for cfg in BUTTONS_CONFIG)
btn_min_y = min(cfg["y"] for cfg in BUTTONS_CONFIG)
btn_max_y = max(cfg["y"] + cfg["height"] for cfg in BUTTONS_CONFIG)

btn_block_width = btn_max_x - btn_min_x
btn_block_height = btn_max_y - btn_min_y

# Apply separate scaling to button area
scaled_btn_block_width = int(btn_block_width * SCALE_X)
scaled_btn_block_height = int(btn_block_height * SCALE_Y)

margin = 20
final_width = max(scaled_display_width, scaled_btn_block_width) + 2 * margin
final_height = margin + scaled_display_height + margin + scaled_btn_block_height + margin

# Center on screen
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
x_coord = (screen_w - final_width) // 2
y_coord = (screen_h - final_height) // 2
root.geometry(f"{final_width}x{final_height}+{x_coord}+{y_coord}")

# 2) Create and place the Display
display_x = (final_width - scaled_display_width) // 2
display_y = margin
disp = Display(root,
               x=display_x,
               y=display_y,
               width=scaled_display_width,
               height=scaled_display_height,
               font=custom_font)
disp.update()

memory = {"value": 0.0}

# Offsets so we can center the button block
offset_x = (final_width - scaled_btn_block_width) // 2 - int(btn_min_x * SCALE_X)
offset_y = display_y + scaled_display_height + margin - int(btn_min_y * SCALE_Y)

# 3) Create Buttons (scaled)
for cfg in BUTTONS_CONFIG:
    cmd_name = cfg.get("command_name", None)

    # Scale each coordinate/size
    scaled_x = int(cfg["x"] * SCALE_X)
    scaled_y = int(cfg["y"] * SCALE_Y)
    scaled_w = int(cfg["width"] * SCALE_X)
    scaled_h = int(cfg["height"] * SCALE_Y)

    dummy_cmd = lambda: None
    if "subtext" in cfg:
        # Compound button
        frame = tk.Frame(root, bg=cfg.get("bg", "#504A49"), relief="raised", borderwidth=1)
        frame.place(x=scaled_x + offset_x,
                    y=scaled_y + offset_y,
                    width=scaled_w, height=scaled_h)

        main_label = tk.Label(frame, text=cfg["text"],
                              font=("Courier", 11),
                              bg=cfg.get("bg", "#504A49"),
                              fg=cfg.get("fg", "white"))
        main_label.pack(side="top", fill="x")

        sub_label = tk.Label(frame, text=cfg["subtext"],
                             font=("Courier", 8),
                             bg=cfg.get("bg", "#504A49"),
                             fg=cfg.get("fg", "#59b7d1"))
        sub_label.pack(side="top", fill="x")

        for widget in (frame, main_label, sub_label):
            widget.bind("<Button-1>", lambda e, func=dummy_cmd: func())

        all_buttons.append({
            "type": "compound",
            "frame": frame,
            "main_label": main_label,
            "sub_label": sub_label,
            # We'll store the final X for association
            "final_x": scaled_x + offset_x,
            "width": scaled_w,
            "orig_bg": cfg.get("bg", "#504A49"),
            "orig_fg": cfg.get("fg", "white"),
            "orig_main_text": cfg["text"],
            "orig_sub_fg": cfg.get("fg", "#59b7d1"),
            "orig_sub_text": cfg["subtext"],
            "command_name": cmd_name
        })
    else:
        # Standard button
        btn = tk.Button(root,
                        text=cfg["text"],
                        font=("Courier", 11, "bold"),
                        command=dummy_cmd,
                        bg=cfg.get("bg", "#1e1818"),
                        fg=cfg.get("fg", "#dde8da"))
        btn.place(x=scaled_x + offset_x,
                  y=scaled_y + offset_y,
                  width=scaled_w, height=scaled_h)

        all_buttons.append({
            "type": "button",
            "widget": btn,
            # We'll store the final X for association
            "final_x": scaled_x + offset_x,
            "width": scaled_w,
            "command_name": cmd_name
        })

# 4) Re-place the f-labels if we're scaling
#    If scale=1.0, we skip re-placing them so they remain at original coords
if not (SCALE_X == 1.0 and SCALE_Y == 1.0):
    for lbl_dict in f_labels_list:
        w = lbl_dict["widget"]
        orig_x = lbl_dict["x"]
        orig_y = lbl_dict["y"]
        scaled_lbl_x = int(orig_x * SCALE_X)
        scaled_lbl_y = int(orig_y * SCALE_Y)
        w.place_configure(x=scaled_lbl_x + offset_x,
                          y=scaled_lbl_y + offset_y)

# 5) Associate each f-label with the nearest button horizontally
#    so the yellow f function will toggle them
for lbl_dict in f_labels_list:
    # Compute the final X for the label
    if SCALE_X == 1.0 and SCALE_Y == 1.0:
        final_lbl_x = lbl_dict["x"]
    else:
        final_lbl_x = int(lbl_dict["x"] * SCALE_X) + offset_x

    best_btn = None
    best_dist = float("inf")
    for btn_dict in all_buttons:
        dist = abs(final_lbl_x - btn_dict["final_x"])
        if dist < best_dist:
            best_dist = dist
            best_btn = btn_dict
    lbl_dict["associated_button"] = best_btn

# 6) Get the command map and rebind
from command_map import get_command_map
command_map = get_command_map(disp, memory, all_buttons, f_labels_list)

for btn_dict in all_buttons:
    c_name = btn_dict.get("command_name")
    if c_name and c_name in command_map:
        if btn_dict["type"] == "button":
            btn_dict["widget"].config(command=command_map[c_name])
        elif btn_dict["type"] == "compound":
            for widget in (btn_dict["frame"],
                           btn_dict["main_label"],
                           btn_dict["sub_label"]):
                widget.bind("<Button-1>", lambda e, func=command_map[c_name]: func())

print(f"Running partial-scale main.pyw (SCALE_X={SCALE_X}, SCALE_Y={SCALE_Y})")
root.mainloop()
