"""
button_config.py

Layout data for all buttons using a dynamic grid system (row, col).
Each button is defined with row and column indices instead of absolute x, y coordinates.
Width and height remain as pixel values for consistency with the original design.
"""

BUTTONS_CONFIG = [
    # COLUMN 0 (leftmost column, originally x=0)
    # top_label: "SL" "x><(i)" "(i)"
    # main_label: "A" "GSB" "R/S" "ON"
    # sub_label: "LJ" "RTN" "P/R"
    {
        "top_label": "SL",
        "main_label": "A",
        "sub_label": "LJ",
        "row": 0, "col": 0, "width": 75, "height": 75,
    },
    {
        "top_label": "x><(i)",
        "main_label": "GSB",
        "sub_label": "RTN",
        "row": 1, "col": 0, "width": 75, "height": 75,
    },
    {
        "top_label": "(i)",
        "main_label": "R/S",
        "sub_label": "P/R",
        "row": 2, "col": 0, "width": 75, "height": 75,
    },
    {
        "main_label": "ON",
        "row": 3, "col": 0, "width": 75, "height": 75,
        "command_name": "reload_program"
    },

    # COLUMN 1 (originally x=100)
    # top_label: "SR" "x><I" "I" "f"
    # main_label: "B" "GTO" "SST"
    # sub_label: "ASR" "LBL" "BST"
    {
        "top_label": "SR",
        "main_label": "B",
        "sub_label": "ASR",
        "row": 0, "col": 1, "width": 75, "height": 75,
    },
    {
        "top_label": "x><I",
        "main_label": "GTO",
        "sub_label": "LBL",
        "row": 1, "col": 1, "width": 75, "height": 75,
    },
    {
        "top_label": "I",
        "main_label": "SST",
        "sub_label": "BST",
        "row": 2, "col": 1, "width": 75, "height": 75,
    },
    {
        "main_label": "f",
        "row": 3, "col": 1, "width": 75, "height": 75,
        "command_name": "yellow_f_function", "bg": "#e3af01", "fg": "black"
    },

    # COLUMN 2 (originally x=200)
    # top_label: "RL" "SHOW" "CLR PRGM"
    # main_label: "C" "HEX" "R↓" "g"
    # sub_label: "DSZ" "DSZ" "R↑"
    {
        "top_label": "RL",
        "main_label": "C",
        "sub_label": "DSZ",
        "row": 0, "col": 2, "width": 75, "height": 75,
    },
    {
        "top_label": "SHOW HEX",
        "main_label": "HEX",
        "sub_label": "DSZ",
        "row": 1, "col": 2, "width": 75, "height": 75,
        "command_name": "set_base_hex"
    },
    {
        "top_label": "CLR PRGM",
        "main_label": "R\u2193",
        "sub_label": "R\u2191",
        "row": 2, "col": 2, "width": 75, "height": 75,
    },
    {
        "main_label": "g",
        "row": 3, "col": 2, "width": 75, "height": 75,
        "command_name": "blue_g_function", "bg": "#59b7d1", "fg": "black"
    },

    # COLUMN 3 (originally x=300)
    # top_label: "RR" "SHOW" "CLR REG" "WSIZE"
    # main_label: "D" "DEC" "x><y" "STO"
    # sub_label: "RRC" "ISZ" "PSE" "←"
    {
        "top_label": "RR",
        "main_label": "D",
        "sub_label": "RRC",
        "row": 0, "col": 3, "width": 75, "height": 75,
    },
    {
        "top_label": "SHOW DEC",
        "main_label": "DEC",
        "sub_label": "ISZ",
        "row": 1, "col": 3, "width": 75, "height": 75,
    },
    {
        "top_label": "CLR REG",
        "main_label": "x><y",
        "sub_label": "PSE",
        "row": 2, "col": 3, "width": 75, "height": 75,
    },
    {
        "top_label": "WSIZE",
        "main_label": "STO",
        "sub_label": "\u2BC7",
        "row": 3, "col": 3, "width": 75, "height": 75,
    },

    # COLUMN 4 (originally x=400)
    # top_label: "RLn" "SHOW" "CLR PRFX" "FLOAT"
    # main_label: "E" "OCT" "BSP" "RCL"
    # sub_label: "RLCn" "√x" "CLX" "→"
    {
        "top_label": "RLn",
        "main_label": "E",
        "sub_label": "RLCn",
        "row": 0, "col": 4, "width": 75, "height": 75,
    },
    {
        "top_label": "SHOW OCT",
        "main_label": "OCT",
        "sub_label": "\u221Ax",
        "row": 1, "col": 4, "width": 75, "height": 75,
    },
    {
        "top_label": "CLR PRFX",
        "main_label": "BSP",
        "sub_label": "CLX",
        "row": 2, "col": 4, "width": 75, "height": 75,
    },
    {
        "top_label": "FLOAT",
        "main_label": "RCL",
        "sub_label": "\u2BC8",
        "row": 3, "col": 4, "width": 75, "height": 75,
    },

    # COLUMN 5 (originally x=500)
    # top_label: "RRn" "SHOW" "WINDOW"
    # main_label: "F" "BIN" "ENTER"
    # sub_label: "RRCn" "1/x" "LST X"
    {
        "top_label": "RRn",
        "main_label": "F",
        "sub_label": "RRCn",
        "row": 0, "col": 5, "width": 75, "height": 75,
    },
    {
        "top_label": "SHOW BIN",
        "main_label": "BIN",
        "sub_label": "1/x",
        "row": 1, "col": 5, "width": 75, "height": 75,
    },
    {
        "top_label": "WINDOW",
        "main_label": "E\nN\nT\nE\nR",
        "sub_label": "LST X",
        "row": 2, "col": 5, "width": 75, "height": 175,  # Spans 2 rows
        "rowspan": 2
    },

    # COLUMN 6 (originally x=600)
    # top_label: "MASKL" "SB" "SC 1'S" "MEM"
    # main_label: "7" "4" "1" "0"
    # sub_label: "#B" "SF" "X≤Y" "X≠Y"
    {
        "top_label": "MASKL",
        "main_label": "7",
        "sub_label": "#B",
        "row": 0, "col": 6, "width": 75, "height": 75,
    },
    {
        "top_label": "SB",
        "main_label": "4",
        "sub_label": "SF",
        "row": 1, "col": 6, "width": 75, "height": 75,
    },
    {
        "top_label": "SC 1'S",
        "main_label": "1",
        "sub_label": "X\u2264Y",
        "row": 2, "col": 6, "width": 75, "height": 75,
    },
    {
        "top_label": "MEM",
        "main_label": "0",
        "sub_label": "X\u2260Y",
        "row": 3, "col": 6, "width": 75, "height": 75,
    },

    # COLUMN 7 (originally x=700)
    # top_label: "MASKR" "CB" "SC 2'S" "STATUS"
    # main_label: "8" "5" "2" "."
    # sub_label: "ABS" "CF" "X<0" "X≠0"
    {
        "top_label": "MASKR",
        "main_label": "8",
        "sub_label": "ABS",
        "row": 0, "col": 7, "width": 75, "height": 75,
    },
    {
        "top_label": "CB",
        "main_label": "5",
        "sub_label": "CF",
        "row": 1, "col": 7, "width": 75, "height": 75,
    },
    {
        "top_label": "SC 2'S",
        "main_label": "2",
        "sub_label": "X<0",
        "row": 2, "col": 7, "width": 75, "height": 75,
    },
    {
        "top_label": "STATUS",
        "main_label": ".",
        "sub_label": "X\u22600",
        "row": 3, "col": 7, "width": 75, "height": 75,
    },

    # COLUMN 8 (originally x=800)
    # top_label: "RMD" "B?" "SC UNSGN" "EEXRRn"
    # main_label: "9" "6" "3" "CHS"
    # sub_label: "DBLR" "F?" "X>Y" "X=Y"
    {
        "top_label": "RMD",
        "main_label": "9",
        "sub_label": "DBLR",
        "row": 0, "col": 8, "width": 75, "height": 75,
    },
    {
        "top_label": "B?",
        "main_label": "6",
        "sub_label": "F?",
        "row": 1, "col": 8, "width": 75, "height": 75,
    },
    {
        "top_label": "SC UNSGN",
        "main_label": "3",
        "sub_label": "X>Y",
        "row": 2, "col": 8, "width": 75, "height": 75,
    },
    {
        "top_label": "EEx",
        "main_label": "CHS",
        "sub_label": "X=Y",
        "row": 3, "col": 8, "width": 75, "height": 75,
    },

    # COLUMN 9 (rightmost column, originally x=900)
    # top_label: "XOR" "AND" "NOT" "OR"
    # main_label: "/" "*" "-" "+"
    # sub_label: "DBL/" "DBL*" "X>0" "X=0"
    {
        "top_label": "XOR",
        "main_label": "/",
        "sub_label": "DBL/",
        "row": 0, "col": 9, "width": 75, "height": 75,
    },
    {
        "top_label": "AND",
        "main_label": "*",
        "sub_label": "DBL*",
        "row": 1, "col": 9, "width": 75, "height": 75,
    },
    {
        "top_label": "NOT",
        "main_label": "-",
        "sub_label": "X>0",
        "row": 2, "col": 9, "width": 75, "height": 75,
    },
    {
        "top_label": "OR",
        "main_label": "+",
        "sub_label": "X=0",
        "row": 3, "col": 9, "width": 75, "height": 75,
    },
]