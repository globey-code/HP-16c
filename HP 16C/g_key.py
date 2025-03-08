# g_key.py
from toggle_helpers import revert_to_normal
from g_function import g_action
from normal_state_function import get_display  # assume this returns the display

# Global flag to track whether g-mode is active.
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
        frame = btn["frame"]
        sub_label = btn.get("sub_label")
        if sub_label:
            frame.config(bg="#59b7d1")
            sub_label.config(bg="#59b7d1", fg="black")
            sub_label.place(relx=0.5, rely=0.5, anchor="center")
            if btn.get("main_label"):
                btn.get("main_label").place_forget()
            if btn.get("top_label"):
                btn.get("top_label").place_forget()
            bind_widgets_to_g_action(btn, button_widgets)

def bind_widgets_to_g_action(btn, button_widgets):
    widgets = [
        btn["frame"],
        btn.get("sub_label"),
        btn.get("main_label"),
        btn.get("top_label")
    ]
    for widget in widgets:
        if widget:
            widget.bind("<Button-1>", lambda e, b=btn: execute_g_action(b, button_widgets))

def execute_g_action(button, button_widgets):
    global g_mode_active
    g_action(button)
    for btn in button_widgets:
        if btn.get("command_name") in ("blue_g_function", "yellow_f_function"):
            continue
        revert_to_normal(btn, button_widgets, get_display())
    g_mode_active = False
