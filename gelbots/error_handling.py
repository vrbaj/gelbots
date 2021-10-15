"""
This module cointains the ErrorLogger class that access the standardized
logger to all other modules.
"""

from time import strftime
from pathlib import Path
import logging.handlers

from PyQt5.QtWidgets import QMessageBox


def exception_handler(func):
    """
    General exception handler for whole function with unexpected exceptions.
    :param func: function that shall be executed
    :return: the results of executed function
    """

    # noinspection PyBroadException

    def inner_function(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except ValueError:
            error_message = f"{func.__name__} - unexpected ValueError exception occurred."
            logger = ErrorLogger(__name__)
            logger.logger.exception(error_message)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText("Unexpected error")
            msg.setWindowTitle("Error")
            msg.exec_()
        except Exception:
            error_message = f"{func.__name__} - unexpected exception occurred."
            logger = ErrorLogger()
            logger.logger.exception(error_message)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText("Unexpected error")
            msg.setWindowTitle("Error")
            msg.exec_()
            raise
    return inner_function


class ErrorLogger:
    """
    Class that implements logger that is utilizing gelbots.log file for all
    logged errors.
    """
    LOG_FILE_NAME = "gelbots.log"
    LOG_MAX_SIZE = 1000000  # 1 MB

    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)  # you can set this to be DEBUG, INFO, ERROR

        # Assign a file-handler to that instance
        self.file_handler = logging.FileHandler(self.LOG_FILE_NAME)
        self.file_handler.setLevel(logging.INFO)  # again, you can set this differently

        # Format your logs (optional)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(self.formatter)

        # Add the handler to your logging instance
        self.logger.addHandler(self.file_handler)

    @exception_handler
    def check_log(self):
        """
        Function to check the existence of log and rename it if it greater than
        LOG_MAX_SIZE.
        :return:
        """
        log = Path(self.LOG_FILE_NAME)
        if log.is_file():
            if log.stat().st_size > self.LOG_MAX_SIZE:
                new_log_name = "gelbots-" + strftime("%Y%m%d-%H%M%S") + ".log"
                handlers = self.logger.handlers[:]
                for handler in handlers:
                    handler.close()
                    self.logger.removeHandler(handler)
                log.rename(new_log_name)

    def log_exception(self, logger_text, msg_text):
        """
        Function that logs catched_exception
        """
        self.logger.exception(logger_text)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Error")
        msg.setText(msg_text)
        msg.setWindowTitle("Error")
        msg.exec_()
