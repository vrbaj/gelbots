"""
This module is implementing the window with laser settings and control.
"""

from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import QSize, QRect, pyqtSignal
from PyQt5.QtGui import QIntValidator, QFont

from error_handling import ErrorLogger


class LaserSettingsWindow(QMainWindow):
    """
    This class is implementing the Laser window that cointains all settings
    related to laser and its control button (ON/OFF).
    """

    change_params = pyqtSignal(int, int, int, int, int, int)
    laser_control_signal = pyqtSignal(str)

    def __init__(self, pulse_number, on_time, off_time, x, y, offset):
        super().__init__()
        self.logger = ErrorLogger()
        self.offset = offset
        self.laser_pulse_n = pulse_number
        self.laser_on_time = on_time
        self.laser_off_time = off_time
        self.laser_x_loc = x
        self.laser_y_loc = y
        # set window properties
        self.setMinimumSize(QSize(250, 300))
        self.setWindowTitle("Laser settings")

        self.int_validator = QIntValidator()

        # LASER
        # Create pulse number label
        self.pulse_number_label = QLabel(self)
        self.pulse_number_label.setGeometry(QRect(10, 0, 80, 20))
        self.pulse_number_label.setText("Pulse n.:")

        # Create pulse number input box
        self.pulse_number_input = QLineEdit(self)
        self.pulse_number_input.setGeometry(QRect(60, 0, 40, 20))
        self.pulse_number_input.setText(str(self.laser_pulse_n))
        self.pulse_number_input.setValidator(self.int_validator)

        # Create laser on label
        self.laser_on_label = QLabel(self)
        self.laser_on_label.setGeometry(QRect(10, 30, 80, 20))
        self.laser_on_label.setText("On.:")

        # Create laser on input box
        self.laser_on_input = QLineEdit(self)
        self.laser_on_input.setGeometry(QRect(60, 30, 40, 20))
        self.laser_on_input.setText(str(self.laser_on_time))
        self.laser_on_input.setValidator(self.int_validator)

        # Create laser off label
        self.laser_off_label = QLabel(self)
        self.laser_off_label.setGeometry(QRect(10, 60, 80, 20))
        self.laser_off_label.setText("Off.:")

        # Create laser off input box
        self.laser_off_input = QLineEdit(self)
        self.laser_off_input.setGeometry(QRect(60, 60, 40, 20))
        self.laser_off_input.setText(str(self.laser_off_time))
        self.laser_off_input.setValidator(self.int_validator)

        # Create laser x loc label
        self.laser_locx_label = QLabel(self)
        self.laser_locx_label.setGeometry(QRect(10, 90, 80, 20))
        self.laser_locx_label.setText("X:")

        # Create laser x coordinate input box
        self.laser_coordx_input = QLineEdit(self)
        self.laser_coordx_input.setGeometry(QRect(60, 90, 40, 20))
        self.laser_coordx_input.setValidator(self.int_validator)
        self.laser_coordx_input.setText(str(self.laser_x_loc))

        # Create laser y loc label
        self.laser_locy_label = QLabel(self)
        self.laser_locy_label.setGeometry(QRect(10, 120, 80, 20))
        self.laser_locy_label.setText("Y:")

        # Create laser y coordinate input box
        self.laser_coordy_input = QLineEdit(self)
        self.laser_coordy_input.setGeometry(QRect(60, 120, 40, 20))
        self.laser_coordy_input.setValidator(self.int_validator)
        self.laser_coordy_input.setText(str(self.laser_y_loc))

        # Create laser offset label
        self.laser_offset_label = QLabel(self)
        self.laser_offset_label.setGeometry(QRect(10, 150, 80, 20))
        self.laser_offset_label.setText("Offset:")

        # Create laser y coordinate input box
        self.laser_offset_input = QLineEdit(self)
        self.laser_offset_input.setGeometry(QRect(60, 150, 40, 20))
        self.laser_offset_input.setValidator(self.int_validator)
        self.laser_offset_input.setText(str(self.offset))

        # laser blink button
        self.blink_laser_button = QPushButton("Blink On", self)
        self.blink_laser_button.setToolTip("Unlimited laser blink")
        self.blink_laser_button.setGeometry(QRect(10, 180, 230, 40))
        self.blink_laser_button.setFixedHeight(22)
        self.blink_laser_button.clicked.connect(self.blink_laser)

        # laser switch button
        self.switch_laser_button = self.switch_laser

        # Apply button
        self.validate_button = self.validate_settings

    @property
    def switch_laser_button(self):
        return self.__switch_laser_button

    @property
    def validate_button(self):
        return self.__validate_button

    @validate_button.setter
    def validate_button(self, validate_settings):
        self.__validate_button = QPushButton(self)
        self.__validate_button.setGeometry(QRect(10, 240, 230, 40))
        self.__validate_button.setToolTip("Click to save settings")
        self.__validate_button.setFont(QFont('Times', 20))
        self.__validate_button.setText("Apply")
        self.__validate_button.clicked.connect(validate_settings)

    @switch_laser_button.setter
    def switch_laser_button(self, switch_laser, **kwargs):
        if "button_text" in kwargs.keys():
            self.__switch_laser_button.setText(kwargs["button_text"])
        else:
            self.__switch_laser_button = QPushButton(self)
            self.__switch_laser_button.setToolTip("Laser switch")
            self.__switch_laser_button.setGeometry(QRect(10, 210, 230, 40))
            self.__switch_laser_button.setFixedHeight(22)
            self.__switch_laser_button.setText("Laser ON")
            self.__switch_laser_button.clicked.connect(switch_laser)

    def validate_settings(self):
        """
        Function to collect data with laser settings from inputboxes.
        The data are sent via signal to main.py.
        :return:
        """
        try:
            self.laser_pulse_n = int(self.pulse_number_input.text())
            self.laser_on_time = int(self.laser_on_input.text())
            self.laser_off_time = int(self.laser_off_input.text())
            self.laser_x_loc = int(self.laser_coordx_input.text())
            self.laser_y_loc = int(self.laser_coordy_input.text())
            self.offset = int(self.laser_offset_input.text())
            self.change_params.emit(self.laser_pulse_n, self.laser_on_time,
                                    self.laser_off_time, self.laser_x_loc,
                                    self.laser_y_loc, self.offset)
        except ValueError:
            self.logger.logger.exception("Error in Laser window validate settings")
            #TODO raise window with error information so the user can check the data

    def blink_laser(self):
        """
        Function to emit signal with laser blinking settings. Signal is accepted in main.py
        that sends and appropriate request to RPI via worker_raspi.py.
        :return:
        """
        if self.blink_laser_button.text() == "Blink On":
            time_on = int(self.laser_on_time)
            time_off = int(self.laser_off_time)
            self.laser_control_signal.emit("k" + "," + str(time_on) + "," + str(time_off))
            self.blink_laser_button.setText("Blink Off")
        else:
            self.blink_laser_button.setText("Blink On")
            self.laser_control_signal.emit("t")

    def switch_laser(self):
        """
        Function to emit signal to main.py about requested state of laser (ON/OFF).
        Signal is accepted in main.py and the appropriate request is sent via worker_raspi.py.
        :return:
        """
        if self.switch_laser_button.text() == "Laser ON":
            self.laser_control_signal.emit("s")
            self.switch_laser_button.setText("Laser OFF")
        else:
            self.laser_control_signal.emit("l")
            self.switch_laser_button.setText("Laser ON")
