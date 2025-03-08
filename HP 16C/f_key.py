# f_key.py
from toggle_helpers import revert_to_normal
from f_function import f_action
from normal_state_function import get_display  # assume this returns the current display

# Global flag to track whether f-mode is active.
f_mode_active = False

def toggle_f_state(button_widgets):
    global f_mode_active
    # If f-mode is already active, cancel it.
    if f_mode_active:
        for btn in button_widgets:
            if btn.get("command_name") in ("yellow_f_function", "blue_g_function"):
                continue
            revert_to_normal(btn, button_widgets, get_display())
        f_mode_active = False
        return

    # Activate f-mode.
    f_mode_active = True
    for btn in button_widgets:
        if btn.get("command_name") in ("yellow_f_function", "blue_g_function"):
            continue

        revert_to_normal(btn, button_widgets, get_display())
        frame = btn["frame"]
        top_label = btn.get("top_label")
        if top_label:
            frame.config(bg="#e3af01")
            top_label.config(bg="#e3af01", fg="black")
            top_label.place(relx=0.5, rely=0.5, anchor="center")
            if btn.get("main_label"):
                btn.get("main_label").place_forget()
            if btn.get("sub_label"):
                btn.get("sub_label").place_forget()
            bind_widgets_to_f_action(btn, button_widgets)

def bind_widgets_to_f_action(btn, button_widgets):
    widgets = [
        btn["frame"],
        btn.get("top_label"),
        btn.get("main_label"),
        btn.get("sub_label")
    ]
    for widget in widgets:
        if widget:
            widget.bind("<Button-1>", lambda e, b=btn: execute_f_action(b, button_widgets))

def execute_f_action(button, button_widgets):
    global f_mode_active
    f_action(button)
    for btn in button_widgets:
        if btn.get("command_name") in ("yellow_f_function", "blue_g_function"):
            continue
        revert_to_normal(btn, button_widgets, get_display())
    f_mode_active = False
