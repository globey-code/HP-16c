"""
g_key.py

Handles toggling 'g-mode' and binding the g_action to button clicks.
"""

from toggle_helpers import revert_to_normal
from g_function import g_action
from normal_state_function import get_display

g_mode_active = False

def toggle_g_state(button_widgets):
    global g_mode_active
    if g_mode_active:
        for btn in button_widgets:
            if btn.get("command_name") in ("blue_g_function", "yellow_f_function"):
                continue
            revert_to_normal(btn, button_widgets, get_display())
        g_mode_active = False
        return

    g_mode_active = True
    for btn in button_widgets:
        if btn.get("command_name") in ("blue_g_function", "yellow_f_function"):
            continue
        revert_to_normal(btn, button_widgets, get_display())
        # highlight sub_label, bind to g_action
        bind_widgets_to_g_action(btn, button_widgets)

def bind_widgets_to_g_action(btn, button_widgets):
    from normal_state_function import get_display
    def on_click(e, b=btn):
        g_action(b)
        toggle_g_state(button_widgets)

    for w in [btn["frame"], btn.get("sub_label"), btn.get("main_label"), btn.get("top_label")]:
        if w:
            w.bind("<Button-1>", on_click)
