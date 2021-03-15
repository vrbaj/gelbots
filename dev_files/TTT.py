from PyQt5.QtCore import QThread, pyqtSignal, QObject, QMutex
import time



class TTT(QThread):
    image_ready = pyqtSignal()
    def __init__(self):
        super(TTT, self).__init__()
        self.quit_flag = False
        self.mutex = QMutex()


    def run(self):
        while True:
            if not self.quit_flag:
                self.doSomething()
                self.image_ready.emit()
                time.sleep(1)
            else:

                break


        self.quit()
        self.wait()

    def doSomething(self):
        self.mutex.lock()
        print('123')
        self.mutex.unlock()