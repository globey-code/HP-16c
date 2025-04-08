"""
button_config.py
Defines the button layout configuration for the HP-16C emulator using a dataclass-based grid system.
Author: GlobeyCode
License: MIT
Created: 3/23/2025
Last Modified: 4/06/2025
Dependencies: Python 3.6+, dataclasses, typing
"""

from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class ButtonConfig:
    """
    Represents the configuration for a single button in the emulator.
    
    Attributes:
        top_label: The text for the top label (optional).
        main_label: The primary label text.
        sub_label: The text for the sub label (optional).
        row: The grid row in which the button appears.
        col: The grid column in which the button appears.
        width: The button width in pixels.
        height: The button height in pixels.
        command_name: (Optional) A command string that defines special behavior.
        bg: Background color (default "#1e1818").
        fg: Foreground (text) color (default "#e3af01").
        rowspan: The number of rows this button spans (default 1).
    """
    top_label: Optional[str] = None
    main_label: Optional[str] = None
    sub_label: Optional[str] = None
    row: int = 0
    col: int = 0
    width: int = 75
    height: int = 75
    command_name: Optional[str] = None
    bg: str = "#1e1818"
    fg: str = "#e3af01"
    rowspan: int = 1


# List of all button configurations.
BUTTONS_CONFIG: List[ButtonConfig] = [
    # COLUMN 0 (leftmost column, originally x=0)
    ButtonConfig(top_label="SL", main_label="A", sub_label="LJ", row=0, col=0),
    ButtonConfig(top_label="x><(i)", main_label="GSB", sub_label="RTN", row=1, col=0),
    ButtonConfig(top_label="(i)", main_label="R/S", sub_label="P/R", row=2, col=0),
    ButtonConfig(main_label="ON", row=3, col=0, command_name="reload_program"),
    
    # COLUMN 1 (originally x=100)
    ButtonConfig(top_label="SR", main_label="B", sub_label="ASR", row=0, col=1),
    ButtonConfig(top_label="x><I", main_label="GTO", sub_label="LBL", row=1, col=1),
    ButtonConfig(top_label="I", main_label="SST", sub_label="BST", row=2, col=1),
    ButtonConfig(main_label="f", row=3, col=1, command_name="yellow_f_function", bg="#e3af01", fg="black"),
    
    # COLUMN 2 (originally x=200)
    ButtonConfig(top_label="RL", main_label="C", sub_label="DSZ", row=0, col=2),
    ButtonConfig(top_label="SHOW HEX", main_label="HEX", sub_label="DSZ", row=1, col=2, command_name="set_base_hex"),
    ButtonConfig(top_label="CLR PRGM", main_label="R↓", sub_label="R↑", row=2, col=2),
    ButtonConfig(main_label="g", row=3, col=2, command_name="blue_g_function", bg="#59b7d1", fg="black"),
    
    # COLUMN 3 (originally x=300)
    ButtonConfig(top_label="RR", main_label="D", sub_label="RRC", row=0, col=3),
    ButtonConfig(top_label="SHOW DEC", main_label="DEC", sub_label="ISZ", row=1, col=3),
    ButtonConfig(top_label="CLR REG", main_label="x><y", sub_label="PSE", row=2, col=3),
    ButtonConfig(top_label="WSIZE", main_label="STO", sub_label="⯇", row=3, col=3),
    
    # COLUMN 4 (originally x=400)
    ButtonConfig(top_label="RLn", main_label="E", sub_label="RLCn", row=0, col=4),
    ButtonConfig(top_label="SHOW OCT", main_label="OCT", sub_label="√x", row=1, col=4),
    ButtonConfig(top_label="CLR PRFX", main_label="BSP", sub_label="CLX", row=2, col=4),
    ButtonConfig(top_label="FLOAT", main_label="RCL", sub_label="⯈", row=3, col=4),
    
    # COLUMN 5 (originally x=500)
    ButtonConfig(top_label="RRn", main_label="F", sub_label="RRCn", row=0, col=5),
    ButtonConfig(top_label="SHOW BIN", main_label="BIN", sub_label="1/x", row=1, col=5),
    ButtonConfig(top_label="WINDOW", main_label="E\nN\nT\nE\nR", sub_label="LST X", row=2, col=5, height=175, rowspan=2),
    
    # COLUMN 6 (originally x=600)
    ButtonConfig(top_label="MASKL", main_label="7", sub_label="#B", row=0, col=6),
    ButtonConfig(top_label="SB", main_label="4", sub_label="SF", row=1, col=6),
    ButtonConfig(top_label="SC 1'S", main_label="1", sub_label="X≤Y", row=2, col=6),
    ButtonConfig(top_label="MEM", main_label="0", sub_label="X≠Y", row=3, col=6),
    
    # COLUMN 7 (originally x=700)
    ButtonConfig(top_label="MASKR", main_label="8", sub_label="ABS", row=0, col=7),
    ButtonConfig(top_label="CB", main_label="5", sub_label="CF", row=1, col=7),
    ButtonConfig(top_label="SC 2'S", main_label="2", sub_label="X<0", row=2, col=7),
    ButtonConfig(top_label="STATUS", main_label=".", sub_label="X≠0", row=3, col=7),
    
    # COLUMN 8 (originally x=800)
    ButtonConfig(top_label="RMD", main_label="9", sub_label="DBLR", row=0, col=8),
    ButtonConfig(top_label="B?", main_label="6", sub_label="F?", row=1, col=8),
    ButtonConfig(top_label="SC UNSGN", main_label="3", sub_label="X>Y", row=2, col=8),
    ButtonConfig(top_label="EEx", main_label="CHS", sub_label="X=Y", row=3, col=8),
    
    # COLUMN 9 (rightmost column, originally x=900)
    ButtonConfig(top_label="XOR", main_label="÷", sub_label="DBL÷", row=0, col=9),
    ButtonConfig(top_label="AND", main_label="×", sub_label="DBL×", row=1, col=9),
    ButtonConfig(top_label="NOT", main_label="-", sub_label="X>0", row=2, col=9),
    ButtonConfig(top_label="OR", main_label="+", sub_label="X=0", row=3, col=9),
]

# Calculate maximum rows and columns for grid layout.
max_rows: int = max(config.row + config.rowspan for config in BUTTONS_CONFIG)
max_cols: int = max(config.col for config in BUTTONS_CONFIG) + 1
