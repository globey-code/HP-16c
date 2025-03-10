"""
logging_config.py

Central logging configuration for the HP16C emulator.
"""

import logging
import sys

logger = logging.getLogger("hp16c")
logger.setLevel(logging.DEBUG)

# Log to file:
file_handler = logging.FileHandler("hp16c.log", mode="a")
file_handler.setLevel(logging.DEBUG)

# Log to console:
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
