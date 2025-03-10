"""
f_key.py

Handles toggling 'f-mode' and binding the f_action to button clicks.
"""

from toggle_helpers import revert_to_normal
from f_function import f_action
from normal_state_function import get_display

f_mode_active = False

def toggle_f_state(button_widgets):
    global f_mode_active
    if f_mode_active:
        # Cancel f-mode
        for btn in button_widgets:
            if btn.get("command_name") in ("yellow_f_function", "blue_g_function"):
                continue
            revert_to_normal(btn, button_widgets, get_display())
        f_mode_active = False
        return

    # Activate f-mode
    f_mode_active = True
    for btn in button_widgets:
        if btn.get("command_name") in ("yellow_f_function", "blue_g_function"):
            continue
        revert_to_normal(btn, button_widgets, get_display())
        frame = btn["frame"]
        top_label = btn.get("top_label")
        if top_label:
            # highlight
            frame.config(bg="#e3af01")
            top_label.config(bg="#e3af01", fg="black")
            # etc...
            bind_widgets_to_f_action(btn, button_widgets)

def bind_widgets_to_f_action(btn, button_widgets):
    from normal_state_function import get_display
    def on_click(e, b=btn):
        f_action(b, get_display())
        # Turn off f-mode after the action
        toggle_f_state(button_widgets)

    for w in [btn["frame"], btn.get("top_label"), btn.get("main_label"), btn.get("sub_label")]:
        if w:
            w.bind("<Button-1>", on_click)
