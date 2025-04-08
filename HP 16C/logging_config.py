"""
logging_config.py
Configures logging for the HP-16C emulator with console and file output, including timestamps.
Author: GlobeyCode
License: MIT
Created: 3/23/2025
Last Modified: 4/06/2025
Dependencies: Python 3.6+, logging, os, datetime
"""

import logging
import os
from datetime import datetime
from logging import Logger, LogRecord


class UTF8StreamHandler(logging.StreamHandler):
    """
    A custom logging stream handler that outputs messages in UTF-8 encoding.
    """
    def emit(self, record: LogRecord) -> None:
        msg = self.format(record)
        if hasattr(self.stream, "buffer"):
            self.stream.buffer.write((msg + self.terminator).encode('utf-8'))
        else:
            # Fallback if stream has no buffer
            self.stream.write(msg + self.terminator)
        self.flush()


def setup_logging() -> Logger:
    """
    Configure logging for the HP-16C emulator with timestamped file output for debug and program logs.

    Returns:
        The debug logger instance.
    """
    current_time: str = datetime.now().strftime("%m-%d-%Y_%I-%M%p").lower()  # e.g., 03-24-2025_10-58pm
    log_dir: str = "logs"
    os.makedirs(log_dir, exist_ok=True)
    debug_log_file: str = f"{log_dir}/hp16c_debug_{current_time}.log"
    program_log_file: str = f"{log_dir}/program_{current_time}.log"

    # Debug logger setup (main log)
    debug_logger: Logger = logging.getLogger('debug')
    debug_logger.setLevel(logging.INFO)
    debug_formatter: logging.Formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
    debug_file_handler: logging.FileHandler = logging.FileHandler(debug_log_file, encoding='utf-8')
    debug_file_handler.setFormatter(debug_formatter)
    debug_console_handler: UTF8StreamHandler = UTF8StreamHandler()
    debug_console_handler.setFormatter(debug_formatter)
    debug_logger.handlers = [debug_file_handler, debug_console_handler]

    # Program logger setup (for program entries; no console output)
    program_logger: Logger = logging.getLogger('program')
    program_logger.setLevel(logging.INFO)
    program_formatter: logging.Formatter = logging.Formatter("%(asctime)s - %(message)s")
    program_file_handler: logging.FileHandler = logging.FileHandler(program_log_file, encoding='utf-8', mode='a')
    program_file_handler.setFormatter(program_formatter)
    program_logger.handlers = [program_file_handler]

    return debug_logger


# Export loggers for use in other modules.
logger: Logger = setup_logging()  # Debug logger
program_logger: Logger = logging.getLogger('program')
