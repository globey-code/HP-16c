#button_config.py

BUTTONS_CONFIG = [



    # Example button entry clearly saving original colors:
{
    "top_label": "SR",      
    "main_label": "B",      
    "sub_label": "ASR",
    "x": 100, "y": 80, "width": 75, "height": 75, 
    "command_name": "add_input_b",
    "orig_bg": "#1e1818",
    "orig_top_label_fg": "#e3af01",
    "orig_main_label_fg": "white",
    "orig_sub_label_fg": "#59b7d1",
    "type": "compound"
},
# Repeat for ALL buttons clearly.





    # COLUMN 1
    # top_label: "XOR" "AND" "NOT" "OR"
    # main_label: "/" "*" "-" "+"
    # sub_label: "DBL/" "DBL*" "X>0" "X=0"
{
    "top_label": "XOR",
    "main_label": "/",              
    "sub_label": "DBL/",    
    "x": 900, "y": 80,  "width": 75, "height": 75, 
    "command_name": "set_operator_div",
    "orig_bg": "#1e1818",
    "orig_top_label_fg": "#e3af01",
    "orig_main_label_fg": "white",
    "orig_sub_label_fg": "#59b7d1",
    "type": "compound"
},
{
    "top_label": "AND",
    "main_label": "*",      
    "sub_label": "DBL*",
    "x": 900, "y": 180, "width": 75, "height": 75, 
    "command_name": "set_operator_mul"
},
{"top_label": "NOT",        "main_label": "-",              "sub_label": "X>0",    "x": 900, "y": 280, "width": 75, "height": 75, "command_name": "set_operator_sub"},
    {"top_label": "OR",         "main_label": "+",              "sub_label": "X=0",    "x": 900, "y": 380, "width": 75, "height": 75, "command_name": "set_operator_add"},
   
    # COLUMN 2
    # top_label: "RMD" "B?" "SC UNSGN" "EEXRRn"
    # main_label: "9" "6" "3" "CHS"
    # sub_label: "DBLR" "F?" "X>Y" "X=Y"
    {"top_label": "RMD",        "main_label": "9",              "sub_label": "DBLR",    "x": 800, "y": 80,  "width": 75, "height": 75, "command_name": "add_input_9"},    
    {"top_label": "B?",         "main_label": "6",              "sub_label": "F?",    "x": 800, "y": 180, "width": 75, "height": 75, "command_name": "add_input_6"},    
    {"top_label": "SC UNSGN",   "main_label": "3",              "sub_label": "X>Y",    "x": 800, "y": 280, "width": 75, "height": 75, "command_name": "add_input_3"},
    {"top_label": "EEXRRn",     "main_label": "CHS",            "sub_label": "X=Y",    "x": 800, "y": 380, "width": 75, "height": 75, "command_name": "change_sign"},    
    
    # COLUMN 3
    # top_label: "MASKR" "CB" "SC 2'S" "STATUS"
    # main_label: "8" "5" "2" "."
    # sub_label: "ABS" "CF" "X<0" "X\u22600"
    {"top_label": "MASKR",      "main_label": "8",              "sub_label": "ABS",    "x": 700, "y": 80,  "width": 75, "height": 75, "command_name": "add_input_8"},
    {"top_label": "CB",         "main_label": "5",              "sub_label": "CF",    "x": 700, "y": 180, "width": 75, "height": 75, "command_name": "add_input_5"},
    {"top_label": "SC 2'S",     "main_label": "2",              "sub_label": "X<0",    "x": 700, "y": 280, "width": 75, "height": 75, "command_name": "add_input_2"},    
    {"top_label": "STATUS",     "main_label": ".",              "sub_label": "X\u22600",    "x": 700, "y": 380, "width": 75, "height": 75, "command_name": "add_input_dot"},    
    
    # COLUMN 4
    # top_label: "MASKL" "SB" "1'S" "MEM"
    # main_label: "7" "4" "1" "0"
    # sub_label: "#B" "SF" "X\u2264Y" "X\u2260Y"
    {"top_label": "MASKL",      "main_label": "7",              "sub_label": "#B",    "x": 600, "y": 80,  "width": 75, "height": 75, "command_name": "add_input_7"},    
    {"top_label": "SB",         "main_label": "4",              "sub_label": "SF",    "x": 600, "y": 180, "width": 75, "height": 75, "command_name": "add_input_4"},    
    {"top_label": "1'S",        "main_label": "1",              "sub_label": "X\u2264Y",    "x": 600, "y": 280, "width": 75, "height": 75, "command_name": "add_input_1"},
    {"top_label": "MEM",        "main_label": "0",              "sub_label": "X\u2260Y",    "x": 600, "y": 380, "width": 75, "height": 75, "command_name": "add_input_0"},    

    # COLUMN 5
    # top_label: "RRn" "SHOW" "WINDOW"
    # main_label: "F" "BIN" "E\nN\nT\nE\nR"
    # sub_label: "RRCn" "1/x" "LST X"
    {"top_label": "RRn",        "main_label": "F",              "sub_label": "RRCn",    "x": 500, "y": 80,  "width": 75, "height": 75, "command_name": "add_input_f"},
    {"top_label": "SHOW BIN",       "main_label": "BIN",            "sub_label": "1/x",     "x": 500, "y": 180, "width": 75, "height": 75, "command_name": "set_base_bin"}, 
    {"top_label": "WINDOW",     "main_label": "E\nN\nT\nE\nR",  "sub_label": "LST X",   "x": 500, "y": 280, "width": 75, "height": 175,"command_name": "press_equals"}, 
    
    # COLUMN 6
    # top_label: "RLn" "SHOW" "CLR PRFX" "FLOAT"
    # main_label: "E" "OCT" "BSP" "RCL"
    # sub_label: "RLCn" "\u221Ax" "CLX" "\u2192"
    {"top_label": "RLn",        "main_label": "E",      "sub_label": "RLCn",            "x": 400, "y": 80,  "width": 75, "height": 75, "command_name": "add_input_e"},
    {"top_label": "SHOW OCT",       "main_label": "OCT",    "sub_label": "\u221Ax",         "x": 400, "y": 180, "width": 75, "height": 75, "command_name": "set_base_oct"},
    {"top_label": "CLR PRFX",   "main_label": "BSP",    "sub_label": "CLX",             "x": 400, "y": 280, "width": 75, "height": 75, "command_name": "backspace"},
    {"top_label": "FLOAT",      "main_label": "RCL",    "sub_label": "\u21db",          "x": 400, "y": 380, "width": 75, "height": 75, "command_name": "mem_clear"},
    {"top_label": "FLOAT",      "main_label": "RCL",    "sub_label": "\u2BC8",          "x": 400, "y": 380, "width": 75, "height": 75, "command_name": "mem_clear"},
    
    # COLUMN 7
    # top_label: "RR" "SHOW" "CLR REG" "WSIZE"
    # main_label: "D" "DEC" "x><y" "STO"
    # sub_label: "RRC" "ISZ" "PSE" "\u2190"
    {"top_label": "RR",         "main_label": "D",      "sub_label": "RRC",             "x": 300, "y": 80,  "width": 75, "height": 75, "command_name": "add_input_d"},
    {"top_label": "SHOW DEC",       "main_label": "DEC",    "sub_label": "ISZ",             "x": 300, "y": 180, "width": 75, "height": 75, "command_name": "set_base_dec"},
    {"top_label": "CLR REG",    "main_label": "x><y",   "sub_label": "PSE",             "x": 300, "y": 280, "width": 75, "height": 75, "command_name": "add_input_c"},
    {"top_label": "WSIZE",      "main_label": "STO",    "sub_label": "\u2b60",          "x": 300, "y": 380, "width": 75, "height": 75, "command_name": "add_input_d"},
    {"top_label": "WSIZE",      "main_label": "STO",    "sub_label": "\u2BC7",          "x": 300, "y": 380, "width": 75, "height": 75, "command_name": "add_input_d"},
    
    # COLUMN 8
    # top_label: "RL" "SHOW" "CLR PRGM"
    # main_label: "C" "HEX" "R\u2193" "g"
    # sub_label: "DSZ" "DSZ" "R\u2191"
    {"top_label": "RL",     "main_label": "C",          "sub_label": "DSZ",         "x": 200, "y": 80,  "width": 75, "height": 75, "command_name": "add_input_c"},
    {"top_label": "SHOW HEX",   "main_label": "HEX",        "sub_label": "DSZ",         "x": 200, "y": 180, "width": 75, "height": 75, "command_name": "set_base_hex"},
    {"top_label": "CLR PRGM",   "main_label": "R\u2193",    "sub_label": "R\u2191",     "x": 200, "y": 280, "width": 75, "height": 75, "command_name": "add_input_g"},
    {                       "main_label": "g",                                      "x": 200, "y": 380, "width": 75, "height": 75, "command_name": "blue_g_function", "bg": "#59b7d1", "fg": "black"},
    
    # COLUMN 9
    # top_label: "SR" "x><I" "I" "f"
    # main_label: "B" "GTO" "SST"
    # sub_label: "ASR" "LBL" "BST"
    {"top_label": "SR",      "main_label": "B",      "sub_label": "ASR",    "x": 100,  "y": 80,  "width": 75, "height": 75, "command_name": "add_input_b"},
    {"top_label": "x><I",    "main_label": "GTO",      "sub_label": "LBL",    "x": 100,  "y": 180, "width": 75, "height": 75, "command_name": "add_input_j"},
    {"top_label": "I",       "main_label": "SST",      "sub_label": "BST",    "x": 100,  "y": 280, "width": 75, "height": 75, "command_name": "add_input_k"},
    {"main_label": "f",                                                     "x": 100,  "y": 380, "width": 75, "height": 75, "command_name": "yellow_f_function", "bg": "#e3af01", "fg": "black"},
    
    # COLUMN 10 
    # top_label: "SL" "x><(i)" "(i)"
    # main_label: "A" "GSB" "R/S" "ON"
    # sub_label: "LJ" "RTN" "P/R"
    {"top_label": "SL",      "main_label": "A",      "sub_label": "LJ",     "x": 0, "y": 80,  "width": 75, "height": 75, "command_name": "add_input_a"},
    {"top_label": "x><(i)",  "main_label": "GSB",    "sub_label": "RTN",    "x": 0, "y": 180, "width": 75, "height": 75, "command_name": "add_input_n"},
    {"top_label": "(i)",     "main_label": "R/S",    "sub_label": "P/R",    "x": 0, "y": 280, "width": 75, "height": 75, "command_name": "add_input_o"},
    {                        "main_label": "ON",                            "x": 0, "y": 380, "width": 75, "height": 75, "command_name": "reload_program"}

]
