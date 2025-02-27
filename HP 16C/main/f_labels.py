from PIL import Image, ImageTk
import tkinter as tk

def create_labels(root):
    labels = []  # Initialize the list to hold label dictionaries.
    
    # Yellow f Function KEYS
    SECTION_LABELS = [
        # ROW 1
        {"text": "XOR",         "x": 658, "y": 222},
        {"text": "RMD",         "x": 586, "y": 222},
        {"text": "MASKR",       "x": 510, "y": 222},
        {"text": "MASKL",       "x": 441, "y": 222},
        {"text": "RRn",         "x": 380, "y": 222},
        {"text": "RLn",         "x": 310, "y": 222},
        {"text": "RR",          "x": 241, "y": 222},
        {"text": "RL",          "x": 172, "y": 222},
        {"text": "SR",          "x": 101, "y": 222},
        {"text": "SL",          "x": 32,  "y": 222},
        
        # ROW 2
        {"text": "AND",         "x": 658, "y": 282},
        {"text": "B?",          "x": 594, "y": 282},
        {"text": "CB",          "x": 522, "y": 282},
        {"text": "SB",          "x": 453, "y": 282},
        {"text": "SHOW",        "x": 268, "y": 282},
        {"text": "x > < I",     "x": 94,  "y": 282},
        {"text": "x > < (i)",   "x": 20,  "y": 282},        
        
        # ROW 3
        {"text": "NOT",         "x": 658, "y": 342},
        {"text": "UNSGN",       "x": 580, "y": 342},
        {"text": "2'S",         "x": 522, "y": 342},
        {"text": "1'S",         "x": 453, "y": 342},
        {"text": "WINDOW",      "x": 367, "y": 342},
        {"text": "PRGM",        "x": 165, "y": 342},
        {"text": "REG",         "x": 239, "y": 342},
        {"text": "PREFIX",      "x": 302, "y": 342},
        
        # ROW 4
        {"text": "OR",          "x": 661, "y": 402},
        {"text": "WSIZE",       "x": 232, "y": 402},
        {"text": "FLOAT",       "x": 301, "y": 402},
    ]
    
    for section in SECTION_LABELS:
        lbl = tk.Label(
            root,
            text=section["text"],
            fg="#e3af01",
            bg="#1e1818",
            font=("Arial", 8)
        )
        lbl.place(x=section["x"], y=section["y"])
        labels.append({
            "widget": lbl,
            "x": section["x"],
            "y": section["y"],
            "orig_text": section["text"],
            "orig_fg": "#e3af01",
            "orig_bg": "#1e1818",
            "associated_button": None  # Will be set later in main.pyw
        })
    
    # (Optional) If you need to create additional small labels or image labels,
    # you can do so here without adding them to the toggle list.
    
    # Create the CLEAR image label (not added to toggle list)
    clear_label = Image.open("images/CLEAR.png").resize((30, 9), resample=Image.Resampling.LANCZOS)
    clear_image = ImageTk.PhotoImage(clear_label)
    clabel = tk.Label(root, image=clear_image, bg="#1e1818")
    clabel.image = clear_image  # keep reference
    clabel.place(x=236, y=334)
    clabel.lift()
    
    # Create the SET COMPL image label (not added to toggle list)
    set_compl_label = Image.open("images/SET_COMPL.png").resize((36, 14), resample=Image.Resampling.LANCZOS)
    set_compl_image = ImageTk.PhotoImage(set_compl_label)
    scom_label = tk.Label(root, image=set_compl_image, bg="#1e1818")
    scom_label.image = set_compl_image  # keep reference
    scom_label.place(x=512, y=331)
    scom_label.lift()

    # Create the CLEAR image label
    clear_label_1 = Image.open("images/CLEAR.png").resize((30, 9), resample=Image.Resampling.LANCZOS)
    clear_image_1 = ImageTk.PhotoImage(clear_label_1)

    clear_label_1 = tk.Label(root, image=clear_image_1, bg="#1e1818")
    clear_label_1.image = clear_image_1  # Keep a reference so it's not garbage collected
    clear_label_1.place(x=236, y=334)
    clear_label_1.lift()  # Bring this image on top of other widgets
    
    # Create the SET COMPL image label
    set_compl_label_2 = Image.open("images/SET_COMPL.png").resize((36, 14), resample=Image.Resampling.LANCZOS)
    set_compl_image_2 = ImageTk.PhotoImage(set_compl_label_2)

    set_compl_label_2 = tk.Label(root, image=set_compl_image_2, bg="#1e1818")
    set_compl_label_2.image = set_compl_image_2  # Keep a reference so it's not garbage collected
    set_compl_label_2.place(x=512, y=331)
    set_compl_label_2.lower()  # Bring this image on top of other widgets
    

    # LEFT CLEAR YELLOW INDICATOR 
    yellow_label_clear_left = Image.open("images/yellow_indicator_left.png").resize((75, 9), resample=Image.Resampling.LANCZOS)
    yellow_image_clear_left = ImageTk.PhotoImage(yellow_label_clear_left)
    
    yellow_label_clear_left = tk.Label(root, image=yellow_image_clear_left, bg="#1e1818")
    yellow_label_clear_left.image = yellow_image_clear_left
    yellow_label_clear_left.place(x=155, y=336)
    yellow_label_clear_left.lower()  # Push it behind the other widgets
    
    # RIGHT CLEAR YELLOW INDICATOR 
    yellow_label_clear_right = Image.open("images/yellow_indicator_right.png").resize((75, 9), resample=Image.Resampling.LANCZOS)
    yellow_image_clear_right = ImageTk.PhotoImage(yellow_label_clear_right)
    
    yellow_label_clear_right = tk.Label(root, image=yellow_image_clear_right, bg="#1e1818")
    yellow_label_clear_right.image = yellow_image_clear_right
    yellow_label_clear_right.place(x=270, y=336)
    yellow_label_clear_right.lower()  # Push it behind the other widgets
    
    # LEFT SET COMPL YELLOW INDICATOR 
    yellow_label_set_compl_left = Image.open("images/yellow_indicator_left.png").resize((75, 9), resample=Image.Resampling.LANCZOS)
    yellow_image_set_compl_left = ImageTk.PhotoImage(yellow_label_set_compl_left)

    yellow_label_set_compl_left = tk.Label(root, image=yellow_image_set_compl_left, bg="#1e1818")
    yellow_label_set_compl_left.image = yellow_image_set_compl_left
    yellow_label_set_compl_left.place(x=435, y=336)
    yellow_label_set_compl_left.lower()  # Push it behind the other widgets

    # RIGHT SET COMPL YELLOW INDICATOR 
    yellow_image_set_compl_right = Image.open("images/yellow_indicator_right.png").resize((75, 9), resample=Image.Resampling.LANCZOS)
    yellow_image_set_compl_right = ImageTk.PhotoImage(yellow_image_set_compl_right)

    yellow_label_set_compl_right = tk.Label(root, image=yellow_image_set_compl_right, bg="#1e1818")
    yellow_label_set_compl_right.image = yellow_image_set_compl_right
    yellow_label_set_compl_right.place(x=550, y=336)
    yellow_label_set_compl_right.lower()  # Push it behind the other widgets
    
    # LEFT SHOW YELLOW INDICATOR 
    yellow_label_show_left = Image.open("images/yellow_indicator_left.png").resize((100, 9), resample=Image.Resampling.LANCZOS)
    yellow_image_show_left = ImageTk.PhotoImage(yellow_label_show_left)

    yellow_label_show_left = tk.Label(root, image=yellow_image_show_left, bg="#1e1818")
    yellow_label_show_left.image = yellow_image_show_left
    yellow_label_show_left.place(x=155, y=285)
    yellow_label_show_left.lower()  # Push it behind the other widgets

    # RIGHT SHOW YELLOW INDICATOR 
    yellow_label_show_right = Image.open("images/yellow_indicator_right.png").resize((100, 9), resample=Image.Resampling.LANCZOS)
    yellow_image_show_right = ImageTk.PhotoImage(yellow_label_show_right)

    yellow_label_show_right = tk.Label(root, image=yellow_image_show_right, bg="#1e1818")
    yellow_label_show_right.image = yellow_image_show_right
    yellow_label_show_right.place(x=316, y=285)
    yellow_label_show_right.lower()  # Push it behind the other widgets
    

    return labels
    

if __name__ == "__main__":
    root = tk.Tk()
    root.title("HP 16C Emulator")
    root.geometry("600x450")
    create_labels(root)
    root.mainloop()
