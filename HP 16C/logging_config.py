"""
logging_config.py

Logging configuration for the HP-16C emulator.
Logs to both file (in the logs directory) and console.
"""

import logging
import os
import sys

# Create logs directory if it doesn't exist
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Set up logger
logger = logging.getLogger("hp16c")
logger.setLevel(logging.DEBUG)  # Overall logger level

# File handler setup
file_handler = logging.FileHandler(os.path.join(LOG_DIR, "hp16c.log"), mode="a")
file_handler.setLevel(logging.DEBUG)  # Detailed logging to file

# Console handler for real-time feedback
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)  # Change to logging.INFO if less detail desired

# Common formatter for consistent log format
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Ensure the logs directory exists
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Attach handlers to the logger
logger = logging.getLogger("hp16c")
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
