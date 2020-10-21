import sys, socket, copy, os
import cv2_worker
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, QComboBox,\
    QLineEdit, QPushButton, QFrame, QFileDialog, QCheckBox, QRubberBand
from PyQt5.QtCore import QSize, QRect, Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QIntValidator, QPixmap, QDoubleValidator, QFont
import cv2
import time, datetime
import numpy as np
import CameraWorker
import RaspiWorker
import DiskCore
import configparser
import keyboard


class sflSettingsWindow(QMainWindow):
    change_params = pyqtSignal(int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int)
    pulse_signal = pyqtSignal()
    flush_switch_signal = pyqtSignal()
    light_switch_signal = pyqtSignal()
    stamping_switch_signal = pyqtSignal(str)
    sfl_switch_signal = pyqtSignal()

    # key_press_signal = pyqtSignal(int)

    def __init__(self, flush_on, flush_off, light_on, light_off, pulse, radius,
                 stamping_dx, stamping_dy, stamping_x_delay, stamping_y_delay, stamping_light_on,
                 stamping_light_off, stamping_flush_on, stamping_flush_off, stamping_x_steps,
                 stamping_y_steps, stamping_batch_size):
        super(sflSettingsWindow, self).__init__()
        self.sfl_flush_on = flush_on
        self.sfl_flush_off = flush_off
        self.sfl_light_on = light_on
        self.sfl_light_off = light_off
        self.sfl_pulse = pulse
        self.sfl_radius = radius
        self.stamping_dx = stamping_dx
        self.stamping_dy = stamping_dy
        self.stamping_x_delay = stamping_x_delay
        self.stamping_y_delay = stamping_y_delay
        self.stamping_light_on = stamping_light_on
        self.stamping_light_off = stamping_light_off
        self.stamping_flush_on = stamping_flush_on
        self.stamping_flush_off = stamping_flush_off
        self.stamping_x_steps = stamping_x_steps
        self.stamping_y_steps = stamping_y_steps
        self.stamping_batch_size = stamping_batch_size

        # set window properties
        self.setMinimumSize(QSize(450, 500))
        self.setWindowTitle("SFL settings")

        self.onlyInt = QIntValidator()

        self.sflPulseLabel = QLabel(self)
        self.sflPulseLabel.setGeometry(QRect(10, 0, 80, 20))
        self.sflPulseLabel.setText("Pulse:")

        self.sflPulseInput = QLineEdit(self)
        self.sflPulseInput.move(60, 0)
        self.sflPulseInput.setFixedWidth(30)
        self.sflPulseInput.setValidator(self.onlyInt)
        self.sflPulseInput.setText(str(self.sfl_pulse))

        #
        self.sflLightOnLabel = QLabel(self)
        self.sflLightOnLabel.setGeometry(QRect(10, 30, 50, 31))
        self.sflLightOnLabel.setText("Light On:")

        self.sflLightOnInput = QLineEdit(self)
        self.sflLightOnInput.move(60, 30)
        self.sflLightOnInput.setFixedWidth(30)
        self.sflLightOnInput.setValidator(self.onlyInt)
        self.sflLightOnInput.setText(str(self.sfl_light_on))

        #
        self.sflRadiusLabel = QLabel(self)
        self.sflRadiusLabel.setGeometry(QRect(100, 30, 50, 30))
        self.sflRadiusLabel.setText("Radius:")

        self.sflRadiusInput = QLineEdit(self)
        self.sflRadiusInput.move(140, 30)
        self.sflRadiusInput.setFixedWidth(30)
        self.sflRadiusInput.setValidator(self.onlyInt)
        self.sflRadiusInput.setText(str(self.sfl_radius))

        self.sflLightOffLabel = QLabel(self)
        self.sflLightOffLabel.setGeometry(QRect(10, 60, 50, 31))
        self.sflLightOffLabel.setText("Light Off:")

        self.sflLightOffInput = QLineEdit(self)
        self.sflLightOffInput.move(60, 60)
        self.sflLightOffInput.setFixedWidth(30)
        self.sflLightOffInput.setValidator(self.onlyInt)
        self.sflLightOffInput.setText(str(self.sfl_light_off))


        self.sflFlushOnLabel = QLabel(self)
        self.sflFlushOnLabel.setGeometry(QRect(10, 90, 50, 31))
        self.sflFlushOnLabel.setText("Flush On:")

        self.sflFlushOnInput = QLineEdit(self)
        self.sflFlushOnInput.move(60, 90)
        self.sflFlushOnInput.setFixedWidth(30)
        self.sflFlushOnInput.setValidator(self.onlyInt)
        self.sflFlushOnInput.setText(str(self.sfl_flush_on))


        self.sflFlushOffLabel = QLabel(self)
        self.sflFlushOffLabel.setGeometry(QRect(10, 120, 50, 31))
        self.sflFlushOffLabel.setText("Flush Off:")


        self.sflFlushOffInput = QLineEdit(self)
        self.sflFlushOffInput.move(60, 120)
        self.sflFlushOffInput.setFixedWidth(30)
        self.sflFlushOffInput.setValidator(self.onlyInt)
        self.sflFlushOffInput.setText(str(self.sfl_flush_off))

        self.stampingDxLabel = QLabel(self)
        self.stampingDxLabel.setGeometry(QRect(200, 0, 100, 25))
        self.stampingDxLabel.setText("Stamping dx:")
        self.stampingDxInput = QLineEdit(self)
        self.stampingDxInput.setGeometry(QRect(300, 0, 50, 25))
        self.stampingDxInput.setValidator(self.onlyInt)
        self.stampingDxInput.setText(str(self.stamping_dx))

        self.stampingDyLabel = QLabel(self)
        self.stampingDyLabel.setGeometry(QRect(200, 25, 100, 25))
        self.stampingDyLabel.setText("Stamping dy:")
        self.stampingDyInput = QLineEdit(self)
        self.stampingDyInput.setGeometry(QRect(300, 25, 50, 25))
        self.stampingDyInput.setValidator(self.onlyInt)
        self.stampingDyInput.setText(str(self.stamping_dy))

        self.stampingX_DelayLabel = QLabel(self)
        self.stampingX_DelayLabel.setGeometry(QRect(200, 50, 100, 25))
        self.stampingX_DelayLabel.setText("Stamping X delay:")
        self.stampingX_DelayInput = QLineEdit(self)
        self.stampingX_DelayInput.setGeometry(QRect(300, 50, 50, 25))
        self.stampingX_DelayInput.setValidator(self.onlyInt)
        self.stampingX_DelayInput.setText(str(self.stamping_x_delay))

        self.stampingY_DelayLabel = QLabel(self)
        self.stampingY_DelayLabel.setGeometry(QRect(200, 75, 100, 25))
        self.stampingY_DelayLabel.setText("Stamping Y delay:")
        self.stampingY_DelayInput = QLineEdit(self)
        self.stampingY_DelayInput.setGeometry(QRect(300, 75, 50, 25))
        self.stampingY_DelayInput.setValidator(self.onlyInt)
        self.stampingY_DelayInput.setText(str(self.stamping_y_delay))

        self.stampingLightOnLabel = QLabel(self)
        self.stampingLightOnLabel.setGeometry(QRect(200, 100, 100, 25))
        self.stampingLightOnLabel.setText("Stamping light ON:")
        self.stampingLightOnInput = QLineEdit(self)
        self.stampingLightOnInput.setGeometry(QRect(300, 100, 50, 25))
        self.stampingLightOnInput.setValidator(self.onlyInt)
        self.stampingLightOnInput.setText(str(self.stamping_light_on))

        self.stampingLightOffLabel = QLabel(self)
        self.stampingLightOffLabel.setGeometry(QRect(200, 125, 100, 25))
        self.stampingLightOffLabel.setText("Stamping light OFF:")
        self.stampingLightOffInput = QLineEdit(self)
        self.stampingLightOffInput.setGeometry(QRect(300, 125, 50, 25))
        self.stampingLightOffInput.setValidator(self.onlyInt)
        self.stampingLightOffInput.setText(str(self.stamping_light_off))

        self.stampingFlushOnLabel = QLabel(self)
        self.stampingFlushOnLabel.setGeometry(QRect(200, 150, 100, 25))
        self.stampingFlushOnLabel.setText("Stamping flush ON:")
        self.stampingFlushOnInput = QLineEdit(self)
        self.stampingFlushOnInput.setGeometry(QRect(300, 150, 50, 25))
        self.stampingFlushOnInput.setValidator(self.onlyInt)
        self.stampingFlushOnInput.setText(str(self.stamping_flush_on))

        self.stampingFlushOffLabel = QLabel(self)
        self.stampingFlushOffLabel.setGeometry(QRect(200, 175, 100, 25))
        self.stampingFlushOffLabel.setText("Stamping flush OFF:")
        self.stampingFlushOffInput = QLineEdit(self)
        self.stampingFlushOffInput.setGeometry(QRect(300, 175, 50, 25))
        self.stampingFlushOffInput.setValidator(self.onlyInt)
        self.stampingFlushOffInput.setText(str(self.stamping_flush_off))

        self.stampingXStepsLabel = QLabel(self)
        self.stampingXStepsLabel.setGeometry(QRect(200, 200, 100, 25))
        self.stampingXStepsLabel.setText("Stamping X steps:")
        self.stampingXStepsInput = QLineEdit(self)
        self.stampingXStepsInput.setGeometry(QRect(300, 200, 50, 25))
        self.stampingXStepsInput.setValidator(self.onlyInt)
        self.stampingXStepsInput.setText(str(self.stamping_x_steps))

        self.stampingYStepsLabel = QLabel(self)
        self.stampingYStepsLabel.setGeometry(QRect(200, 225, 100, 25))
        self.stampingYStepsLabel.setText("Stamping Y steps:")
        self.stampingYStepsInput = QLineEdit(self)
        self.stampingYStepsInput.setGeometry(QRect(300, 225, 50, 25))
        self.stampingYStepsInput.setValidator(self.onlyInt)
        self.stampingYStepsInput.setText(str(self.stamping_y_steps))

        self.stampingBatchSizeLabel = QLabel(self)
        self.stampingBatchSizeLabel.setGeometry(QRect(200, 250, 100, 25))
        self.stampingBatchSizeLabel.setText("Stamping Batch size:")
        self.stampingBatchSizeInput = QLineEdit(self)
        self.stampingBatchSizeInput.setGeometry(QRect(300, 250, 50, 25))
        self.stampingBatchSizeInput.setValidator(self.onlyInt)
        self.stampingBatchSizeInput.setText(str(self.stamping_batch_size))

        # Apply button
        self.stampingButton = QPushButton(self)
        self.stampingButton.setGeometry(QRect(200, 300, 100, 30))
        self.stampingButton.setToolTip("Click to start stamping")
        self.stampingButton.setText("Stamping ON")
        self.stampingButton.clicked.connect(self.switch_stamping)

        # sfl swithc button
        self.sflButton = QPushButton('SFL ON', self)
        self.sflButton.setToolTip('SFL ON')
        self.sflButton.move(10, 160)
        self.sflButton.setFixedHeight(40)
        self.sflButton.clicked.connect(self.sfl_switch)

        # sfl light switch button
        self.sflLightButton = QPushButton('Light ON', self)
        self.sflLightButton.setToolTip('Light ON')
        self.sflLightButton.move(10, 210)
        self.sflLightButton.setFixedHeight(40)
        self.sflLightButton.clicked.connect(self.light_switch)

        # sfl flush switch button
        self.sflFlushButton = QPushButton('Flush ON', self)
        self.sflFlushButton.setToolTip('Flush ON')
        self.sflFlushButton.move(10, 260)
        self.sflFlushButton.setFixedHeight(40)
        self.sflFlushButton.clicked.connect(self.flush_switch)

        # sfl pulse button
        self.sflPulseButton = QPushButton('Pulse', self)
        self.sflPulseButton.setToolTip('Pulse')
        self.sflPulseButton.move(10, 310)
        self.sflPulseButton.setFixedHeight(40)
        self.sflPulseButton.clicked.connect(self.pulse)

        # Apply button
        self.validateButton = QPushButton(self)
        self.validateButton.setGeometry(QRect(10, 360, 60, 30))
        self.validateButton.setToolTip("Click to save settings")
        self.validateButton.setText("Apply")
        self.validateButton.clicked.connect(self.validate_settings)

        # key press event
        # self.keyPressEvent = self.keyPressEvent


        # def keyPressEvent(self, e):
        #     print(e.key())
        #     self.key_press_signal.emit(e.key())


    def validate_settings(self):
        self.sfl_pulse = int(self.sflPulseInput.text())
        self.sfl_flush_on = int(self.sflFlushOnInput.text())
        self.sfl_flush_off = int(self.sflFlushOffInput.text())
        self.sfl_light_on = int(self.sflLightOnInput.text())
        self.sfl_light_off = int(self.sflLightOffInput.text())
        self.sfl_radius = int(self.sflRadiusInput.text())
        self.stamping_dx = int(self.stampingDxInput.text())
        self.stamping_dy = int(self.stampingDyInput.text())
        self.stamping_x_delay = int(self.stampingX_DelayInput.text())
        self.stamping_y_delay = int(self.stampingY_DelayInput.text())
        self.stamping_light_on = int(self.stampingLightOnInput.text())
        self.stamping_light_off = int(self.stampingLightOffInput.text())
        self.stamping_flush_on = int(self.stampingFlushOnInput.text())
        self.stamping_flush_off = int(self.stampingFlushOffInput.text())
        self.stamping_x_steps = int(self.stampingXStepsInput.text())
        self.stamping_y_steps = int(self.stampingYStepsInput.text())
        self.stamping_batch_size = int(self.stampingBatchSizeInput.text())
        self.change_params.emit(self.sfl_light_on, self.sfl_light_off, self.sfl_flush_on, self.sfl_flush_off,
                                self.sfl_pulse, self.sfl_radius, self.stamping_dx, self.stamping_dy, self.stamping_x_delay,
                                                     self.stamping_y_delay, self.stamping_light_on,
                                                     self.stamping_light_off, self.stamping_flush_on,
                                                     self.stamping_flush_off, self.stamping_x_steps,
                                                     self.stamping_y_steps, self.stamping_batch_size)

    def pulse(self):
        self.pulse_signal.emit()

    def flush_switch(self):
        self.flush_switch_signal.emit()

    def light_switch(self):
        self.light_switch_signal.emit()

    def sfl_switch(self):
        self.sfl_switch_signal.emit()

    def switch_stamping(self):
        if self.stampingButton.text() == "Stamping ON":
            self.stamping_switch_signal.emit("start")
            self.stampingButton.setText("Stamping OFF")
        else:
            self.stamping_switch_signal.emit("end")
            self.stampingButton.setText("Stamping ON")


class LaserSettingsWindow(QMainWindow):
    change_params = pyqtSignal(int, int, int, int, int, int)
    laser_control_signal = pyqtSignal(str)

    def __init__(self, pulse_number, on_time, off_time, x, y, offset):
        super(LaserSettingsWindow, self).__init__()
        # set variables
        # self.save_interval = interval
        # self.save_namespace = namespace
        # self.save_path = path
        self.offset = offset
        self.laser_pulse_n = pulse_number
        self.laser_on_time = on_time
        self.laser_off_time = off_time
        self.laser_x_loc = x
        self.laser_y_loc = y
        # set window properties
        self.setMinimumSize(QSize(250, 300))
        self.setWindowTitle("Laser settings")

        self.onlyInt = QIntValidator()

        # LASER
        # Create pulse number label
        self.pulseNumberLabel = QLabel(self)
        self.pulseNumberLabel.setGeometry(QRect(10, 0, 80, 20))
        self.pulseNumberLabel.setText("Pulse n.:")

        # Create pulse number input box
        self.pulseNumberInput = QLineEdit(self)
        self.pulseNumberInput.setGeometry(QRect(60, 0, 40, 20))
        self.pulseNumberInput.setText(str(self.laser_pulse_n))
        self.pulseNumberInput.setValidator(self.onlyInt)


        # Create laser on label
        self.laserOnLabel = QLabel(self)
        self.laserOnLabel.setGeometry(QRect(10, 30, 80, 20))
        self.laserOnLabel.setText("On.:")

        # Create laser on input box
        self.laserOnInput = QLineEdit(self)
        self.laserOnInput.setGeometry(QRect(60, 30, 40, 20))
        self.laserOnInput.setText(str(self.laser_on_time))
        self.laserOnInput.setValidator(self.onlyInt)


        # Create laser off label
        self.laserOffLabel = QLabel(self)
        self.laserOffLabel.setGeometry(QRect(10, 60, 80, 20))
        self.laserOffLabel.setText("Off.:")

        # Create laser off input box
        self.laserOffInput = QLineEdit(self)
        self.laserOffInput.setGeometry(QRect(60, 60, 40, 20))
        self.laserOffInput.setText(str(self.laser_off_time))
        self.laserOffInput.setValidator(self.onlyInt)

        # Create laser x loc label
        self.laserLocXLabel = QLabel(self)
        self.laserLocXLabel.setGeometry(QRect(10, 90, 80, 20))
        self.laserLocXLabel.setText("X:")

        # Create laser x coordinate input box
        self.laserCoordXInput = QLineEdit(self)
        self.laserCoordXInput.setGeometry(QRect(60, 90, 40, 20))
        self.laserCoordXInput.setValidator(self.onlyInt)
        self.laserCoordXInput.setText(str(self.laser_x_loc))

        # Create laser y loc label
        self.laserLocYLabel = QLabel(self)
        self.laserLocYLabel.setGeometry(QRect(10, 120, 80, 20))
        self.laserLocYLabel.setText("Y:")

        # Create laser y coordinate input box
        self.laserCoordYInput = QLineEdit(self)
        self.laserCoordYInput.setGeometry(QRect(60, 120, 40, 20))
        self.laserCoordYInput.setValidator(self.onlyInt)
        self.laserCoordYInput.setText(str(self.laser_y_loc))

        # Create laser offset label
        self.laserOffsetLabel = QLabel(self)
        self.laserOffsetLabel.setGeometry(QRect(10, 150, 80, 20))
        self.laserOffsetLabel.setText("Offset:")

        # Create laser y coordinate input box
        self.laserOffsetInput = QLineEdit(self)
        self.laserOffsetInput.setGeometry(QRect(60, 150, 40, 20))
        self.laserOffsetInput.setValidator(self.onlyInt)
        self.laserOffsetInput.setText(str(self.offset))

        # laser blink button
        self.blinkLaserButton = QPushButton("Blink On", self)
        self.blinkLaserButton.setToolTip("Unlimited laser blink")
        self.blinkLaserButton.setGeometry(QRect(10, 180, 230, 40))
        self.blinkLaserButton.setFixedHeight(22)
        self.blinkLaserButton.clicked.connect(self.blink_laser)

        # laser switch button
        self.switchLaserButton = QPushButton("Laser ON", self)
        self.switchLaserButton.setToolTip("Laser switch")
        self.switchLaserButton.setGeometry(QRect(10, 210, 230, 40))
        self.switchLaserButton.setFixedHeight(22)
        self.switchLaserButton.clicked.connect(self.switch_laser)

        # Apply button
        self.validateButton = QPushButton(self)
        self.validateButton.setGeometry(QRect(10, 240, 230, 40))
        self.validateButton.setToolTip("Click to save settings")
        self.validateButton.setFont(QFont('Times', 20))
        self.validateButton.setText("Apply")
        self.validateButton.clicked.connect(self.validate_settings)

    def validate_settings(self):
        self.laser_pulse_n = int(self.pulseNumberInput.text())
        self.laser_on_time = int(self.laserOnInput.text())
        self.laser_off_time = int(self.laserOffInput.text())
        self.laser_x_loc = int(self.laserCoordXInput.text())
        self.laser_y_loc = int(self.laserCoordYInput.text())
        self.offset = int(self.laserOffsetInput.text())
        self.change_params.emit(self.laser_pulse_n, self.laser_on_time, self.laser_off_time, self.laser_x_loc,
                                self.laser_y_loc, self.offset)


    def blink_laser(self):
        if self.blinkLaserButton.text() == "Blink On":
            time_on = int(self.laser_on_time)
            time_off = int(self.laser_off_time)
            self.laser_control_signal.emit("k" + "," + str(time_on) + "," + str(time_off))
            self.blinkLaserButton.setText("Blink Off")
        else:
            self.blinkLaserButton.setText("Blink On")
            self.laser_control_signal.emit("t")

    def switch_laser(self):
        if self.switchLaserButton.text() == "Laser ON":
            self.laser_control_signal.emit("s")
            self.switchLaserButton.setText("Laser OFF")
        else:
            self.laser_control_signal.emit("l")
            self.switchLaserButton.setText("Laser ON")


class VideoSettingsWindow(QMainWindow):
    closed = pyqtSignal(int, str, str)

    def __init__(self, interval, namespace, path):
        super(VideoSettingsWindow, self).__init__()
        # set variables
        self.save_interval = interval
        self.save_namespace = namespace
        self.save_path = path

        # check box to save ROI
        self.roiCheckbox = QCheckBox(self)
        self.roiCheckbox.setText("save roi")
        self.roiCheckbox.setToolTip("Click to save only ROI")
        self.roiCheckbox.setGeometry(QRect(200, 30, 100, 25))
        self.roiCheckbox.setLayoutDirection(Qt.RightToLeft)

        # set window properties
        self.setMinimumSize(QSize(800, 120))
        self.setWindowTitle("Video settings")
        self.some_bullshit = "wtf"
        self.onlyInt = QIntValidator()

        # Interval label
        self.intervalLabel = QLabel(self)
        self.intervalLabel.setGeometry(QRect(10, 5, 80, 31))
        self.intervalLabel.setText("Saving interval:")

        # Create width input box
        self.intervalInput = QLineEdit(self)
        self.intervalInput.setGeometry(QRect(90, 10, 30, 20))
        self.intervalInput.setText(str(self.save_interval))
        self.intervalInput.setValidator(self.onlyInt)

        # Interval seconds label
        self.secondsLabel = QLabel(self)
        self.secondsLabel.setGeometry(QRect(125, 5, 80, 31))
        self.secondsLabel.setText("[s]")

        # Namespace label
        self.namespaceLabel = QLabel(self)
        self.namespaceLabel.setGeometry(QRect(30, 35, 80, 31))
        self.namespaceLabel.setText("Files name:")

        # Create namespace input box
        self.namespaceInput = QLineEdit(self)
        self.namespaceInput.setGeometry(QRect(90, 40, 85, 20))
        self.namespaceInput.setText(self.save_namespace)

        # Path label
        self.pathLabel = QLabel(self)
        self.pathLabel.setGeometry(QRect(50, 65, 80, 31))
        self.pathLabel.setText("Path:")

        # Path button
        self.pathButton = QPushButton(self)
        self.pathButton.setGeometry(QRect(90, 70, 30, 20))
        self.pathButton.setToolTip("Click to choose directory")
        self.pathButton.setText("...")
        self.pathButton.clicked.connect(self.get_video_path)

        # Path actual label
        self.pathActualLabel = QLabel(self)
        self.pathActualLabel.setGeometry(QRect(130, 65, 650, 31))
        self.pathActualLabel.setText(self.save_path)

        # Apply button
        self.validateButton = QPushButton(self)
        self.validateButton.setGeometry(QRect(739, 90, 60, 30))
        self.validateButton.setToolTip("Click to save settings")
        self.validateButton.setText("Apply")
        self.validateButton.clicked.connect(self.validate_settings)

        # set ROI button
        self.roiButton = QPushButton(self)
        self.roiButton.setGeometry(QRect(739, 40, 60, 30))
        self.roiButton.setToolTip("Click to set ROI for saving video")
        self.roiButton.setText("ROI")
        self.roiButton.clicked.connect(self.roi_pushed)
        self.roi_enabled = False

    def roi_pushed(self):
        self.roi_enabled = True
        print(self.roi_enabled)

    def get_video_path(self):
        file = str(QFileDialog.getExistingDirectory(self, "Select directory"))
        self.save_path = file
        self.pathActualLabel.setText(file)

    def validate_settings(self):
        self.save_interval = int(self.intervalInput.text())
        self.save_namespace = str(self.namespaceInput.text())
        self.save_path = str(self.save_path)
        self.closed.emit(self.save_interval, self.save_namespace, self.save_path)


class ExampleWindow(QMainWindow):
    CONFIG_FILE_NAME = "config.ini"
    PIXMAP_HEIGHT = 720
    PIXMAP_WIDTH = 1280

    def __init__(self):
        QMainWindow.__init__(self)
        self.hook = keyboard.on_press(self.keyboardEventReceived)
        self.draw_roi = False
        # variables
        self.image_to_display = []
        self.gray_image = []
        self.move_laser_enabled = False
        self.set_goal_enabled = False
        self.set_disk_enabled = False
        self.set_sfl_enabled = False
        self.draw_marks_enabled = False
        self.set_laser_enabled = False
        self.automode_enabled = False
        self.checker_memory = False
        # TODO load default settings of all values that can be set via this GUI
        try:
            self.config = configparser.RawConfigParser()
        except Exception as ex:
            print(ex)

        try:
            self.config.read(self.CONFIG_FILE_NAME)
            self.cam_width_value = self.config.getint("camera", "width", fallback=1920)
            self.cam_height_value = self.config.getint("camera", "height", fallback=1080)
            self.cam_fps_value = self.config.getint("camera", "fps", fallback=50)
            self.cam_exposure_value = self.config.getint("camera", "exposure", fallback=10)
            self.cam_gain_value = float(str(self.config.get("camera", "gain", fallback=1)).replace(",", "."))
            self.cam_brightness_value = float(str(self.config.get("camera", "brightness",
                                                                  fallback=0.5)).replace(",", "."))
            self.mag_value = self.config.getint("camera", "mag", fallback=4)
            self.laser_pulse_n = self.config.getint("laser", "pulses", fallback=1)
            self.laser_on_time = self.config.getint("laser", "on_time", fallback=1)
            self.laser_off_time = self.config.getint("laser", "off_time", fallback=1)
            self.laser_x_loc = self.config.getint("laser", "x_loc", fallback=0)
            self.laser_y_loc = self.config.getint("laser", "y_loc", fallback=0)
            self.offset = self.config.getint("laser", "offset", fallback=10)
            self.disk_x_loc = self.config.getint("disk", "x_loc", fallback=0)
            self.disk_y_loc = self.config.getint("disk", "y_loc", fallback=0)
            self.goal_x_loc = self.config.getint("goal", "x_loc", fallback=0)
            self.goal_y_loc = self.config.getint("goal", "y_loc", fallback=0)
            self.sfl_x_loc = self.config.getint("sfl", "x_loc", fallback=0)
            self.sfl_y_loc = self.config.getint("sfl", "y_loc", fallback=0)
            self.sfl_radius = self.config.getint("sfl", "radius", fallback=0)
            self.steppers_x = self.config.getint("steppers", "x", fallback=10)
            self.steppers_y = self.config.getint("steppers", "y", fallback=10)
            self.save_interval = self.config.getint("video", "interval", fallback=1)
            self.save_namespace = self.config.get("video", "namespace", fallback="video")
            self.save_path = self.config.get("video", "path", fallback="c:/")
            self.sfl_flush_on = self.config.getint("sfl", "flush_on", fallback=50)
            self.sfl_flush_off = self.config.getint("sfl", "flush_off", fallback=500)
            self.sfl_light_on = self.config.getint("sfl", "light_on", fallback=50)
            self.sfl_light_off = self.config.getint("sfl", "light_off", fallback=500)
            self.sfl_pulse = self.config.getint("sfl", "pulse", fallback=3000)
            # stamping settings
            self.stamping_dx = self.config.getint("stamping", "dx", fallback=1)
            self.stamping_dy = self.config.getint("stamping", "dy", fallback=1)
            self.stamping_x_delay = self.config.getint("stamping", "x_delay", fallback=100)
            self.stamping_y_delay = self.config.getint("stamping", "y_delay", fallback=100)
            self.stamping_light_on = self.config.getint("stamping", "light_on", fallback=100)
            self.stamping_light_off = self.config.getint("stamping", "light_off", fallback=100)
            self.stamping_flush_on = self.config.getint("stamping", "flush_on", fallback=100)
            self.stamping_flush_off = self.config.getint("stamping", "flush_off", fallback=100)
            self.stamping_x_steps = self.config.getint("stamping", "x_steps", fallback=100)
            self.stamping_y_steps = self.config.getint("stamping", "y_steps", fallback=100)
            self.stamping_batch_size = self.config.getint("stamping", "batch_size", fallback=100)
            print(self.sfl_radius)
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

        # Create disk x loc label
        self.diskLocXLabel = QLabel(central_widget)
        self.diskLocXLabel.setGeometry(QRect(410, 30, 80, 31))
        self.diskLocXLabel.setText("Disk X:")

        # Create disk x coordinate input box
        self.diskCoordXInput = QLineEdit(central_widget)
        self.diskCoordXInput.move(445, 35)
        self.diskCoordXInput.setFixedWidth(30)
        self.diskCoordXInput.setValidator(self.onlyInt)
        self.diskCoordXInput.setText(str(self.disk_x_loc))
        self.diskCoordXInput.editingFinished.connect(self.disk_x_loc_edited)

        # Create disk y loc label
        self.diskLocYLabel = QLabel(central_widget)
        self.diskLocYLabel.setGeometry(QRect(480, 30, 80, 31))
        self.diskLocYLabel.setText("Y:")

        # Create disk y coordinate input box
        self.diskCoordYInput = QLineEdit(central_widget)
        self.diskCoordYInput.move(510, 35)
        self.diskCoordYInput.setFixedWidth(30)
        self.diskCoordYInput.setValidator(self.onlyInt)
        self.diskCoordYInput.setText(str(self.disk_y_loc))
        self.diskCoordYInput.editingFinished.connect(self.disk_y_loc_edited)

        # Create goal x loc label
        self.goalLocXLabel = QLabel(central_widget)
        self.goalLocXLabel.setGeometry(QRect(550, 30, 80, 31))
        self.goalLocXLabel.setText("Goal X:")

        # Create goal x coordinate input box
        self.goalCoordXInput = QLineEdit(central_widget)
        self.goalCoordXInput.move(585, 35)
        self.goalCoordXInput.setFixedWidth(30)
        self.goalCoordXInput.setValidator(self.onlyInt)
        self.goalCoordXInput.setText(str(self.goal_x_loc))
        self.goalCoordXInput.editingFinished.connect(self.goal_x_loc_edited)

        # Create goal y loc label
        self.goalLocYLabel = QLabel(central_widget)
        self.goalLocYLabel.setGeometry(QRect(625, 30, 80, 31))
        self.goalLocYLabel.setText("Y:")

        # Create goal y coordinate input box
        self.goalCoordYInput = QLineEdit(central_widget)
        self.goalCoordYInput.move(640, 35)
        self.goalCoordYInput.setFixedWidth(30)
        self.goalCoordYInput.setValidator(self.onlyInt)
        self.goalCoordYInput.setText(str(self.goal_y_loc))
        self.goalCoordYInput.editingFinished.connect(self.goal_y_loc_edited)

        # add pix
        self.imageDisplay = QLabel(self)
        self.imageDisplay.setGeometry(QRect(10, 60, self.PIXMAP_WIDTH, self.PIXMAP_HEIGHT))
        self.imageDisplay.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.imageDisplay.mousePressEvent = self.click_to_get_coords
        self.imageDisplay.mouseMoveEvent = self.mouseMoveEvent
        self.imageDisplay.mouseReleaseEvent = self.mouseReleaseEvent

        # Create log
        self.message_text = QtWidgets.QPlainTextEdit(central_widget)
        self.message_text.setGeometry(10, 1050, 1280, 30)
        self.message_text.setReadOnly(True)
        self.message_text.setPlainText("Initialized..")

        # run camera button
        self.runCameraButton = QPushButton('Run camera', self)
        self.runCameraButton.setToolTip('This is an example button')
        self.runCameraButton.move(650, 10)
        self.runCameraButton.setFixedHeight(22)
        self.runCameraButton.clicked.connect(self.run_camera)



        # status label of raspi
        self.raspiStatus = QLabel(central_widget)
        self.raspiStatus.setGeometry(QRect(1500, 5, 80, 30))
        self.raspiStatus.setText("Raspberri")
        self.raspiStatus.setAutoFillBackground(True)
        self.raspiStatus.setStyleSheet("background-color:green;")
        self.raspiStatus.setAlignment(Qt.AlignCenter)
        self.raspiStatus.setFrameShape(QFrame.Panel)
        self.raspiStatus.setFrameShadow(QFrame.Sunken)
        self.raspiStatus.setLineWidth(2)
        self.raspiStatus.mousePressEvent = self.init_raspi

        # red button stop
        self.redButton = QPushButton("Red button", self)
        self.redButton.setToolTip("Click to stop all raspberry processes")
        self.redButton.move(1000, 30)
        self.redButton.setFixedHeight(22)
        self.redButton.clicked.connect(self.red_button)

        # steppers x param label
        self.steppersParamXLabel = QLabel(central_widget)
        self.steppersParamXLabel.setGeometry(QRect(1600, 5, 80, 31))
        self.steppersParamXLabel.setText("Manual steps X:")

        # steppers x param input
        self.steppersXInput = QLineEdit(central_widget)
        self.steppersXInput.move(1680, 10)
        self.steppersXInput.setFixedWidth(30)
        self.steppersXInput.setValidator(self.onlyInt)
        self.steppersXInput.setText(str(self.steppers_x))
        self.steppersXInput.editingFinished.connect(self.steppers_x_edited)

        # steppers y param label
        self.steppersParamYLabel = QLabel(central_widget)
        self.steppersParamYLabel.setGeometry(QRect(1600, 35, 80, 31))
        self.steppersParamYLabel.setText("Manual steps Y:")

        # steppers Y param input
        self.steppersYInput = QLineEdit(central_widget)
        self.steppersYInput.move(1680, 40)
        self.steppersYInput.setFixedWidth(30)
        self.steppersYInput.setValidator(self.onlyInt)
        self.steppersYInput.setText(str(self.steppers_y))
        self.steppersYInput.editingFinished.connect(self.steppers_y_edited)

        # save video settings
        self.saveVideoButton = QPushButton("Video settings", self)
        self.saveVideoButton.setToolTip("Click to set video settings")
        self.saveVideoButton.move(1300, 30)
        self.saveVideoButton.setFixedHeight(22)
        self.saveVideoButton.clicked.connect(self.save_video_settings)

        # laser settings window
        self.laserSettingsButton = QPushButton("Laser settings", self)
        self.laserSettingsButton.setToolTip("Click to set laser settings")
        self.laserSettingsButton.move(1750, 150)
        self.laserSettingsButton.setFixedHeight(22)
        self.laserSettingsButton.clicked.connect(self.show_laser_settings)

        # sfl settings window
        self.sflSettingsButton = QPushButton("SFL settings", self)
        self.sflSettingsButton.setToolTip("Click to set sfl settings")
        self.sflSettingsButton.move(1750, 200)
        self.sflSettingsButton.setFixedHeight(22)
        self.sflSettingsButton.clicked.connect(self.show_sfl_settings)

        # check box to move laser to desired position
        self.moveLaserCheckbox = QCheckBox(self)
        self.moveLaserCheckbox.setText("Move laser")
        self.moveLaserCheckbox.setToolTip("Click to image to move laser to desired position")
        self.moveLaserCheckbox.setGeometry(QRect(850, 30, 100, 25))
        self.moveLaserCheckbox.setLayoutDirection(Qt.RightToLeft)
        self.moveLaserCheckbox.stateChanged.connect(self.laser_checkbox_click)

        # check box to select disk
        self.setDiskCheckbox = QCheckBox(self)
        self.setDiskCheckbox.setText("Select disk")
        self.setDiskCheckbox.setToolTip("Click to image to to select target disk")
        self.setDiskCheckbox.setGeometry(QRect(750, 30, 100, 25))
        self.setDiskCheckbox.setLayoutDirection(Qt.RightToLeft)
        self.setDiskCheckbox.stateChanged.connect(self.disk_checkbox_click)

        # check box to set goal
        self.setGoalCheckbox = QCheckBox(self)
        self.setGoalCheckbox.setText("Set target")
        self.setGoalCheckbox.setToolTip("Click to image to set goal")
        self.setGoalCheckbox.setGeometry(QRect(750, 5, 100, 25))
        self.setGoalCheckbox.setLayoutDirection(Qt.RightToLeft)
        self.setGoalCheckbox.stateChanged.connect(self.goal_checkbox_click)

        # check box save video on disk
        self.saveVideoCheckbox = QCheckBox(self)
        self.saveVideoCheckbox.setText("Save video")
        self.saveVideoCheckbox.setToolTip("Click to save/stop saving the video on the disk")
        self.saveVideoCheckbox.setGeometry(QRect(850, 5, 100, 25))
        self.saveVideoCheckbox.setLayoutDirection(Qt.RightToLeft)
        self.saveVideoCheckbox.stateChanged.connect(self.save_video_checkbox_click)

        # check box to draw marks
        self.drawMarksCheckbox = QCheckBox(self)
        self.drawMarksCheckbox.setText("Draw marks")
        self.drawMarksCheckbox.setToolTip("Click to draw marks into image")
        self.drawMarksCheckbox.setGeometry(QRect(1100, 5, 100, 25))
        self.drawMarksCheckbox.setLayoutDirection(Qt.RightToLeft)
        self.drawMarksCheckbox.stateChanged.connect(self.draw_marks_checkbox_click)

        # check box to set laser
        self.setLaserCheckbox = QCheckBox(self)
        self.setLaserCheckbox.setText("Set laser")
        self.setLaserCheckbox.setToolTip("Click to image to set laser position")
        self.setLaserCheckbox.setGeometry(QRect(1100, 35, 100, 25))
        self.setLaserCheckbox.setLayoutDirection(Qt.RightToLeft)
        self.setLaserCheckbox.stateChanged.connect(self.set_laser_checkbox_click)

        # check box to set sfl
        self.setSflCheckbox = QCheckBox(self)
        self.setSflCheckbox.setText("Set sfl")
        self.setSflCheckbox.setToolTip("Click to image to set sfl position")
        self.setSflCheckbox.setGeometry(QRect(1000, 5, 100, 25))
        self.setSflCheckbox.setLayoutDirection(Qt.RightToLeft)
        self.setSflCheckbox.stateChanged.connect(self.set_sfl_checkbox_click)

        # find disks button
        self.findDisksButton = QPushButton('Find disks', self)
        self.findDisksButton.setToolTip('Click to find disks')
        self.findDisksButton.move(1300, 5)
        self.findDisksButton.setFixedHeight(22)
        self.findDisksButton.clicked.connect(self.find_disks)

        # automode button
        self.autoModeButton = QPushButton('Auto ON', self)
        self.autoModeButton.setToolTip('Auto ON')
        self.autoModeButton.move(1750, 5)
        self.autoModeButton.setFixedHeight(22)
        self.autoModeButton.clicked.connect(self.automode)

        # laser swithc button
        self.laserButton = QPushButton('Laser ON', self)
        self.laserButton.setToolTip('Laser ON')
        self.laserButton.move(1750, 35)
        self.laserButton.setFixedHeight(22)
        self.laserButton.clicked.connect(self.laser_switch)



        # key events
        # self.keyPressEvent = self.keyPressEvent

        # start Raspi communication thread
        self.raspi_comm = RaspiWorker.RaspiWorker()
        self.raspi_comm.signal_comm_err.connect(self.raspi_fail)
        self.raspi_comm.start()

        # start Disk Core thread
        self.disk_core = DiskCore.DiskCore([self.disk_x_loc, self.disk_y_loc],
                                           [self.laser_x_loc, self.laser_y_loc],
                                           [self.goal_x_loc, self.goal_y_loc],
                                           self.laser_pulse_n * (self.laser_on_time + self.laser_off_time), self.offset,
                                           self.mag_value)
        self.disk_core.gray_image_request.connect(self.core_image_request)
        self.disk_core.steppers_request.connect(self.move_steppers)
        self.disk_core.coords_update.connect(self.update_coords)
        self.disk_core.laser_shot.connect(self.blink_laser_n)
        self.disk_core.auto_done.connect(self.automode_finished)

        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()
        self.endpoint = QPoint()



        # video settings window
        self.video_settings_window = VideoSettingsWindow(self.save_interval, self.save_namespace, self.save_path)
        self.video_settings_window.closed.connect(self.video_settings_close)

        # laser settings window
        self.laser_settings_window = LaserSettingsWindow(self.laser_pulse_n, self.laser_on_time, self.laser_off_time,
                                                         self.laser_x_loc, self.laser_y_loc, self.offset)
        self.laser_settings_window.change_params.connect(self.laser_settings_changed)
        self.laser_settings_window.laser_control_signal.connect(self.laser_control)

        self.sfl_settings_window = sflSettingsWindow(self.sfl_flush_on, self.sfl_flush_off, self.sfl_light_on,
                                                     self.sfl_light_off, self.sfl_pulse, self.sfl_radius,
                                                     self.stamping_dx, self.stamping_dy, self.stamping_x_delay,
                                                     self.stamping_y_delay, self.stamping_light_on,
                                                     self.stamping_light_off, self.stamping_flush_on,
                                                     self.stamping_flush_off, self.stamping_x_steps,
                                                     self.stamping_y_steps, self.stamping_batch_size)
        self.sfl_settings_window.change_params.connect(self.sfl_settings_changed)

        self.sfl_settings_window.sfl_switch_signal.connect(self.sfl_switch)
        self.sfl_settings_window.pulse_signal.connect(self.pulse)
        self.sfl_settings_window.flush_switch_signal.connect(self.flush_switch)
        self.sfl_settings_window.light_switch_signal.connect(self.light_switch)
        self.sfl_settings_window.stamping_switch_signal.connect(self.stamping_switch)
        # signal from sfl window
        # self.sfl_settings_window.key_press_signal.connect(self.sfl_key)

        # check box for magnificience
        self.magLabel = QLabel(self)
        self.magLabel.setText("Magnification")
        self.magLabel.setGeometry(QRect(10, 30, 80, 25))
        self.mag4Checkbox = QCheckBox(self)
        self.mag4Checkbox.setText("4x")
        self.mag4Checkbox.setToolTip("Click to set magnification")
        self.mag4Checkbox.setGeometry(QRect(70, 30, 40, 25))
        self.mag4Checkbox.setLayoutDirection(Qt.RightToLeft)
        self.mag4Checkbox.stateChanged.connect(lambda: self.mag_click(self.mag4Checkbox))
        self.mag10Checkbox = QCheckBox(self)
        self.mag10Checkbox.setText("10x")
        self.mag10Checkbox.setToolTip("Click to set magnification")
        self.mag10Checkbox.setGeometry(QRect(110, 30, 40, 25))
        self.mag10Checkbox.setLayoutDirection(Qt.RightToLeft)
        self.mag10Checkbox.stateChanged.connect(lambda: self.mag_click(self.mag10Checkbox))
        self.mag20Checkbox = QCheckBox(self)
        self.mag20Checkbox.setText("20x")
        self.mag20Checkbox.setToolTip("Click to set magnification")
        self.mag20Checkbox.setGeometry(QRect(150, 30, 40, 25))
        self.mag20Checkbox.setLayoutDirection(Qt.RightToLeft)
        self.mag20Checkbox.stateChanged.connect(lambda: self.mag_click(self.mag20Checkbox))
        self.mag40Checkbox = QCheckBox(self)
        self.mag40Checkbox.setText("40x")
        self.mag40Checkbox.setToolTip("Click to set magnification")
        self.mag40Checkbox.setGeometry(QRect(190, 30, 40, 25))
        self.mag40Checkbox.setLayoutDirection(Qt.RightToLeft)
        self.mag40Checkbox.stateChanged.connect(lambda: self.mag_click(self.mag40Checkbox))

        if self.mag_value == 4:
            self.mag4Checkbox.setChecked(True)
        elif self.mag_value == 10:
            self.mag10Checkbox.setChecked(True)
        elif self.mag_value == 20:
            self.mag20Checkbox.setChecked(True)
        self.checkboxMag_group = QtWidgets.QButtonGroup(self)
        self.checkboxMag_group.addButton(self.mag4Checkbox)
        self.checkboxMag_group.addButton(self.mag10Checkbox)
        self.checkboxMag_group.addButton(self.mag20Checkbox)
        self.checkboxMag_group.addButton(self.mag40Checkbox)
        self.checkboxMag_group.setExclusive(True)

        # self.checkboxMarks_group = QtWidgets.QButtonGroup(self)
        # self.checkboxMarks_group.addButton(self.setSflCheckbox)
        # self.checkboxMarks_group.addButton(self.setGoalCheckbox)
        # self.checkboxMarks_group.addButton(self.setDiskCheckbox)
        # self.checkboxMarks_group.addButton(self.setLaserCheckbox)

        self.showMaximized()

    def stamping_switch(self, command):
        if command == "start":
            pass
        elif command == "end":
            pass
        print(command)

    def keyboardEventReceived(self, event):
        keyboard_pressed = event.name
        if keyboard_pressed == "a":
            # move left
            self.raspi_comm.requests_queue.append("x-" + str(self.steppers_x))

            # TODO recompute goal and target disk coord
            self.disk_core.recompute_goal(-self.steppers_x, 0)
            self.disk_core.recompute_disk(-self.steppers_x, 0)
            self.disk_core.coords_update.emit(self.disk_core.goal_x, self.disk_core.goal_y,
                                              self.disk_core.target_disk_x, self.disk_core.target_disk_y)

        elif keyboard_pressed == "d":
            # move right
            self.raspi_comm.requests_queue.append("x" + str(self.steppers_x))
            self.disk_core.recompute_goal(self.steppers_x, 0)
            self.disk_core.recompute_disk(self.steppers_x, 0)
            self.disk_core.coords_update.emit(self.disk_core.goal_x, self.disk_core.goal_y,
                                              self.disk_core.target_disk_x, self.disk_core.target_disk_y)
        elif keyboard_pressed == "s":
            # move top
            self.raspi_comm.requests_queue.append("y-" + str(self.steppers_y))
            self.disk_core.recompute_goal(0, -self.steppers_y)
            self.disk_core.recompute_disk(0, -self.steppers_y)
            self.disk_core.coords_update.emit(self.disk_core.goal_x, self.disk_core.goal_y,
                                              self.disk_core.target_disk_x, self.disk_core.target_disk_y)
        elif keyboard_pressed == "w":
            # move down
            self.raspi_comm.requests_queue.append("y" + str(self.steppers_y))
            self.disk_core.recompute_goal(0, self.steppers_y)
            self.disk_core.recompute_disk(0, self.steppers_y)
            self.disk_core.coords_update.emit(self.disk_core.goal_x, self.disk_core.goal_y,
                                              self.disk_core.target_disk_x, self.disk_core.target_disk_y)
        elif keyboard_pressed == "q":
            self.raspi_comm.requests_queue.append("s")
        elif keyboard_pressed == "e":
            self.raspi_comm.requests_queue.append("l")



    def sfl_key(self, pressed_key):
        print(pressed_key)
        if pressed_key == 65:
            # move left
            self.raspi_comm.requests_queue.append("x-" + str(self.steppers_x))

            # TODO recompute goal and target disk coord
            self.disk_core.recompute_goal(-self.steppers_x, 0)
            self.disk_core.recompute_disk(-self.steppers_x, 0)
            self.disk_core.coords_update.emit(self.disk_core.goal_x, self.disk_core.goal_y,
                                              self.disk_core.target_disk_x, self.disk_core.target_disk_y)

        elif pressed_key == 68:
            # move right
            self.raspi_comm.requests_queue.append("x" + str(self.steppers_x))
            self.disk_core.recompute_goal(self.steppers_x, 0)
            self.disk_core.recompute_disk(self.steppers_x, 0)
            self.disk_core.coords_update.emit(self.disk_core.goal_x, self.disk_core.goal_y,
                                              self.disk_core.target_disk_x, self.disk_core.target_disk_y)
        elif pressed_key == 83:
            # move top
            self.raspi_comm.requests_queue.append("y-" + str(self.steppers_y))
            self.disk_core.recompute_goal(0, -self.steppers_y)
            self.disk_core.recompute_disk(0, -self.steppers_y)
            self.disk_core.coords_update.emit(self.disk_core.goal_x, self.disk_core.goal_y,
                                              self.disk_core.target_disk_x, self.disk_core.target_disk_y)
        elif pressed_key == 87:
            # move down
            self.raspi_comm.requests_queue.append("y" + str(self.steppers_y))
            self.disk_core.recompute_goal(0, self.steppers_y)
            self.disk_core.recompute_disk(0, self.steppers_y)
            self.disk_core.coords_update.emit(self.disk_core.goal_x, self.disk_core.goal_y,
                                              self.disk_core.target_disk_x, self.disk_core.target_disk_y)
        elif pressed_key == 81:
            self.raspi_comm.requests_queue.append("s")
        elif pressed_key == 69:
            self.raspi_comm.requests_queue.append("l")


    def mag_click(self, mag):
        mag_text = mag.text()
        if mag_text == "4x":
            self.mag_value = 4
            print("4x")
            self.disk_core.mag = 4

        elif mag_text == "10x":
            self.mag_value = 10
            self.disk_core.mag = 10
            print("10x")
        elif mag_text == "20x":
            self.mag_value = 20
            self.disk_core.mag = 20
            print("20x")
        elif mag_text == "40x":
            self.mag_value = 40
            self.disk_core.mag = 40
            print("40x")
        self.config.set("camera", "mag", self.mag_value)
        self.update_config_file()

    def set_sfl_checkbox_click(self, state):
        self.set_sfl_enabled = state

    def laser_control(self, command):
        self.raspi_comm.requests_queue.append(command)

    def sfl_settings_changed(self, light_on, light_off, flush_on, flush_off, pulse, radius,
                             stamping_dx, stamping_dy, stamping_x_delay, stamping_y_delay, stamping_light_on,
                             stamping_light_off, stamping_flush_on, stamping_flush_off, stamping_x_steps,
                             stamping_y_steps, stamping_batch_size):
        self.sfl_light_on = light_on
        self.sfl_light_off = light_off
        self.sfl_flush_off = flush_off
        self.sfl_flush_on = flush_on
        self.sfl_pulse = pulse
        self.sfl_radius = radius

        self.stamping_dx = stamping_dx
        self.stamping_dy = stamping_dy
        self.stamping_x_delay = stamping_x_delay
        self.stamping_y_delay = stamping_y_delay
        self.stamping_light_on = stamping_light_on
        self.stamping_light_off = stamping_light_off
        self.stamping_flush_on = stamping_flush_on
        self.stamping_flush_off = stamping_flush_off
        self.stamping_x_steps = stamping_x_steps
        self.stamping_y_steps = stamping_y_steps
        self.stamping_batch_size = stamping_batch_size

        self.config.set("sfl", "pulse", self.sfl_pulse)
        self.config.set("sfl", "light_on", self.sfl_light_on)
        self.config.set("sfl", "light_off", self.sfl_light_off)
        self.config.set("sfl", "flush_on", self.sfl_flush_on)
        self.config.set("sfl", "flush_off", self.sfl_flush_off)
        self.config.set("sfl", "radius", self.sfl_radius)

        self.config.set("stamping", "dx", self.stamping_dx)
        self.config.set("stamping", "dy", self.stamping_dy)
        self.config.set("stamping", "x_delay", self.stamping_x_delay)
        self.config.set("stamping", "y_delay", self.stamping_y_delay)
        self.config.set("stamping", "light_on", self.stamping_light_on)
        self.config.set("stamping", "light_off", self.stamping_light_off)
        self.config.set("stamping", "flush_on", self.stamping_flush_on)
        self.config.set("stamping", "flush_off", self.stamping_flush_off)
        self.config.set("stamping", "x_steps", self.stamping_x_steps)
        self.config.set("stamping", "y_steps", self.stamping_y_steps)
        self.config.set("stamping", "batch_size", self.stamping_batch_size)
        self.update_config_file()


    def laser_settings_changed(self, n, on, off, x, y, offset):
        self.laser_pulse_n = n
        self.laser_on_time = on
        self.laser_off_time = off
        self.laser_x_loc = x
        self.laser_y_loc = y
        self.offset = offset
        self.config.set("laser", "pulses", self.laser_pulse_n)
        self.config.set("laser", "on_time", self.laser_on_time)
        self.config.set("laser", "off_time", self.laser_off_time)
        self.config.set("laser", "x_loc", self.laser_x_loc)
        self.config.set("laser", "y_loc", self.laser_y_loc)
        self.config.set("laser", "offset", self.offset)
        self.disk_core.region_offset = self.offset
        self.update_config_file()

    def pulse(self):
        self.raspi_comm.requests_queue.append("a" + "," + str(self.sfl_light_on) + "," + str(self.sfl_pulse))


    def sfl_pulse_edited(self):
        self.sfl_pulse = int(self.sflPulseInput.text())
        self.message_text.setPlainText("sfl pulse: {} ".format(str(self.sfl_pulse)))
        self.config.set("sfl", "pulse", self.sfl_pulse)
        self.update_config_file()

    def flush_switch(self):
        if self.sfl_settings_window.sflFlushButton.text() == "Flush ON":
            self.sfl_settings_window.sflFlushButton.setText("Flush OFF")
            self.raspi_comm.requests_queue.append("n")
        else:
            self.raspi_comm.requests_queue.append("m")
            self.sfl_settings_window.sflFlushButton.setText("Flush ON")

    def light_switch(self):
        if self.sfl_settings_window.sflLightButton.text() == "Light ON":
            self.sfl_settings_window.sflLightButton.setText("Light OFF")
            self.raspi_comm.requests_queue.append("j")
        else:
            self.raspi_comm.requests_queue.append("h")
            self.sfl_settings_window.sflLightButton.setText("Light ON")

    def sfl_switch(self):
        if self.sfl_settings_window.sflButton.text() == "SFL ON":
            self.sfl_settings_window.sflButton.setText("SFL OFF")
            self.raspi_comm.requests_queue.append("p" + "," + str(self.sfl_flush_on) + "," + str(self.sfl_flush_off) +
                                                  "," + str(self.sfl_light_on) + "," + str(self.sfl_light_off))
        else:
            self.raspi_comm.requests_queue.clear()
            self.raspi_comm.requests_queue.append("r")
            self.sfl_settings_window.sflButton.setText("SFL ON")

            # TODO stop

    def sfl_light_on_edited(self):
        self.sfl_settings_window.sfl_light_on = int(self.sflLightOnInput.text())
        self.message_text.setPlainText("sfl light on: {} ".format(str(self.sfl_light_on)))
        self.config.set("sfl", "light_on", self.sfl_light_on)
        self.update_config_file()

    def sfl_light_off_edited(self):
        self.sfl_light_off = int(self.sflLightOffInput.text())
        self.message_text.setPlainText("sfl light off: {} ".format(str(self.sfl_light_off)))
        self.config.set("sfl", "light_off", self.sfl_light_off)
        self.update_config_file()

    def sfl_flush_on_edited(self):
        self.sfl_flush_on = int(self.sflFlushOnInput.text())
        self.message_text.setPlainText("sfl flush on: {} ".format(str(self.sfl_flush_on)))
        self.config.set("sfl", "flush_on", self.sfl_flush_on)
        self.update_config_file()

    def sfl_flush_off_edited(self):
        self.sfl_flush_off = int(self.sflFlushOffInput.text())
        self.message_text.setPlainText("sfl flush off: {} ".format(str(self.sfl_flush_off)))
        self.config.set("sfl", "flush_off", self.sfl_flush_off)
        self.update_config_file()

    def laser_switch(self):
        if self.laserButton.text() == "Laser ON":
            self.raspi_comm.requests_queue.append("s")
            self.laserButton.setText("Laser OFF")
        else:
            self.raspi_comm.requests_queue.append("l")
            self.laserButton.setText("Laser ON")

    def automode_finished(self):
        pass

    def update_coords(self, goal_x, goal_y, disk_x, disk_y):
        self.goal_x_loc = goal_x
        self.goal_y_loc = goal_y
        self.disk_x_loc = disk_x
        self.disk_y_loc = disk_y

        self.goalCoordXInput.setText(str(goal_x))
        self.goalCoordYInput.setText(str(goal_y))
        self.diskCoordXInput.setText(str(disk_x))
        self.diskCoordYInput.setText(str(disk_y))

    def move_steppers(self, x, y):
        print("asdasdasdasda")
        print("steppers request:", x, ", ", y)
        self.raspi_comm.requests_queue.append("x" + str(x))
        print("x sent")
        self.raspi_comm.requests_queue.append("y" + str(y))
        print("y sent")

    def automode(self):
        if self.autoModeButton.text() == "Auto ON":
            self.autoModeButton.setText("Auto OFF")
            self.automode_enabled = True
            self.disk_core.auto_mode = True
            self.disk_core.auto_step = -1
            self.disk_core.target_disk_x = self.disk_x_loc
            self.disk_core.target_disk_y = self.disk_y_loc
            self.disk_core.laser_x = self.laser_x_loc
            self.disk_core.laser_y = self.laser_y_loc
            self.disk_core.goal_x = self.goal_x_loc
            self.disk_core.goal_y = self.goal_y_loc
            self.disk_core.start()
        else:
            self.autoModeButton.setText("Auto ON")
            self.automode_enabled = False
            self.disk_core.auto_mode = False

    def core_image_request(self):
        self.disk_core.image_to_process = np.copy(self.gray_image)

    def find_disks(self):
        helpy_im = self.gray_image
        locs = self.disk_core.find_disks(helpy_im)
        for max_loc in locs:
            helpy_im = cv2.drawMarker(helpy_im, max_loc, (255, 255, 255), markerType=cv2.MARKER_CROSS,
                                      markerSize=20, thickness=1, line_type=cv2.LINE_AA)

            cv2.putText(helpy_im, str(max_loc), max_loc, cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 2,
                        cv2.LINE_AA)
        helpy_im = cv2.resize(helpy_im, (1280, 720))
        cv2.imshow("Disk locations", helpy_im)
        cv2.waitKey(0)

    def set_laser_checkbox_click(self, state):
        self.set_laser_enabled = state


    def draw_marks_checkbox_click(self, state):
        self.draw_marks_enabled = state


    def save_video_checkbox_click(self, state):
        if self.camera_worker is not None:
            self.camera_worker.grab_flag = state

    def laser_checkbox_click(self, state):
        self.move_laser_enabled = state

    def disk_checkbox_click(self, state):
        self.set_disk_enabled = state


    def goal_checkbox_click(self, state):
        self.set_goal_enabled = state


    def click_to_get_coords(self, event):
        x_pixmap = event.pos().x()
        y_pixmap = event.pos().y()
        x_scale = self.cam_width_value / self.PIXMAP_WIDTH
        y_scale = self.cam_height_value / self.PIXMAP_HEIGHT
        x_image = int(x_pixmap * x_scale)
        y_image = int(y_pixmap * y_scale)

        if self.move_laser_enabled:
            print(x_image)
            print(y_image)
            steps_x = x_image - self.laser_x_loc
            steps_y = y_image - self.laser_y_loc
            print("y" + str(int(6.6666 * steps_y)))
            print("x" + str(int(6.6666 * steps_x)))
            self.raspi_comm.requests_queue.append("y" + str(int(6.6666 * steps_y/2.5)))
            self.raspi_comm.requests_queue.append("x" + str(int(6.6666 * steps_x/2.5)))

            # TODO send command to RaspiWorker
        elif self.set_goal_enabled:
            self.goal_x_loc = x_image
            self.goal_y_loc = y_image
            self.goalCoordXInput.setText(str(x_image))
            self.goalCoordYInput.setText(str(y_image))
            self.config.set("goal", "x_loc", self.goal_x_loc)
            self.config.set("goal", "y_loc", self.goal_y_loc)
            self.disk_core.goal_x = self.goal_x_loc
            self.disk_core.goal_y = self.goal_y_loc
            self.update_config_file()
        elif self.set_disk_enabled:
            locs = self.disk_core.find_disks(self.gray_image)
            if len(locs) > 0:
                nearest_disk = self.disk_core.nearest_disk([x_image, y_image], locs)
                self.disk_x_loc = nearest_disk[0]
                self.disk_y_loc = nearest_disk[1]
                self.diskCoordXInput.setText(str(self.disk_x_loc))
                self.diskCoordYInput.setText(str(self.disk_y_loc))
                self.config.set("disk", "x_loc", self.disk_x_loc)
                self.config.set("disk", "y_loc", self.disk_y_loc)
                self.disk_core.target_disk_x = self.disk_x_loc
                self.disk_core.target_disk_y = self.disk_y_loc
                self.update_config_file()
        elif self.set_laser_enabled:
            self.laser_x_loc = x_image
            self.laser_y_loc = y_image
            self.laser_settings_window.laserCoordXInput.setText(str(x_image))
            self.laser_settings_window.laserCoordYInput.setText(str(y_image))
            self.config.set("laser", "x_loc", self.laser_x_loc)
            self.config.set("laser", "y_loc", self.laser_y_loc)
            self.update_config_file()
        elif self.video_settings_window.roi_enabled:
            if event.button() == QtCore.Qt.LeftButton:
                self.origin = QPoint(x_pixmap, y_pixmap)
                self.rubberBand.setGeometry(QRect(QPoint(x_pixmap + 10, y_pixmap + 60), QSize()))
                self.rubberBand.show()
        elif self.set_sfl_enabled:
            self.sfl_x_loc = x_image
            self.sfl_y_loc = y_image
            self.config.set("sfl", "x_loc", self.sfl_x_loc)
            self.config.set("sfl", "y_loc", self.sfl_y_loc)
            self.update_config_file()

    def video_settings_close(self, save_interval, save_namespace, save_path):
        self.save_interval = save_interval
        self.save_namespace = save_namespace
        self.save_path = save_path
        self.config.set("video", "interval", save_interval)
        self.config.set("video", "namespace", save_namespace)
        self.config.set("video", "path", save_path)
        self.camera_worker.grab_period = save_interval
        self.camera_worker.grab_directory = save_path
        self.camera_worker.grab_namespace = save_namespace
        self.update_config_file()

    def save_video_settings(self):
        self.video_settings_window.show()
        # print(self.video_settings_window.some_bullshit)

    def show_laser_settings(self):
        self.laser_settings_window.show()

    def show_sfl_settings(self):
        self.sfl_settings_window.show()

    def steppers_x_edited(self):
        """Function to set steppers steps for manual control"""
        self.steppers_x = int(self.steppersXInput.text())
        self.message_text.setPlainText("stepper x: {} ".format(str(self.steppers_x)))
        self.config.set("steppers", "x", self.steppers_x)
        self.update_config_file()

    def steppers_y_edited(self):
        """Function to set steppers steps for manual control"""
        self.steppers_y = int(self.steppersYInput.text())
        self.message_text.setPlainText("stepper y: {} ".format(str(self.steppers_y)))
        self.config.set("steppers", "y", self.steppers_y)
        self.update_config_file()

    def red_button(self):
        self.raspi_comm.requests_queue.clear()
        self.raspi_comm.requests_queue.append("r")

    def init_raspi(self, event):
        self.raspiStatus.setStyleSheet("background-color:green;")
        if not self.raspi_comm.raspi_status:
            self.raspi_comm = RaspiWorker.RaspiWorker()
            self.raspi_comm.signal_comm_err.connect(self.raspi_fail)
            self.raspi_comm.start()


    def blink_laser_n(self):
        time_on = int(self.laser_on_time)
        time_off = int(self.laser_off_time)
        n = int(self.laser_pulse_n)
        self.raspi_comm.requests_queue.append("q" + "," + str(time_on) + "," + str(time_off) + "," + str(n))

    def raspi_fail(self):
        self.message_text.setPlainText("raspi went wrong")
        self.raspiStatus.setStyleSheet("background-color:red;")
        self.raspi_comm.terminate()

    def keyPressEvent(self, e):
        print(e.key())
        self.message_text.setPlainText("event " + str(e.key()))
        if e.key() == 65:
            # move left
            self.raspi_comm.requests_queue.append("x-" + str(self.steppers_x))

            # TODO recompute goal and target disk coord
            self.disk_core.recompute_goal(-self.steppers_x, 0)
            self.disk_core.recompute_disk(-self.steppers_x, 0)
            self.disk_core.coords_update.emit(self.disk_core.goal_x, self.disk_core.goal_y,
                                              self.disk_core.target_disk_x, self.disk_core.target_disk_y)

        elif e.key() == 68:
            # move right
            self.raspi_comm.requests_queue.append("x" + str(self.steppers_x))
            self.disk_core.recompute_goal(self.steppers_x, 0)
            self.disk_core.recompute_disk(self.steppers_x, 0)
            self.disk_core.coords_update.emit(self.disk_core.goal_x, self.disk_core.goal_y,
                                              self.disk_core.target_disk_x, self.disk_core.target_disk_y)
        elif e.key() == 83:
            # move top
            self.raspi_comm.requests_queue.append("y-" + str(self.steppers_y))
            self.disk_core.recompute_goal(0, -self.steppers_y)
            self.disk_core.recompute_disk(0, -self.steppers_y)
            self.disk_core.coords_update.emit(self.disk_core.goal_x, self.disk_core.goal_y,
                                              self.disk_core.target_disk_x, self.disk_core.target_disk_y)
        elif e.key() == 87:
            # move down
            self.raspi_comm.requests_queue.append("y" + str(self.steppers_y))
            self.disk_core.recompute_goal(0, self.steppers_y)
            self.disk_core.recompute_disk(0, self.steppers_y)
            self.disk_core.coords_update.emit(self.disk_core.goal_x, self.disk_core.goal_y,
                                              self.disk_core.target_disk_x, self.disk_core.target_disk_y)
        elif e.key() == 81:
            self.raspi_comm.requests_queue.append("s")
        elif e.key() == 69:
            self.raspi_comm.requests_queue.append("l")

    def goal_x_loc_edited(self):
        """Function to set the goal coord"""
        self.goal_x_loc = int(self.goalCoordXInput.text())
        self.message_text.setPlainText("goal x loc: {} ".format(str(self.goal_x_loc)))
        self.config.set("goal", "x_loc", self.goal_x_loc)
        self.update_config_file()

    def goal_y_loc_edited(self):
        """Function to set the goal coord"""
        self.goal_y_loc = int(self.goalCoordYInput.text())
        self.message_text.setPlainText("goal y loc: {} ".format(str(self.goal_y_loc)))
        self.config.set("goal", "y_loc", self.goal_y_loc)
        self.update_config_file()

    def disk_x_loc_edited(self):
        """Function to set the disk coord"""
        self.disk_x_loc = int(self.diskCoordXInput.text())
        self.message_text.setPlainText("disk x loc: {} ".format(str(self.disk_x_loc)))
        self.config.set("disk", "x_loc", self.disk_x_loc)
        self.update_config_file()

    def disk_y_loc_edited(self):
        """Function to set the disk coord"""
        self.disk_y_loc = int(self.diskCoordYInput.text())
        self.message_text.setPlainText("disk y loc: {} ".format(str(self.disk_y_loc)))
        self.config.set("disk", "y_loc", self.disk_y_loc)
        self.update_config_file()

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
                self.message_text.setPlainText("Height value error")
                print("ValueError")

    def run_camera(self):
        if self.cameraComboBox.count() > 0:
            if self.runCameraButton.text() == "Run camera":
                self.cameraComboBox.setEnabled(False)
                self.camera_worker = CameraWorker.CameraWorker(self.cameraComboBox.currentIndex(), self.cam_width_value,
                                                               self.cam_height_value, self.cam_fps_value,
                                                               self.cam_exposure_value, self.cam_gain_value,
                                                               self.cam_brightness_value, self.save_interval,
                                                               self.save_namespace, self.save_path)
                self.camera_worker.image_ready.connect(self.obtain_image)
                self.camera_worker.start()
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
        if self.video_settings_window.roiCheckbox.isChecked():
            self.camera_worker.save_roi = True
        else:
            self.camera_worker.save_roi = False
        self.camera_worker.mutex.unlock()
        self.gray_image = cv2.cvtColor(self.image_to_display, cv2.COLOR_BGR2GRAY)
        if self.draw_marks_enabled:
            # TODO wrap draw markers into function that will check the coords (if it is inside of img)
            pass
            self.gray_image = cv2.drawMarker(self.gray_image, (self.goal_x_loc, self.goal_y_loc), (0, 255, 255),
                                             markerType=cv2.MARKER_DIAMOND, markerSize=20, thickness=1,
                                             line_type=cv2.LINE_AA)
            self.gray_image = cv2.drawMarker(self.gray_image, (self.disk_x_loc, self.disk_y_loc), (255, 255, 0),
                                             markerType=cv2.MARKER_TILTED_CROSS, markerSize=20, thickness=1,
                                             line_type=cv2.LINE_AA)
            self.gray_image = cv2.drawMarker(self.gray_image, (self.laser_x_loc, self.laser_y_loc), (0, 255, 0),
                                             markerType=cv2.MARKER_STAR, markerSize=20, thickness=1,
                                             line_type=cv2.LINE_AA)
            self.gray_image = cv2.drawMarker(self.gray_image, (self.sfl_x_loc, self.sfl_y_loc), (0, 255, 0),
                                             markerType=cv2.MARKER_CROSS, markerSize=20, thickness=1,
                                             line_type=cv2.LINE_AA)
            self.gray_image = cv2.circle(self.gray_image, (self.sfl_x_loc, self.sfl_y_loc), self.sfl_radius,
                                         (0, 255, 0), 2)
            x_scale = self.cam_width_value / self.PIXMAP_WIDTH
            y_scale = self.cam_height_value / self.PIXMAP_HEIGHT
            if self.draw_roi:
                rectangle_startpoint_x = int(x_scale * self.origin.x())
                rectangle_startpoint_y = int(y_scale * self.origin.y())
                rectangle_endpoint_x = int(x_scale * self.endpoint.x())
                rectangle_endpoint_y = int(y_scale * self.endpoint.y())
                self.camera_worker.roi_origin = (rectangle_startpoint_x, rectangle_startpoint_y)
                self.camera_worker.roi_endpoint = (rectangle_endpoint_x, rectangle_endpoint_y)
                self.gray_image = cv2.rectangle(self.gray_image, (rectangle_startpoint_x,
                                                                  rectangle_startpoint_y),
                                                (rectangle_endpoint_x, rectangle_endpoint_y),
                                                (250, 255, 0), 2)
        height, width = self.gray_image.shape[:2]
        image_for_pixmap = QtGui.QImage(self.gray_image, width, height, QtGui.QImage.Format_Grayscale8)
        #self.imageDisplay.setPixmap(QPixmap(image_for_pixmap).scaled(1280, 720))
        self.imageDisplay.setPixmap(QPixmap(image_for_pixmap).scaled(self.PIXMAP_WIDTH, self.PIXMAP_HEIGHT))

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
            cap = cv2.VideoCapture(index)
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

    def mouseMoveEvent(self, event):
        if not self.origin.isNull() and self.video_settings_window.roi_enabled:
            self.rubberBand.setGeometry(QRect(QPoint(self.origin.x()+10, self.origin.y()+60),
                                              QPoint(event.pos().x()+10, event.pos().y()+60)))

    def mouseReleaseEvent(self, event):

        if event.button() == QtCore.Qt.LeftButton and self.video_settings_window.roi_enabled:
            self.rubberBand.hide()
            self.endpoint = QPoint(event.pos())

            self.video_settings_window.roi_enabled = False
            self.draw_roi = True




if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    mainWin = ExampleWindow()
    mainWin.show()
    sys.exit(app.exec_())
