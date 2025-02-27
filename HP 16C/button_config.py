"""
button_config.py
----------------
Defines a list of dictionaries describing each button's text,
pixel coordinates, size, and the command name that maps to
functions in command_map.py. Also includes memory buttons (M+, M-, MR, MC).
"""

BUTTONS_CONFIG = [

    #COLUMN 1: /,*,-,+
    {"text": "/",                   "x": 630, "y": 80,  "width": 45, "height": 35, "command_name": "set_operator_div"},
    {"text": "*",                   "x": 630, "y": 140, "width": 45, "height": 35, "command_name": "set_operator_mul"},
    {"text": "-",                   "x": 630, "y": 200, "width": 45, "height": 35, "command_name": "set_operator_sub"},
    {"text": "+",                   "x": 630, "y": 260, "width": 45, "height": 35, "command_name": "set_operator_add"},
   
    #COLUMN 2: 9,6,3,CHS
    {"text": "9",                   "x": 560, "y": 80,  "width": 45, "height": 35, "command_name": "add_input_9"},    
    {"text": "6",                   "x": 560, "y": 140, "width": 45, "height": 35, "command_name": "add_input_6"},    
    {"text": "3",                   "x": 560, "y": 200, "width": 45, "height": 35, "command_name": "add_input_3"},
    {"text": "CHS",                 "x": 560, "y": 260, "width": 45, "height": 35, "command_name": "change_sign"},    
    
    #COLUMN 3: 8,5,2,.
    {"text": "8",                   "x": 490, "y": 80,  "width": 45, "height": 35, "command_name": "add_input_8"},
    {"text": "5",                   "x": 490, "y": 140, "width": 45, "height": 35, "command_name": "add_input_5"},
    {"text": "2",                   "x": 490, "y": 200, "width": 45, "height": 35, "command_name": "add_input_2"},    
    {"text": ".",                   "x": 490, "y": 260, "width": 45, "height": 35, "command_name": "add_input_dot"},    
    
    #COLUMN 4: 7,4,1,0
    {"text": "7",                   "x": 420, "y": 80,  "width": 45, "height": 35, "command_name": "add_input_7"},    
    {"text": "4",                   "x": 420, "y": 140, "width": 45, "height": 35, "command_name": "add_input_4"},    
    {"text": "1",                   "x": 420, "y": 200, "width": 45, "height": 35, "command_name": "add_input_1"},
    {"text": "0",                   "x": 420, "y": 260, "width": 45, "height": 35, "command_name": "add_input_0"},    

    # COLUMN 5: F, BIN, ENTER
    {"text": "F",                   "x": 350, "y": 80,  "width": 45, "height": 35, "command_name": "add_input_f"},
    {"text": "BIN",                 "x": 350, "y": 140, "width": 45, "height": 35, "command_name": "set_base_bin"}, 
    {"text": "E\nN\nT\nE\nR",       "x": 350, "y": 200, "width": 45, "height": 95,"command_name": "press_equals"}, 
    
    # COLUMN 6: E, OCT, MR, MC
    {"text": "E",                   "x": 280, "y": 80,  "width": 45, "height": 35, "command_name": "add_input_e"},
    {"text": "OCT",                 "x": 280, "y": 140, "width": 45, "height": 35, "command_name": "set_base_oct"},
    {"text": "MR",                  "x": 280, "y": 200, "width": 45, "height": 35, "command_name": "mem_recall"},
    {"text": "MC",                  "x": 280, "y": 260, "width": 45, "height": 35, "command_name": "mem_clear"},
    
    # COLUMN 7: D, DEC, C, D
    {"text": "D",                   "x": 210, "y": 80,  "width": 45, "height": 35, "command_name": "add_input_d"},
    {"text": "DEC",                 "x": 210, "y": 140, "width": 45, "height": 35, "command_name": "set_base_dec"},
    {"text": "C",                   "x": 210, "y": 200, "width": 45, "height": 35, "command_name": "add_input_c"},
    {"text": "D",                   "x": 210, "y": 260, "width": 45, "height": 35, "command_name": "add_input_d"},
    
    # COLUMN 8: C, HEX, G, H
    {"text": "C",                   "x": 140, "y": 80,  "width": 45, "height": 35, "command_name": "add_input_c"},
    {"text": "HEX",                 "x": 140, "y": 140, "width": 45, "height": 35, "command_name": "set_base_hex"},
    {"text": "G",                   "x": 140, "y": 200, "width": 45, "height": 35, "command_name": "add_input_g"},
    {"text": "g",                   "x": 140, "y": 260, "width": 45, "height": 35, "command_name": "blue_g_function", "bg": "#59b7d1", "fg": "black"},
    
    # COLUMN 9: B, J, K, L
    {"text": "B",                   "x": 70,  "y": 80,  "width": 45, "height": 35, "command_name": "add_input_b"},
    {"text": "J",                   "x": 70,  "y": 140, "width": 45, "height": 35, "command_name": "add_input_j"},
    {"text": "K",                   "x": 70,  "y": 200, "width": 45, "height": 35, "command_name": "add_input_k"},
    {"text": "f",                   "x": 70,  "y": 260, "width": 45, "height": 35, "command_name": "yellow_f_function", "bg": "#e3af01", "fg": "black"},
    
    # COLUMN 10: A, GSB, R/S, ON
    {"text": "A", "subtext": "LJ",      "x": 0,   "y": 80,  "width": 45, "height": 35, "command_name": "add_input_a"},
    {"text": "GSB", "subtext": "RTN",   "x": 0,   "y": 140, "width": 45, "height": 35, "command_name": "add_input_n"},
    {"text": "R/S", "subtext": "P/R",   "x": 0,   "y": 200, "width": 45, "height": 35, "command_name": "add_input_o"},
    {"text": "ON",                      "x": 0,   "y": 260, "width": 45, "height": 35, "command_name": "reload_program"}
]
