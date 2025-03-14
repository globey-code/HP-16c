def initialize_states(display, buttons):
    set_display(display)

    for btn in buttons:
        cmd_name = btn["command_name"]
        if cmd_name == "yellow_f_function":
            bind_toggle(btn, lambda e: toggle_f_state(buttons))
        elif cmd_name == "blue_g_function":
            bind_toggle(btn, lambda e: toggle_g_state(buttons))
        else:
            toggle_normal_state(btn, buttons, display)

def bind_toggle(btn, handler):
    widgets = [btn["frame"], btn.get("top_label"), btn.get("main_label"), btn.get("sub_label")]
    for widget in widgets:
        if widget:
            widget.bind("<Button-1>", handler)