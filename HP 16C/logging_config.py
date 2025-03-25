# logging_config.py
# Sets up logging for the HP-16C emulator with console and file output, including timestamps.
# Author: GlobeyCode
# License: MIT
# Date: 3/23/2025
# Dependencies: Python 3.6+, standard libraries (logging, os, datetime)

import logging
import os
from datetime import datetime

def setup_logging():
    """Configure logging with timestamped file output for debug and program logs."""
    current_time = datetime.now().strftime("%m-%d-%Y_%I-%M%p").lower()  # e.g., 03-24-2025_10-58pm
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    debug_log_file = f"{log_dir}/hp16c_debug_{current_time}.log"
    program_log_file = f"{log_dir}/program_{current_time}.log"

    # Custom UTF-8 handler for console
    class UTF8StreamHandler(logging.StreamHandler):
        def emit(self, record):
            msg = self.format(record)
            self.stream.buffer.write((msg + self.terminator).encode('utf-8'))
            self.flush()

    # Debug logger setup (main log)
    debug_logger = logging.getLogger('debug')
    debug_logger.setLevel(logging.INFO)
    debug_formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
    debug_file_handler = logging.FileHandler(debug_log_file, encoding='utf-8')
    debug_file_handler.setFormatter(debug_formatter)
    debug_console_handler = UTF8StreamHandler()
    debug_console_handler.setFormatter(debug_formatter)
    debug_logger.handlers = [debug_file_handler, debug_console_handler]

    # Program logger setup (program entries log)
    program_logger = logging.getLogger('program')
    program_logger.setLevel(logging.INFO)
    program_formatter = logging.Formatter("%(asctime)s - %(message)s")  # Simpler format
    program_file_handler = logging.FileHandler(program_log_file, encoding='utf-8', mode='a')  # Append mode
    program_file_handler.setFormatter(program_formatter)
    program_logger.handlers = [program_file_handler]  # No console output

    return debug_logger

# Export loggers for use in other modules
logger = setup_logging()  # Debug logger
program_logger = logging.getLogger('program')  # Program logger