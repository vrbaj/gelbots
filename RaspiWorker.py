from PyQt5.QtCore import QThread, QMutex, pyqtSignal
from datetime import datetime
import time
import socket


class RaspiWorker(QThread):
    signal_comm_err = pyqtSignal()
    RASPI_IP = "192.168.0.100"
    RASPI_PORT = 6543

    def __init__(self):
        super(RaspiWorker, self).__init__()
        self.requests_queue = []
        self.quit_flag = False  # flag to kill worker
        self.raspi_status = True
        self.k = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.k.settimeout(0.5)

    def run(self):
        try:
            self.k.connect((self.RASPI_IP, self.RASPI_PORT))
        except OSError as ex:
            self.quit_flag = True
            self.raspi_status = False
            self.signal_comm_err.emit()

        while True:
            if self.quit_flag:
                break
            else:
                if len(self.requests_queue):
                    request_to_process = self.requests_queue.pop(0)
                    print("req:", request_to_process)
                    try:
                        self.k.sendall(bytes(request_to_process + ";", "UTF-8"))
                    except (Exception, socket.error) as ex:
                        self.raspi_status = False
                        self.k.close()
                        self.quit_flag = True
                        self.signal_comm_err.emit()
                time.sleep(0.05)
                # TODO check queue and send to raspi. if red_button empty queue and send terminate all thread to raspi
                # TODO message to stop only the laser infinity blinking
        self.k.close()
        self.quit()
        self.wait()
