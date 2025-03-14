"""
button_state_manager.py

Binds each button to the correct method in the controller or modes.
No circular import: we only import 'controller' if needed.
"""

from modes import toggle_f_mode, toggle_g_mode, do_shift_left, f_mode_active, g_mode_active

class ButtonStateManager:
    def __init__(self, button_widgets, controller):
        self.button_widgets = button_widgets
        self.controller = controller

    def bind_button_states(self):
        for btn in self.button_widgets:
            cmd_name = btn.get("command_name", "")
            if cmd_name == "toggle_f_mode":
                self._bind_toggle_f(btn)
            elif cmd_name == "toggle_g_mode":
                self._bind_toggle_g(btn)
            elif cmd_name == "shift_left_f":
                self._bind_shift_left_f(btn)
            else:
                self._bind_normal(btn)

    def _bind_toggle_f(self, btn):
        def on_click(e):
            toggle_f_mode()
        self._bind_to_all_widgets(btn, on_click)

    def _bind_toggle_g(self, btn):
        def on_click(e):
            toggle_g_mode()
        self._bind_to_all_widgets(btn, on_click)

    def _bind_shift_left_f(self, btn):
        """
        Example: calls do_shift_left(...) from modes.py, passing the controller.
        """
        def on_click(e):
            do_shift_left(self.controller)
        self._bind_to_all_widgets(btn, on_click)

    def _bind_normal(self, btn):
        """
        Default: interpret command_name as a controller method.
        E.g., "enter_value" => self.controller.enter_value()
        """
        def on_click(e):
            cmd = btn.get("command_name", "")
            if cmd == "enter_value":
                self.controller.enter_value()
            elif cmd == "add_digit_5":
                self.controller.enter_digit("5")
            elif cmd == "op_plus":
                self.controller.enter_operator("+")
            # etc.
        self._bind_to_all_widgets(btn, on_click)

    def _bind_to_all_widgets(self, btn, func):
        for w in [btn["frame"], btn.get("top_label"), btn.get("main_label"), btn.get("sub_label")]:
            if w:
                w.bind("<Button-1>", func)
