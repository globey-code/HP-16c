"""
toggle_helpers.py

Helpers for reverting buttons to their normal state after toggling f or g mode.
"""

from normal_state_key import toggle_normal_state

def revert_to_normal(button, buttons=None, display=None):
    frame = button.get("frame")
    if frame:
        frame.config(bg=button.get("orig_bg", "#1e1818"))

    top_label = button.get("top_label")
    if top_label:
        top_label.config(
            fg=button.get("orig_top_fg", "#e3af01"),
            bg=button.get("orig_bg", "#1e1818"),
            text=button.get("orig_top_text", top_label.cget("text"))
        )
        top_label.place(relx=0.5, rely=0, anchor="n")

    main_label = button.get("main_label")
    if main_label:
        main_label.config(
            fg=button.get("orig_fg", "white"),
            bg=button.get("orig_bg", "#1e1818"),
            text=button.get("orig_main_text", main_label.cget("text"))
        )
        main_label.place(relx=0.5, rely=0.5, anchor="center")

    sub_label = button.get("sub_label")
    if sub_label:
        sub_label.config(
            fg=button.get("orig_sub_fg", "#59b7d1"),
            bg=button.get("orig_bg", "#1e1818"),
            text=button.get("orig_sub_text", sub_label.cget("text"))
        )
        sub_label.place(relx=0.5, rely=1, anchor="s")

    if buttons is not None and display is not None:
        cmd = button.get("command_name")
        if cmd not in ("yellow_f_function", "blue_g_function", "reload_program"):
            toggle_normal_state(button, buttons, display)
