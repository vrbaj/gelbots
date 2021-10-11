"""
This module is implementing the window with laser settings and control.
"""

from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import QSize, QRect, pyqtSignal
from PyQt5.QtGui import QIntValidator, QFont

from error_handling import ErrorLogger
from gelbots_dataclasses import LaserParams


class LaserSettingsWindow(QMainWindow):
    """
    This class is implementing the Laser window that cointains all settings
    related to laser and its control button (ON/OFF).
    """

    # pylint: disable=too-many-instance-attributes
    # Eight is reasonable in this case.

    change_params = pyqtSignal(object)
    laser_control_signal = pyqtSignal(str)

    def __init__(self, laser_params: LaserParams):
        super().__init__()
        self.logger = ErrorLogger()
        self.laser_params = laser_params
        self.int_validator = QIntValidator()

        # set window properties
        self.setMinimumSize(QSize(250, 300))
        self.setWindowTitle("Laser settings")

        # labels
        self.pulse_number_label = QLabel(self)
        self.laser_on_label = QLabel(self)
        self.laser_off_label = QLabel(self)
        self.laser_locx_label = QLabel(self)
        self.laser_locy_label = QLabel(self)
        self.laser_offset_label = QLabel(self)
        self.__init_labels()

        # input boxes
        self.pulse_number_input = QLineEdit(self)
        self.laser_on_input = QLineEdit(self)
        self.laser_off_input = QLineEdit(self)
        self.laser_coordx_input = QLineEdit(self)
        self.laser_coordy_input = QLineEdit(self)
        self.laser_offset_input = QLineEdit(self)
        self.__init_input_boxes()

        # laser blink button
        self.blink_laser_button = QPushButton("Blink On", self)
        self.__init_blink_laser_button()

        # laser switch button
        self.switch_laser_button = QPushButton(self)
        self.__init_laser_button()

        # Apply button
        self.validate_button = self.validate_settings

    def __init_blink_laser_button(self):
        """
        Function to set up blink laser button and connect the blink_laser
        function.
        :return:
        """
        self.blink_laser_button.setToolTip("Unlimited laser blink")
        self.blink_laser_button.setGeometry(QRect(10, 180, 230, 40))
        self.blink_laser_button.setFixedHeight(22)
        self.blink_laser_button.clicked.connect(self.blink_laser)

    def __init_laser_button(self):
        """
        Function __init_laser_button setups laser switching button
        :return:
        """
        self.switch_laser_button.setToolTip("Laser switch")
        self.switch_laser_button.setGeometry(QRect(10, 210, 230, 40))
        self.switch_laser_button.setFixedHeight(22)
        self.switch_laser_button.setText("Laser ON")
        self.switch_laser_button.clicked.connect(self.switch_laser)

    def __init_labels(self):
        """
        Function __init_labels sets labels params (position and text)
        :return:
        """
        # pulse number label
        self.pulse_number_label.setGeometry(QRect(10, 0, 80, 20))
        self.pulse_number_label.setText("Pulse n.:")
        # laser on label
        self.laser_on_label.setGeometry(QRect(10, 30, 80, 20))
        self.laser_on_label.setText("On.:")
        # laser off label
        self.laser_off_label.setGeometry(QRect(10, 60, 80, 20))
        self.laser_off_label.setText("Off.:")
        # laser x coordinate label
        self.laser_locx_label.setGeometry(QRect(10, 90, 80, 20))
        self.laser_locx_label.setText("X:")
        # laser y coordinate label
        self.laser_locy_label.setGeometry(QRect(10, 120, 80, 20))
        self.laser_locy_label.setText("Y:")
        # laser offset label
        self.laser_offset_label.setGeometry(QRect(10, 150, 80, 20))
        self.laser_offset_label.setText("Offset:")

    def __init_input_boxes(self):
        """
        Function __init_input_boxes sets up input boxes and their params.
        :return:
        """
        # pulse number input box
        self.pulse_number_input.setGeometry(QRect(60, 0, 40, 20))
        self.pulse_number_input.setText(str(self.laser_params.laser_pulse_n))
        self.pulse_number_input.setValidator(self.int_validator)
        # laser on input box
        self.laser_on_input.setGeometry(QRect(60, 30, 40, 20))
        self.laser_on_input.setText(str(self.laser_params.laser_on_time))
        self.laser_on_input.setValidator(self.int_validator)
        # laser off input box
        self.laser_off_input.setGeometry(QRect(60, 60, 40, 20))
        self.laser_off_input.setText(str(self.laser_params.laser_off_time))
        self.laser_off_input.setValidator(self.int_validator)
        # laser x coordinate input box
        self.laser_coordx_input.setGeometry(QRect(60, 90, 40, 20))
        self.laser_coordx_input.setValidator(self.int_validator)
        self.laser_coordx_input.setText(str(self.laser_params.laser_x_loc))
        # laser y coordinate input box
        self.laser_coordy_input.setGeometry(QRect(60, 120, 40, 20))
        self.laser_coordy_input.setValidator(self.int_validator)
        self.laser_coordy_input.setText(str(self.laser_params.laser_y_loc))
        # laser offset input box
        self.laser_offset_input.setGeometry(QRect(60, 150, 40, 20))
        self.laser_offset_input.setValidator(self.int_validator)
        self.laser_offset_input.setText(str(self.laser_params.offset))

    @property
    def validate_button(self):
        """
        Validate button as property. Probably will be removed
        and replaced by __init_validate_button like function.
        :return:
        """
        return self.__validate_button

    @validate_button.setter
    def validate_button(self, validate_settings):
        self.__validate_button = QPushButton(self)
        self.__validate_button.setGeometry(QRect(10, 240, 230, 40))
        self.__validate_button.setToolTip("Click to save settings")
        self.__validate_button.setFont(QFont('Times', 20))
        self.__validate_button.setText("Apply")
        self.__validate_button.clicked.connect(validate_settings)

    def validate_settings(self):
        """
        Function to collect data with laser settings from inputboxes.
        The data are sent via signal to gelbots.py.
        :return:
        """
        try:
            self.laser_params.laser_pulse_n = int(self.pulse_number_input.text())
            self.laser_params.laser_on_time = int(self.laser_on_input.text())
            self.laser_params.laser_off_time = int(self.laser_off_input.text())
            self.laser_params.laser_x_loc = int(self.laser_coordx_input.text())
            self.laser_params.laser_y_loc = int(self.laser_coordy_input.text())
            self.laser_params.offset = int(self.laser_offset_input.text())
            self.change_params.emit(self.laser_params)
        except ValueError:
            self.logger.logger.exception("Error in Laser window validate settings")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText("Laser params are not numbers")
            msg.setWindowTitle("Error")
            msg.exec_()

    def blink_laser(self):
        """
        Function to emit signal with laser blinking settings. Signal is accepted in gelbots.py
        that sends and appropriate request to RPI via worker_raspi.py.
        :return:
        """
        if self.blink_laser_button.text() == "Blink On":
            try:
                time_on = int(self.laser_params.laser_on_time)
                time_off = int(self.laser_params.laser_off_time)
                self.laser_control_signal.emit("k" + "," + str(time_on) + "," + str(time_off))
                self.blink_laser_button.setText("Blink Off")
            except ValueError:
                self.logger.logger.exception("Error in Laser window: Blink ON")
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error")
                msg.setInformativeText("Laser params are not numbers")
                msg.setWindowTitle("Error")
                msg.exec_()
        else:
            self.blink_laser_button.setText("Blink On")
            self.laser_control_signal.emit("t")

    def switch_laser(self):
        """
        Function to emit signal to gelbots.py about requested state of laser (ON/OFF).
        Signal is accepted in gelbots.py and the appropriate request is sent via worker_raspi.py.
        :return:
        """
        if self.switch_laser_button.text() == "Laser ON":
            self.laser_control_signal.emit("s")
            self.switch_laser_button.setText("Laser OFF")
        else:
            self.laser_control_signal.emit("l")
            self.switch_laser_button.setText("Laser ON")
