from f_key import toggle_f_state
from g_key import toggle_g_state
from normal_state_key import toggle_normal_state
from normal_state_function import set_display
from reload import reload_program  # Import the reload function

class ButtonStateManager:
    def __init__(self, button_widgets, display):
        self.button_widgets = button_widgets
        self.display = display

    def bind_button_states(self):
        set_display(self.display)

        for btn in self.button_widgets:
            cmd_name = btn.get("command_name")
            if cmd_name == "yellow_f_function":
                self.bind_f_button(btn)
            elif cmd_name == "blue_g_function":
                self.bind_g_button(btn)
            elif cmd_name == "reload_program":
                self.bind_reload_button(btn)
            else:
                self.bind_normal_button(btn)

    def bind_f_button(self, btn):
        widgets = [btn["frame"], btn.get("top_label"), btn.get("main_label"), btn.get("sub_label")]
        for widget in widgets:
            if widget:
                widget.bind("<Button-1>", lambda e, btns=self.button_widgets: toggle_f_state(btns))

    def bind_g_button(self, btn):
        widgets = [btn["frame"], btn.get("top_label"), btn.get("main_label"), btn.get("sub_label")]
        for widget in widgets:
            if widget:
                widget.bind("<Button-1>", lambda e, btns=self.button_widgets: toggle_g_state(btns))

    def bind_reload_button(self, btn):
        # Bind only to the reload (ON) button. Do not let normal state binding override this.
        widgets = [btn["frame"], btn.get("top_label"), btn.get("main_label"), btn.get("sub_label")]
        for widget in widgets:
            if widget:
                widget.bind("<Button-1>", lambda e: reload_program())

    def bind_normal_button(self, btn):
        toggle_normal_state(btn, self.button_widgets, self.display)
