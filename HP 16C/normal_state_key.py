from normal_state_function import normal_action_digit, normal_action_operator, normal_action_special
from mode_manager import is_input_allowed

def toggle_normal_state(btn, buttons, display):
    # Normalize the label by removing newline characters and extra spaces.
    label = btn.get("orig_main_text", "").replace("\n", "").strip()

    # If this is the ON button, skip normal state binding.
    if label.upper() == "ON":
        return

    def click_handler(e):
        e.widget.event_generate("<<NormalClick>>")

    def normal_handler(e):
        # For digit/alpha input, check if allowed.
        if label.isdigit() or label.upper() in "ABCDEF":
            if not is_input_allowed(label):
                print(f"Ignored '{label}' - invalid in current mode.")
                return
        
        if label.isdigit():
            normal_action_digit(label)
        elif label in {"+", "-", "*", "/"}:
            normal_action_operator(label)
        else:
            normal_action_special(label, buttons, display)

    for widget in [btn["frame"], btn.get("top_label"), btn.get("main_label"), btn.get("sub_label")]:
        if widget and hasattr(widget, "bind"):
            widget.bind("<Button-1>", click_handler)
            widget.bind("<<NormalClick>>", normal_handler)
