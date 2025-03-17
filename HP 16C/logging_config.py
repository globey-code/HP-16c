"""
logging_config.py

Sets up logging for the HP-16C emulator with console and file output.
"""

import logging
import os
from datetime import datetime

def setup_logging():
    """Configure logging with timestamped file output and console output."""
    current_time = datetime.now().strftime("%m-%d-%Y_%I-%M%p").lower()  # e.g., 03-16-2025_10-58pm
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = f"{log_dir}/hp16c_debug_{current_time}.log"

    # Custom UTF-8 handler for console
    class UTF8StreamHandler(logging.StreamHandler):
        def emit(self, record):
            msg = self.format(record)
            self.stream.buffer.write((msg + self.terminator).encode('utf-8'))
            self.flush()

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),  # UTF-8 for file
            UTF8StreamHandler()  # UTF-8 for console
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()