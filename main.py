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
    CONFIG_FILE_NAME = "config.ini"

    def __init__(self):
        QMainWindow.__init__(self)
        # variables
        self.image_to_display = []
        # TODO load default settings of all values that can be set via this GUI
        self.config = configparser.RawConfigParser()
        try:
            self.config.read(self.CONFIG_FILE_NAME)
            self.cam_width_value = self.config.getint("camera", "width", fallback=1920)
            self.cam_height_value = self.config.getint("camera", "height", fallback=1080)
            self.cam_fps_value = self.config.getint("camera", "fps", fallback=50)
            self.cam_exposure_value = self.config.getint("camera", "exposure", fallback=10)
            self.cam_gain_value = float(str(self.config.get("camera", "gain", fallback=1)).replace(",", "."))
            self.cam_brightness_value = float(str(self.config.get("camera", "brightness",
                                                                  fallback=0.5)).replace(",", "."))
            self.laser_pulse_n = self.config.getint("laser", "pulses", fallback=1)
            self.laser_on_time = self.config.getint("laser", "on_time", fallback=1)
            self.laser_off_time = self.config.getint("laser", "off_time", fallback=1)
            self.laser_x_loc = self.config.getint("laser", "x_loc", fallback=0)
            self.laser_y_loc = self.config.getint("laser", "y_loc", fallback=0)
        except Exception as ex:
            print(ex)
        print(self.config.sections())
        # set window properties
        central_widget = QWidget(self)
        self.setMinimumSize(QSize(1800, 1030))
        self.setWindowTitle("Gelbot aimbot")
        self.setCentralWidget(central_widget)

        # Set validators
        self.onlyInt = QIntValidator()
        self.onlyDbl = QDoubleValidator()

        # CAMERA
        # Create camera combo box label
        self.cameraLabel = QLabel(central_widget)
        self.cameraLabel.setGeometry(QRect(10, 5, 80, 31))
        self.cameraLabel.setText("Camera:")

        # Create combobox and add items.
        self.cameraComboBox = QComboBox(central_widget)
        self.cameraComboBox.setGeometry(QRect(60, 10, 40, 20))
        self.cameraComboBox.setObjectName("cameraComboBox")
        self.cameraComboBox.currentIndexChanged.connect(self.camera_changed)

        self.refresh_camera_list()
        self.camera_worker = None

        # Create width label
        self.widthLabel = QLabel(central_widget)
        self.widthLabel.setGeometry(QRect(120, 5, 80, 31))
        self.widthLabel.setText("Width:")

        # Create width input box
        self.widthInput = QLineEdit(central_widget)
        self.widthInput.move(155, 10)
        self.widthInput.setFixedWidth(30)
        self.widthInput.setText(str(self.cam_width_value))
        self.widthInput.setValidator(self.onlyInt)
        self.widthInput.editingFinished.connect(self.width_edited)

        # Create height label
        self.heightLabel = QLabel(central_widget)
        self.heightLabel.setGeometry(QRect(200, 5, 80, 31))
        self.heightLabel.setText("Height:")

        # Create height input box
        self.heightInput = QLineEdit(central_widget)
        self.heightInput.move(235, 10)
        self.heightInput.setFixedWidth(30)
        self.heightInput.setText(str(self.cam_height_value))
        self.heightInput.setValidator(self.onlyInt)
        self.heightInput.editingFinished.connect(self.height_edited)

        # Create FPS label
        self.fpsLabel = QLabel(central_widget)
        self.fpsLabel.setGeometry(QRect(280, 5, 80, 31))
        self.fpsLabel.setText("FPS:")

        # Create fps input box
        self.fpsInput = QLineEdit(central_widget)
        self.fpsInput.move(305, 10)
        self.fpsInput.setFixedWidth(30)
        self.fpsInput.setText(str(self.cam_fps_value))
        self.fpsInput.setValidator(self.onlyInt)
        self.fpsInput.editingFinished.connect(self.fps_edited)

        # Create exposure label
        self.exposureLabel = QLabel(central_widget)
        self.exposureLabel.setGeometry(QRect(350, 5, 80, 31))
        self.exposureLabel.setText("Exposure:")

        # Create exposure input box
        self.exposureInput = QLineEdit(central_widget)
        self.exposureInput.move(400, 10)
        self.exposureInput.setFixedWidth(30)
        self.exposureInput.setText(str(self.cam_exposure_value))
        self.exposureInput.setValidator(self.onlyInt)
        self.exposureInput.editingFinished.connect(self.exposure_edited)

        # Create gain label
        self.gainLabel = QLabel(central_widget)
        self.gainLabel.setGeometry(QRect(450, 5, 80, 31))
        self.gainLabel.setText("Gain:")

        # Create gain input box
        self.gainInput = QLineEdit(central_widget)
        self.gainInput.move(480, 10)
        self.gainInput.setFixedWidth(40)
        self.gainInput.setText(str(self.cam_gain_value).replace(".", ","))
        self.gainInput.setValidator(self.onlyDbl)
        self.gainInput.editingFinished.connect(self.gain_edited)

        # Create brightness label
        self.brightnessLabel = QLabel(central_widget)
        self.brightnessLabel.setGeometry(QRect(540, 5, 80, 31))
        self.brightnessLabel.setText("Brightness:")

        # Create gain input box
        self.brightnessInput = QLineEdit(central_widget)
        self.brightnessInput.move(600, 10)
        self.brightnessInput.setFixedWidth(30)
        self.brightnessInput.setText(str(self.cam_brightness_value).replace(".", ","))
        self.brightnessInput.setValidator(self.onlyDbl)
        self.brightnessInput.editingFinished.connect(self.brightness_edited)

        # LASER
        # Create pulse number label
        self.pulseNumberLabel = QLabel(central_widget)
        self.pulseNumberLabel.setGeometry(QRect(10, 30, 80, 31))
        self.pulseNumberLabel.setText("Pulse n.:")

        # Create pulse number input box
        self.pulseNumberInput = QLineEdit(central_widget)
        self.pulseNumberInput.move(60, 35)
        self.pulseNumberInput.setFixedWidth(30)
        self.pulseNumberInput.setText(str(self.laser_pulse_n))
        self.pulseNumberInput.setValidator(self.onlyInt)
        self.pulseNumberInput.editingFinished.connect(self.pulse_number_edited)

        # Create laser on label
        self.laserOnLabel = QLabel(central_widget)
        self.laserOnLabel.setGeometry(QRect(120, 30, 80, 31))
        self.laserOnLabel.setText("On.:")

        # Create laser on input box
        self.laserOnInput = QLineEdit(central_widget)
        self.laserOnInput.move(155, 35)
        self.laserOnInput.setFixedWidth(30)
        self.laserOnInput.setText(str(self.laser_on_time))
        self.laserOnInput.setValidator(self.onlyInt)
        self.laserOnInput.editingFinished.connect(self.laser_on_edited)

        # Create laser off label
        self.laserOffLabel = QLabel(central_widget)
        self.laserOffLabel.setGeometry(QRect(200, 30, 80, 31))
        self.laserOffLabel.setText("Off.:")

        # Create laser off input box
        self.laserOffInput = QLineEdit(central_widget)
        self.laserOffInput.move(235, 35)
        self.laserOffInput.setFixedWidth(30)
        self.laserOffInput.setText(str(self.laser_off_time))
        self.laserOffInput.setValidator(self.onlyInt)
        self.laserOffInput.editingFinished.connect(self.laser_off_edited)

        # Create laser x loc label
        self.laserLocXLabel = QLabel(central_widget)
        self.laserLocXLabel.setGeometry(QRect(280, 30, 80, 31))
        self.laserLocXLabel.setText("X:")

        # Create laser x coordinate input box
        self.laserCoordXInput = QLineEdit(central_widget)
        self.laserCoordXInput.move(305, 35)
        self.laserCoordXInput.setFixedWidth(30)
        self.laserCoordXInput.setValidator(self.onlyInt)
        self.laserCoordXInput.setText(str(self.laser_x_loc))
        self.laserCoordXInput.editingFinished.connect(self.laser_x_loc_edited)

        # Create laser y loc label
        self.laserLocYLabel = QLabel(central_widget)
        self.laserLocYLabel.setGeometry(QRect(350, 30, 80, 31))
        self.laserLocYLabel.setText("Y:")

        # Create laser y coordinate input box
        self.laserCoordYInput = QLineEdit(central_widget)
        self.laserCoordYInput.move(370, 35)
        self.laserCoordYInput.setFixedWidth(30)
        self.laserCoordYInput.setValidator(self.onlyInt)
        self.laserCoordYInput.setText(str(self.laser_y_loc))
        self.laserCoordYInput.editingFinished.connect(self.laser_y_loc_edited)

        # add pix
        self.imageDisplay = QLabel(self)
        self.imageDisplay.setGeometry(QRect(10, 80, 1200, 800))

        # Create log
        self.message_text = QtWidgets.QPlainTextEdit(central_widget)
        self.message_text.setGeometry(10, 900, 1000, 40)
        self.message_text.setReadOnly(True)
        self.message_text.setPlainText("Initialized..")

        # run camera button
        self.runCameraButton = QPushButton('Run camera', self)
        self.runCameraButton.setToolTip('This is an example button')
        self.runCameraButton.move(650, 10)
        self.runCameraButton.setFixedHeight(22)
        self.runCameraButton.clicked.connect(self.run_camera)

        self.showMaximized()

    def laser_x_loc_edited(self):
        """Function to set the laser coord"""
        self.laser_x_loc = int(self.laserCoordXInput.text())
        self.message_text.setPlainText("laser x loc: {} ".format(str(self.laser_x_loc)))
        self.config.set("laser", "x_loc", self.laser_x_loc)
        self.update_config_file()

    def laser_y_loc_edited(self):
        """Function to set the laser coord"""
        self.laser_y_loc = int(self.laserCoordYInput.text())
        self.message_text.setPlainText("laser y loc: {} ".format(str(self.laser_y_loc)))
        self.config.set("laser", "y_loc", self.laser_y_loc)
        self.update_config_file()

    def laser_on_edited(self):
        """Function to set the time on for laser"""
        try:
            laser_on = self.laser_on_time
            self.laser_on_time = int(self.laserOnInput.text())
            self.message_text.setPlainText(
              "Laser on time value changed from {} to {}".format(str(laser_on), str(self.laser_on_time)))
            self.config.set("laser", "on_time", self.laser_on_time)
            self.update_config_file()
        except Exception as e:
            print(e)
            self.message_text.setPlainText("Laser on time error")

    def laser_off_edited(self):
        """Function to set the time on for laser"""
        try:
            laser_off = self.laser_off_time
            self.laser_off_time = int(self.laserOffInput.text())
            self.message_text.setPlainText(
              "Laser off time value changed from {} to {}".format(str(laser_off), str(self.laser_off_time)))
            self.config.set("laser", "off_time", self.laser_off_time)
            self.update_config_file()
        except Exception as e:
            print(e)
            self.message_text.setPlainText("Laser off time error")

    def pulse_number_edited(self):
        """Function to set the number of laser pulses"""
        try:
            pulse_number = self.laser_pulse_n
            self.laser_pulse_n = int(self.pulseNumberInput.text())
            self.message_text.setPlainText(
              "Laser pulse number value changed from {} to {}".format(str(pulse_number), str(self.laser_pulse_n)))
            self.config.set("laser", "pulses", self.laser_pulse_n)
            self.update_config_file()
        except Exception as e:
            print(e)
            self.message_text.setPlainText("Number of laser pulses error")

    def brightness_edited(self):
        """Function to set brightness of the camera"""
        if self.cam_brightness_value is not None:
            try:
                brightness_value = self.camera_worker.brightness
                new_brightness_value = float(self.brightnessInput.text().replace(",", "."))
                self.message_text.setPlainText(
                  "Brightness value changed from {} to {}".format(str(brightness_value), str(new_brightness_value)))
                self.camera_worker.brightness = new_brightness_value
                self.camera_worker.change_params_flag = True
                print("config set")
                self.config.set("camera", "brightness", str(new_brightness_value).replace(".", ","))
                print("config update")
                self.update_config_file()
            except Exception as ex:
                self.message_text.setPlainText("Brightness value error")
                print(ex)

    def gain_edited(self):
        """Function to set gain of the camera"""
        if self.camera_worker is not None:
            try:
                gain_value = self.camera_worker.gain
                new_gain_value = float(self.gainInput.text().replace(",", "."))
                self.message_text.setPlainText("Gain value changed from {} to {}".format(str(gain_value),
                                                                                         str(new_gain_value)))
                self.camera_worker.gain = new_gain_value
                self.camera_worker.change_params_flag = True
                self.config.set("camera", "gain", str(new_gain_value).replace(".", ","))
                self.update_config_file()
            except ValueError:
                self.message_text.setPlainText("Exposure value error")
                print("Gain Value Error")

    def exposure_edited(self):
        """Function to set Exposure of camera"""
        if self.camera_worker is not None:
            try:
                exposure_value = self.camera_worker.exposure
                new_exposure_value = int(self.exposureInput.text())
                self.message_text.setPlainText("Exposure value changed from {} to {}".format(str(exposure_value),
                                                                                             str(new_exposure_value)))
                self.camera_worker.exposure = new_exposure_value
                self.camera_worker.change_params_flag = True
                self.config.set("camera", "exposure", new_exposure_value)
                self.update_config_file()
            except ValueError:
                self.message_text.setPlainText("Exposure value error")
                print("exposure value error")

    def fps_edited(self):
        """Function to set FPS of camera"""
        if self.camera_worker is not None:
            try:
                fps_value = self.camera_worker.fps
                new_fps_value = int(self.fpsInput.text())
                self.message_text.setPlainText("FPS value changed from {} to {}".format(str(fps_value),
                                                                                        str(new_fps_value)))
                self.camera_worker.fps = new_fps_value
                self.camera_worker.change_params_flag = True
                self.config.set("camera", "fps", new_fps_value)
                self.update_config_file()
            except ValueError:
                self.message_text.setPlainText("Width value error")
                print("ValueError")

    def width_edited(self):
        """Function to set  width of camera image"""
        if self.camera_worker is not None:
            try:
                width_value = self.camera_worker.width
                new_width_value = int(self.widthInput.text())
                self.message_text.setPlainText("Frame width value changed from {} to {}".format(str(width_value),
                                                                                                str(new_width_value)))
                self.camera_worker.width = new_width_value
                self.camera_worker.change_params_flag = True
                self.config.set("camera", "width", new_width_value)
                self.update_config_file()
            except ValueError:
                self.message_text.setPlainText("Width value error")
                print("ValueError")

    def height_edited(self):
        """Function to set  height of camera image"""
        if self.camera_worker is not None:
            try:
                height_value = self.camera_worker.height
                new_height_value = int(self.heightInput.text())
                self.message_text.setPlainText("Frame height value changed from {} to {}".format(str(height_value),
                                                                                                 str(new_height_value)))
                self.camera_worker.height = new_height_value
                self.camera_worker.change_params_flag = True
                self.config.set("camera", "height", new_height_value)
                self.update_config_file()
            except ValueError:
                self.message_text.setPlainText("Width value error")
                print("ValueError")

    def run_camera(self):
        if self.runCameraButton.text() == "Run camera":
            self.cameraComboBox.setEnabled(False)
            self.camera_worker = CameraWorker.CameraWorker(self.cameraComboBox.currentIndex(), self.cam_width_value,
                                                           self.cam_brightness_value, self.cam_fps_value,
                                                           self.cam_exposure_value, self.cam_gain_value,
                                                           self.cam_brightness_value)
            # self.camera_worker = CameraWorker.CameraWorker(self.cameraComboBox.currentIndex())
            self.camera_worker.start()
            self.camera_worker.image_ready.connect(self.obtain_image)
            self.runCameraButton.setText("Stop camera")
        else:
            self.camera_worker.image_ready.disconnect(self.obtain_image)
            self.camera_worker.quit_flag = True
            self.cameraComboBox.setEnabled(True)
            self.runCameraButton.setText("Run camera")

    def obtain_image(self):
        """Function to get camera image from camera worker. The conversion to grayscale is done."""
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

    def update_config_file(self):
        try:
            print("updating config")
            with open(self.CONFIG_FILE_NAME, "w") as configfile:
                self.config.write(configfile)
        except Exception as ex:
            print("Exception in update_config_file: ", ex)

    def closeEvent(self, event):
        if self.camera_worker is not None:
            self.camera_worker.quit_flag = True
            time.sleep(0.5)
        sys.exit()

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    mainWin = ExampleWindow()
    mainWin.show()
    sys.exit(app.exec_())
