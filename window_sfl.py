"""
This module is implementing the window with sfl settings and control.
"""

from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import QSize, QRect, pyqtSignal
from PyQt5.QtGui import QIntValidator

from gelbots_dataclasses import SflParams


class SflSettingsWindow(QMainWindow):
    """
    This class is implementing the Sfl window that contains all settings
    related to sfl and stamping.
    """

    # pylint: disable=too-many-instance-attributes
    # 42 is reasonable in this case.

    # pylint: disable=too-many-statements
    # 51 is reasonable in this case

    change_params = pyqtSignal(object)
    pulse_signal = pyqtSignal()
    flush_switch_signal = pyqtSignal()
    light_switch_signal = pyqtSignal()
    stamping_switch_signal = pyqtSignal(str)
    sfl_switch_signal = pyqtSignal()

    def __init__(self, sfl_params: SflParams):
        super().__init__()
        self.sfl_params = sfl_params
        self.int_validator = QIntValidator()

        # set window properties
        self.setMinimumSize(QSize(450, 500))
        self.setWindowTitle("SFL settings")

        # sfl labels
        self.sfl_pulse_label = QLabel(self)
        self.sfl_light_on_label = QLabel(self)
        self.sfl_radius_label = QLabel(self)
        self.sfl_light_off_label = QLabel(self)
        self.sfl_flush_on_label = QLabel(self)
        self.sfl_flush_off_label = QLabel(self)
        self.sfl_stamping_dx_label = QLabel(self)
        self.__init_sfl_labels()

        # stamping labels
        self.stamping_dy_label = QLabel(self)
        self.stamping_x_delay_label = QLabel(self)
        self.stamping_y_delay_label = QLabel(self)
        self.stamping_light_on_label = QLabel(self)
        self.stamping_light_off_label = QLabel(self)
        self.stamping_flush_on_label = QLabel(self)
        self.stamping_flush_off_label = QLabel(self)
        self.stamping_x_steps_label = QLabel(self)
        self.stamping_y_steps_label = QLabel(self)
        self.stamping_batch_size_label = QLabel(self)
        self.__init_stamping_labels()

        # sfl inputs
        self.sfl_pulse_input = QLineEdit(self)
        self.sfl_light_on_input = QLineEdit(self)
        self.sfl_radius_input = QLineEdit(self)
        self.sfl_light_off_input = QLineEdit(self)
        self.sfl_flush_on_input = QLineEdit(self)
        self.sfl_flush_off_input = QLineEdit(self)
        self.__init_sfl_inputs()
        # stamping inputs
        self.stamping_dx_input = QLineEdit(self)
        self.stamping_dy_input = QLineEdit(self)
        self.stamping_x_delay_input = QLineEdit(self)
        self.stamping_y_delay_input = QLineEdit(self)
        self.stamping_light_on_input = QLineEdit(self)
        self.stamping_light_off_input = QLineEdit(self)
        self.stamping_flush_on_input = QLineEdit(self)
        self.stamping_flush_off_input = QLineEdit(self)
        self.stamping_x_steps_input = QLineEdit(self)
        self.stamping_y_steps_input = QLineEdit(self)
        self.stamping_batch_size_input = QLineEdit(self)
        self.__init_stamping_inputs()

        # buttons
        self.sfl_stamping_button = QPushButton(self)
        self.sfl_switch_button = QPushButton('SFL ON', self)
        self.sfl_light_button = QPushButton('Light ON', self)
        self.sfl_flush_button = QPushButton('Flush ON', self)
        self.sfl_pulse_button = QPushButton('Pulse', self)
        self.sfl_validate_button = QPushButton(self)
        self.__init_buttons()

    def __init_sfl_labels(self):
        """
        Function to init labels associated with SLF.
        :return:
        """
        # pulse label
        self.sfl_pulse_label.setGeometry(QRect(10, 0, 80, 20))
        self.sfl_pulse_label.setText("Pulse:")
        # sfl light on label
        self.sfl_light_on_label.setGeometry(QRect(10, 30, 50, 31))
        self.sfl_light_on_label.setText("Light On:")
        # sfl radius label
        self.sfl_radius_label.setGeometry(QRect(100, 30, 50, 30))
        self.sfl_radius_label.setText("Radius:")
        # sfl light off label
        self.sfl_light_off_label.setGeometry(QRect(10, 60, 50, 31))
        self.sfl_light_off_label.setText("Light Off:")
        # sfl flush on label
        self.sfl_flush_on_label.setGeometry(QRect(10, 90, 50, 31))
        self.sfl_flush_on_label.setText("Flush On:")
        # sfl flush off label
        self.sfl_flush_off_label.setGeometry(QRect(10, 120, 50, 31))
        self.sfl_flush_off_label.setText("Flush Off:")
        # sfl stamping dx label
        self.sfl_stamping_dx_label.setGeometry(QRect(200, 0, 100, 25))
        self.sfl_stamping_dx_label.setText("Stamping dx:")

    def __init_stamping_labels(self):
        """
        Function to init all labels associated with stamping.
        :return:
        """
        # sfl stamping dy label
        self.stamping_dy_label.setGeometry(QRect(200, 25, 100, 25))
        self.stamping_dy_label.setText("Stamping dy:")
        # sfl stamping x delay label
        self.stamping_x_delay_label.setGeometry(QRect(200, 50, 100, 25))
        self.stamping_x_delay_label.setText("Stamping X delay:")
        # sfl stamping y delay label
        self.stamping_y_delay_label.setGeometry(QRect(200, 75, 100, 25))
        self.stamping_y_delay_label.setText("Stamping Y delay:")
        # sfl stamping light on label
        self.stamping_light_on_label.setGeometry(QRect(200, 100, 100, 25))
        self.stamping_light_on_label.setText("Stamping light ON:")
        # sfl stamping light off label
        self.stamping_light_off_label.setGeometry(QRect(200, 125, 100, 25))
        self.stamping_light_off_label.setText("Stamping light OFF:")
        # sfl stamping flush on label
        self.stamping_flush_on_label.setGeometry(QRect(200, 150, 100, 25))
        self.stamping_flush_on_label.setText("Stamping flush ON:")
        # sfl stamping flush off label
        self.stamping_flush_off_label.setGeometry(QRect(200, 175, 100, 25))
        self.stamping_flush_off_label.setText("Stamping flush OFF:")
        # sfl stamping x steps label
        self.stamping_x_steps_label.setGeometry(QRect(200, 200, 100, 25))
        self.stamping_x_steps_label.setText("Stamping X steps:")
        # sfl stamping y steps label
        self.stamping_y_steps_label.setGeometry(QRect(200, 225, 100, 25))
        self.stamping_y_steps_label.setText("Stamping Y steps:")
        # sfl stamping batch size
        self.stamping_batch_size_label.setGeometry(QRect(200, 250, 100, 25))
        self.stamping_batch_size_label.setText("Stamping Batch size:")

    def __init_sfl_inputs(self):
        """
        This function initializes all sfl inputs.
        :return:
        """
        # sfl pulse input
        self.sfl_pulse_input.move(60, 0)
        self.sfl_pulse_input.setFixedWidth(30)
        self.sfl_pulse_input.setValidator(self.int_validator)
        self.sfl_pulse_input.setText(str(self.sfl_params.sfl_pulse))
        # sfl light on input
        self.sfl_light_on_input.move(60, 30)
        self.sfl_light_on_input.setFixedWidth(30)
        self.sfl_light_on_input.setValidator(self.int_validator)
        self.sfl_light_on_input.setText(str(self.sfl_params.sfl_light_on))
        # sfl radius input
        self.sfl_radius_input.move(140, 30)
        self.sfl_radius_input.setFixedWidth(30)
        self.sfl_radius_input.setValidator(self.int_validator)
        self.sfl_radius_input.setText(str(self.sfl_params.sfl_radius))
        # sfl light off input
        self.sfl_light_off_input.move(60, 60)
        self.sfl_light_off_input.setFixedWidth(30)
        self.sfl_light_off_input.setValidator(self.int_validator)
        self.sfl_light_off_input.setText(str(self.sfl_params.sfl_light_off))
        # sfl flush on input
        self.sfl_flush_on_input.move(60, 90)
        self.sfl_flush_on_input.setFixedWidth(30)
        self.sfl_flush_on_input.setValidator(self.int_validator)
        self.sfl_flush_on_input.setText(str(self.sfl_params.sfl_flush_on))
        # sfl flush off input
        self.sfl_flush_off_input.move(60, 120)
        self.sfl_flush_off_input.setFixedWidth(30)
        self.sfl_flush_off_input.setValidator(self.int_validator)
        self.sfl_flush_off_input.setText(str(self.sfl_params.sfl_flush_off))

    def __init_stamping_inputs(self):
        """
        This function initializes all stamping inputs.
        :return:
        """
        # sfl stamping dx input
        self.stamping_dx_input.setGeometry(QRect(300, 0, 50, 25))
        self.stamping_dx_input.setValidator(self.int_validator)
        self.stamping_dx_input.setText(str(self.sfl_params.stamping_dx))
        # sfl stamping dy input
        self.stamping_dy_input.setGeometry(QRect(300, 25, 50, 25))
        self.stamping_dy_input.setValidator(self.int_validator)
        self.stamping_dy_input.setText(str(self.sfl_params.stamping_dy))
        # sfl stamping x delay input
        self.stamping_x_delay_input.setGeometry(QRect(300, 50, 50, 25))
        self.stamping_x_delay_input.setValidator(self.int_validator)
        self.stamping_x_delay_input.setText(str(self.sfl_params.stamping_x_delay))
        # sfl stamping y delay input
        self.stamping_y_delay_input.setGeometry(QRect(300, 75, 50, 25))
        self.stamping_y_delay_input.setValidator(self.int_validator)
        self.stamping_y_delay_input.setText(str(self.sfl_params.stamping_y_delay))
        # sfl stamping light on input
        self.stamping_light_on_input.setGeometry(QRect(300, 100, 50, 25))
        self.stamping_light_on_input.setValidator(self.int_validator)
        self.stamping_light_on_input.setText(str(self.sfl_params.stamping_light_on))
        # sfl stamping light off input
        self.stamping_light_off_input.setGeometry(QRect(300, 125, 50, 25))
        self.stamping_light_off_input.setValidator(self.int_validator)
        self.stamping_light_off_input.setText(str(self.sfl_params.stamping_light_off))
        # sfl stamping flush on input
        self.stamping_flush_on_input.setGeometry(QRect(300, 150, 50, 25))
        self.stamping_flush_on_input.setValidator(self.int_validator)
        self.stamping_flush_on_input.setText(str(self.sfl_params.stamping_flush_on))
        # sfl stamping flush off input
        self.stamping_flush_off_input.setGeometry(QRect(300, 175, 50, 25))
        self.stamping_flush_off_input.setValidator(self.int_validator)
        self.stamping_flush_off_input.setText(str(self.sfl_params.stamping_flush_off))
        # sfl stamping x steps input
        self.stamping_x_steps_input.setGeometry(QRect(300, 200, 50, 25))
        self.stamping_x_steps_input.setValidator(self.int_validator)
        self.stamping_x_steps_input.setText(str(self.sfl_params.stamping_x_steps))
        # sfl stamping y steps input
        self.stamping_y_steps_input.setGeometry(QRect(300, 225, 50, 25))
        self.stamping_y_steps_input.setValidator(self.int_validator)
        self.stamping_y_steps_input.setText(str(self.sfl_params.stamping_y_steps))
        # sfl stamping batch size input
        self.stamping_batch_size_input.setGeometry(QRect(300, 250, 50, 25))
        self.stamping_batch_size_input.setValidator(self.int_validator)
        self.stamping_batch_size_input.setText(str(self.sfl_params.stamping_batch_size))

    def __init_buttons(self):
        # sfl stamping button
        self.sfl_stamping_button.setGeometry(QRect(200, 300, 100, 30))
        self.sfl_stamping_button.setToolTip("Click to start stamping")
        self.sfl_stamping_button.setText("Stamping ON")
        self.sfl_stamping_button.clicked.connect(self.switch_stamping)
        # sfl switch button
        self.sfl_switch_button.setToolTip('SFL ON')
        self.sfl_switch_button.move(10, 160)
        self.sfl_switch_button.setFixedHeight(40)
        self.sfl_switch_button.clicked.connect(self.sfl_switch)
        # sfl light switch button
        self.sfl_light_button.setToolTip('Light ON')
        self.sfl_light_button.move(10, 210)
        self.sfl_light_button.setFixedHeight(40)
        self.sfl_light_button.clicked.connect(self.light_switch)
        # sfl flush switch button
        self.sfl_flush_button.setToolTip('Flush ON')
        self.sfl_flush_button.move(10, 260)
        self.sfl_flush_button.setFixedHeight(40)
        self.sfl_flush_button.clicked.connect(self.flush_switch)
        # sfl pulse button
        self.sfl_pulse_button.setToolTip('Pulse')
        self.sfl_pulse_button.move(10, 310)
        self.sfl_pulse_button.setFixedHeight(40)
        self.sfl_pulse_button.clicked.connect(self.pulse)
        # Apply button
        self.sfl_validate_button.setGeometry(QRect(10, 360, 60, 30))
        self.sfl_validate_button.setToolTip("Click to save settings")
        self.sfl_validate_button.setText("Apply")
        self.sfl_validate_button.clicked.connect(self.validate_settings)

    def validate_settings(self):
        """
        This function converts the text from input boxes to numbers and emit
        signal to main.py where is the config file overwritten.
        :return:
        """
        try:
            self.sfl_params.sfl_pulse = int(self.sfl_pulse_input.text())
            self.sfl_params.sfl_flush_on = int(self.sfl_flush_on_input.text())
            self.sfl_params.sfl_flush_off = int(self.sfl_flush_off_input.text())
            self.sfl_params.sfl_light_on = int(self.sfl_light_on_input.text())
            self.sfl_params.sfl_light_off = int(self.sfl_light_off_input.text())
            self.sfl_params.sfl_radius = int(self.sfl_radius_input.text())
            self.sfl_params.stamping_dx = int(self.stamping_dx_input.text())
            self.sfl_params.stamping_dy = int(self.stamping_dy_input.text())
            self.sfl_params.stamping_x_delay = int(self.stamping_x_delay_input.text())
            self.sfl_params.stamping_y_delay = int(self.stamping_y_delay_input.text())
            self.sfl_params.stamping_light_on = int(self.stamping_light_on_input.text())
            self.sfl_params.stamping_light_off = int(self.stamping_light_off_input.text())
            self.sfl_params.stamping_flush_on = int(self.stamping_flush_on_input.text())
            self.sfl_params.stamping_flush_off = int(self.stamping_flush_off_input.text())
            self.sfl_params.stamping_x_steps = int(self.stamping_x_steps_input.text())
            self.sfl_params.stamping_y_steps = int(self.stamping_y_steps_input.text())
            self.sfl_params.stamping_batch_size = int(self.stamping_batch_size_input.text())
            self.change_params.emit(self.sfl_params)
        except ValueError:
            self.logger.logger.exception("Error in Sfl window validate settings")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText("Sfl params are not numbers")
            msg.setWindowTitle("Error")
            msg.exec_()

    def pulse(self):
        """
        Function to emit signal to main.py to perform sfl pulse.
        :return:
        """
        self.pulse_signal.emit()

    def flush_switch(self):
        """
        Function to emit signal to main.py to switch flush.
        :return:
        """
        self.flush_switch_signal.emit()

    def light_switch(self):
        """
        Function to emit signal to main.py to switch light.
        :return:
        """
        self.light_switch_signal.emit()

    def sfl_switch(self):
        """
        Function to emit signal to main.py to start sfl.
        :return:
        """
        self.sfl_switch_signal.emit()

    def switch_stamping(self):
        """
        Function to emit signal to main.py to start sfl stamping mode.
        :return:
        """
        if self.sfl_stamping_button.text() == "Stamping ON":
            self.stamping_switch_signal.emit("start")
            self.sfl_stamping_button.setText("Stamping OFF")
        else:
            self.stamping_switch_signal.emit("end")
            self.sfl_stamping_button.setText("Stamping ON")
