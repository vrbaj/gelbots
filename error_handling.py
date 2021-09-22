import logging.handlers
import os


class ErrorLogger:
    def __init__(self):
        self.logger = logging.getLogger("gelbots_logger")
        self.logger.setLevel(logging.INFO)  # you can set this to be DEBUG, INFO, ERROR

        # Assign a file-handler to that instance
        self.fh = logging.FileHandler("gelbots.log")
        self.fh.setLevel(logging.INFO)  # again, you can set this differently

        # Format your logs (optional)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.fh.setFormatter(self.formatter)  # This will set the format to the file handler

        # Add the handler to your logging instance
        self.logger.addHandler(self.fh)
