import sys, socket, copy, os
import cv2_worker
from configparser import ConfigParser
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, QComboBox, QLineEdit, QPushButton
from PyQt5.QtCore import QSize, QRect, Qt
from PyQt5.QtGui import QIntValidator, QPixmap, QDoubleValidator
import cv2
import subprocess
import time, datetime
import numpy as np
import CameraWorker
import configparser


class ExampleWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        # variables
        self.image_to_display = []
        #TODO load default settings of all values that can be set via this GUI
        self.config = configparser.ConfigParser()
        try:
            self.config.read("config.ini")
            self.cam_width_value = self.config.get("camera", "width", fallback=1920)
            self.cam_height_value = self.config.get("camera", "height", fallback=1080)
            self.cam_fps_value = self.config.get("camera", "fps", fallback=50)

        except Exception as ex:
            print(ex)

        # set window properties
        centralWidget = QWidget(self)
        self.setMinimumSize(QSize(1600, 950))
        self.setWindowTitle("Gelbot aimbot")
        self.setCentralWidget(centralWidget)

        # Set validators
        self.onlyInt = QIntValidator()
        self.onlyDbl = QDoubleValidator()

        # Create combobox and add items.
        self.cameraComboBox = QComboBox(centralWidget)
        self.cameraComboBox.setGeometry(QRect(70, 45, 40, 20))
        self.cameraComboBox.setObjectName(("cameraComboBox"))
        self.cameraComboBox.currentIndexChanged.connect(self.camera_changed)

        self.refresh_camera_list()

        # Create camera combo box label
        self.cameraLabel = QLabel(centralWidget)
        self.cameraLabel.setGeometry(QRect(10, 40, 80, 31))
        self.cameraLabel.setText("Camera:")

        self.camera_worker = None

        # Create width label
        self.widthLabel = QLabel(centralWidget)
        self.widthLabel.setGeometry(QRect(130, 40, 80, 31))
        self.widthLabel.setText("Width:")

        # Create width input box
        self.widthInput = QLineEdit(centralWidget)
        self.widthInput.move(180, 41)
        self.widthInput.setFixedWidth(40)
        self.widthInput.setText(str(self.cam_width_value))
        self.widthInput.setValidator(self.onlyInt)
        self.widthInput.editingFinished.connect(self.width_edited)


        # Create height label
        self.heightLabel = QLabel(centralWidget)
        self.heightLabel.setGeometry(QRect(230, 40, 80, 31))
        self.heightLabel.setText("Height:")

        # Create height input box
        self.heightInput = QLineEdit(centralWidget)
        self.heightInput.move(280, 41)
        self.heightInput.setFixedWidth(40)
        self.heightInput.setText(str(self.cam_height_value))
        self.heightInput.setValidator(self.onlyInt)
        self.heightInput.editingFinished.connect(self.height_edited)

        # Create FPS label
        self.fpsLabel = QLabel(centralWidget)
        self.fpsLabel.setGeometry(QRect(330, 40, 80, 31))
        self.fpsLabel.setText("FPS:")

        # Create fps input box
        self.fpsInput = QLineEdit(centralWidget)
        self.fpsInput.move(380, 41)
        self.fpsInput.setFixedWidth(40)
        self.fpsInput.setText(str(self.cam_fps_value))
        self.fpsInput.setValidator(self.onlyInt)
        self.fpsInput.editingFinished.connect(self.fps_edited)

        # add pix
        self.imageDisplay = QLabel(self)
        self.imageDisplay.setGeometry(QRect(10, 80, 1200, 800))

        # run camera button
        self.runCameraButton = QPushButton('Run camera', self)
        self.runCameraButton.setToolTip('This is an example button')
        self.runCameraButton.move(600, 40)
        self.runCameraButton.clicked.connect(self.run_camera)




    def fps_edited(self):
        """Function to set FPS of camera"""
        if self.camera_worker is not None:
            try:
                fps_value = self.camera_worker.fps
                new_fps_value = int(self.fpsInput.text())
                #self.logger.setPlainText("FPS value changed from {} to {}".format(str(fps_value), str(new_fps_value)))
                self.camera_worker.fps = new_fps_value
                self.camera_worker.change_params_flag = True
                # TODO save config file
            except ValueError:
                # self.logger.setPlainText("Width value error")
                print("ValueError")





    def width_edited(self):
        """Function to set  width of camera image"""
        if self.camera_worker is not None:
            try:
                width_value = self.camera_worker.width
                new_width_value = int(self.widthInput.text())
                #self.logger.setPlainText("Frame width value changed from {} to {}".format(str(cam_width_value), str(new_width_value)))
                self.camera_worker.width = new_width_value
                self.camera_worker.change_params_flag = True
                # TODO save config file
            except ValueError:
                #self.logger.setPlainText("Width value error")
                print("ValueError")


    def height_edited(self):
        """Function to set  height of camera image"""
        if self.camera_worker is not None:
            try:
                height_value = self.camera_worker.height
                new_height_value = int(self.heightInput.text())
                #self.logger.setPlainText("Frame width value changed from {} to {}".format(str(cam_width_value), str(new_width_value)))
                self.camera_worker.height= new_height_value
                self.camera_worker.change_params_flag = True
                # TODO save config file
            except ValueError:
                #self.logger.setPlainText("Width value error")
                print("ValueError")

    def run_camera(self):
        if self.runCameraButton.text() == "Run camera":
            self.camera_worker = CameraWorker.CameraWorker(self.cameraComboBox.currentIndex())
            self.camera_worker.start()
            self.camera_worker.image_ready.connect(self.obtain_image)
            self.runCameraButton.setText("Stop camera")
        else:
            self.camera_worker.image_ready.disconnect(self.obtain_image)
            self.camera_worker.quit_flag = True
            self.runCameraButton.setText("Run camera")

    def obtain_image(self):
        self.camera_worker.mutex.lock()
        self.image_to_display = np.copy(self.camera_worker.raw_image)
        self.camera_worker.mutex.unlock()
        gray = cv2.cvtColor(self.image_to_display, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape[:2]
        image_for_pixmap = QtGui.QImage(gray, width, height, QtGui.QImage.Format_Grayscale8)
        self.imageDisplay.setPixmap(QPixmap(image_for_pixmap))

    def camera_changed(self):
        """
        This function emits a signal to CameraWorker thread, that the working camera was changed.
        :return: No return
        """
        print("emit signal to camera worker with index> ", self.cameraComboBox.currentIndex())

    def refresh_camera_list(self):
        """
        This function finds available cameras in Windows 10 OS and fill camera combo box with the indexes of available
        cameras
        :return: No return
        """
        arr = []
        for index in range(3):
            cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            if cap is None or not cap.isOpened():
                print("invalid cam at idx> ", index)
            else:
                arr.append(index)
            cap.release()
        for idx, item in enumerate(arr):
            self.cameraComboBox.addItem((str(idx)))


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    mainWin = ExampleWindow()
    mainWin.show()
    sys.exit(app.exec_())
