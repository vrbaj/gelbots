"""
Working QThread for communication with Raspberry Pi 4 via socket.
"""
import time
import socket

from PyQt5.QtCore import QThread, pyqtSignal
from error_handling import ErrorLogger


class RaspiWorker(QThread):
    """
    Class that represent the connection to Raspberry PI with constants
    RASPI_PI (IP address of RPI)
    RASPI_PORT (port number on which is RPI listening to receive commands)
    """
    signal_comm_err = pyqtSignal()
    RASPI_IP = "192.168.0.100"
    RASPI_PORT = 6543

    def __init__(self):
        # super(RaspiWorker, self).__init__()
        super().__init__()
        self.requests_queue = []
        self.quit_flag = False  # flag to kill worker
        self.raspi_status = True
        self.k = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.k.settimeout(0.5)
        self.logger = ErrorLogger()

    def run(self):
        """
        Function run is ensuring connection to Raspberry PI and consecutive loop
        which is sending commands to Raspberry Pi. It is running in single QThread.
        :return: None
        """
        try:
            self.k.connect((self.RASPI_IP, self.RASPI_PORT))
        except OSError:
            self.logger.logger.exception("Connection to raspi failed")
            self.quit_flag = True
            self.raspi_status = False
            self.signal_comm_err.emit()

        while not self.quit_flag:
            if self.requests_queue:
                request_to_process = self.requests_queue.pop(0)
                print("req:", request_to_process)
                try:
                    self.k.sendall(bytes(request_to_process + ";", "UTF-8"))
                except socket.error:
                    self.logger.logger.exception("Sending command to RPI failed")
                    self.raspi_status = False
                    self.k.close()
                    self.quit_flag = True
                    self.signal_comm_err.emit()
                except Exception:
                    self.logger.logger.exception("General error while sending command to RPI")
                    raise
            time.sleep(0.05)
        self.k.close()
        self.quit()
        self.wait()
