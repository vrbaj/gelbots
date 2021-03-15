from dev_files import TTT as TTT

from PyQt5 import QtWidgets
import sys


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.btn = QtWidgets.QPushButton('run process')
        self.btn.clicked.connect(self.create_process)
        self.setCentralWidget(self.btn)


    def create_process(self):
        if self.btn.text() == "run process":
            print("Started")
            self.btn.setText("stop process")
            self.t = TTT.TTT()
            self.t.start()
            self.t.image_ready.connect(self.obtain_image)

        else:
            self.t.quit_flag = True
            print("Stop sent")
            self.t.wait()
            print("Stopped")
            self.btn.setText("run process")


    def obtain_image(self):
        print("obtained image")

if __name__=="__main__":
    app=QtWidgets.QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())