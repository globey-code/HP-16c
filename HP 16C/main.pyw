import tkinter as tk
import tkinter.font as tkFont
from ui import setup_ui
from button_state_manager import ButtonStateManager
from configuration import load_config
from normal_state_function import set_display
#from keyboard_input import restrict_input

def main():
    root = tk.Tk()
    root.title("HP 16C Emulator")
    root.iconbitmap("images/HP16C_Logo.ico")
    root.configure(bg="#1e1818")
    root.resizable(False, False)

    #restrict_input(root)  # <-- Optionally restrict keyboard input

    config = load_config()

    try:
        custom_font = tkFont.Font(family="Courier", size=18)
    except Exception:
        custom_font = ("Courier", 18)

    # Create the UI (returns display and buttons)
    disp, buttons = setup_ui(root, config, custom_font)
    set_display(disp)

    # Start periodic stack updates
    disp.schedule_stack_updates()

    # Initialize button states
    button_manager = ButtonStateManager(buttons, disp)
    button_manager.bind_button_states()

    print("Running HP 16C Emulator")
    root.mainloop()

if __name__ == "__main__":
    main()
