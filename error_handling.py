"""
This module cointains the ErrorLogger class that access the standardized
logger to all other modules.
"""

import logging.handlers


class ErrorLogger:
    """
    Class that implements logger that is utilizing gelbots.log file for all
    logged errors.
    """
    def __init__(self):
        self.logger = logging.getLogger("gelbots_logger")
        self.logger.setLevel(logging.INFO)  # you can set this to be DEBUG, INFO, ERROR

        # Assign a file-handler to that instance
        self.file_handler = logging.FileHandler("gelbots.log")
        self.file_handler.setLevel(logging.INFO)  # again, you can set this differently

        # Format your logs (optional)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(self.formatter)

        # Add the handler to your logging instance
        self.logger.addHandler(self.file_handler)
