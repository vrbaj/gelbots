"""
This module is implementing the window with sfl settings and control.
"""

from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import QSize, QRect, pyqtSignal
from PyQt5.QtGui import QIntValidator


class SflSettingsWindow(QMainWindow):
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
        super(SflSettingsWindow, self).__init__()
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

        self.int_validator = QIntValidator()

        self.sfl_pulse_label = QLabel(self)
        self.sfl_pulse_label.setGeometry(QRect(10, 0, 80, 20))
        self.sfl_pulse_label.setText("Pulse:")

        self.sfl_pulse_input = QLineEdit(self)
        self.sfl_pulse_input.move(60, 0)
        self.sfl_pulse_input.setFixedWidth(30)
        self.sfl_pulse_input.setValidator(self.int_validator)
        self.sfl_pulse_input.setText(str(self.sfl_pulse))

        #
        self.sfl_light_on_label = QLabel(self)
        self.sfl_light_on_label.setGeometry(QRect(10, 30, 50, 31))
        self.sfl_light_on_label.setText("Light On:")

        self.sfl_light_on_input = QLineEdit(self)
        self.sfl_light_on_input.move(60, 30)
        self.sfl_light_on_input.setFixedWidth(30)
        self.sfl_light_on_input.setValidator(self.int_validator)
        self.sfl_light_on_input.setText(str(self.sfl_light_on))

        #
        self.sfl_radius_label = QLabel(self)
        self.sfl_radius_label.setGeometry(QRect(100, 30, 50, 30))
        self.sfl_radius_label.setText("Radius:")

        self.sfl_radius_input = QLineEdit(self)
        self.sfl_radius_input.move(140, 30)
        self.sfl_radius_input.setFixedWidth(30)
        self.sfl_radius_input.setValidator(self.int_validator)
        self.sfl_radius_input.setText(str(self.sfl_radius))

        self.sfl_light_off_label = QLabel(self)
        self.sfl_light_off_label.setGeometry(QRect(10, 60, 50, 31))
        self.sfl_light_off_label.setText("Light Off:")

        self.sfl_light_off_input = QLineEdit(self)
        self.sfl_light_off_input.move(60, 60)
        self.sfl_light_off_input.setFixedWidth(30)
        self.sfl_light_off_input.setValidator(self.int_validator)
        self.sfl_light_off_input.setText(str(self.sfl_light_off))

        self.sfl_flush_on_label = QLabel(self)
        self.sfl_flush_on_label.setGeometry(QRect(10, 90, 50, 31))
        self.sfl_flush_on_label.setText("Flush On:")

        self.sfl_flush_on_input = QLineEdit(self)
        self.sfl_flush_on_input.move(60, 90)
        self.sfl_flush_on_input.setFixedWidth(30)
        self.sfl_flush_on_input.setValidator(self.int_validator)
        self.sfl_flush_on_input.setText(str(self.sfl_flush_on))

        self.sfl_flush_off_label = QLabel(self)
        self.sfl_flush_off_label.setGeometry(QRect(10, 120, 50, 31))
        self.sfl_flush_off_label.setText("Flush Off:")

        self.sfl_flush_off_input = QLineEdit(self)
        self.sfl_flush_off_input.move(60, 120)
        self.sfl_flush_off_input.setFixedWidth(30)
        self.sfl_flush_off_input.setValidator(self.int_validator)
        self.sfl_flush_off_input.setText(str(self.sfl_flush_off))

        self.stamping_dx_label = QLabel(self)
        self.stamping_dx_label.setGeometry(QRect(200, 0, 100, 25))
        self.stamping_dx_label.setText("Stamping dx:")

        self.stamping_dx_input = QLineEdit(self)
        self.stamping_dx_input.setGeometry(QRect(300, 0, 50, 25))
        self.stamping_dx_input.setValidator(self.int_validator)
        self.stamping_dx_input.setText(str(self.stamping_dx))

        self.stamping_dy_label = QLabel(self)
        self.stamping_dy_label.setGeometry(QRect(200, 25, 100, 25))
        self.stamping_dy_label.setText("Stamping dy:")

        self.stamping_dy_input = QLineEdit(self)
        self.stamping_dy_input.setGeometry(QRect(300, 25, 50, 25))
        self.stamping_dy_input.setValidator(self.int_validator)
        self.stamping_dy_input.setText(str(self.stamping_dy))

        self.stamping_x_delay_label = QLabel(self)
        self.stamping_x_delay_label.setGeometry(QRect(200, 50, 100, 25))
        self.stamping_x_delay_label.setText("Stamping X delay:")

        self.stamping_x_delay_input = QLineEdit(self)
        self.stamping_x_delay_input.setGeometry(QRect(300, 50, 50, 25))
        self.stamping_x_delay_input.setValidator(self.int_validator)
        self.stamping_x_delay_input.setText(str(self.stamping_x_delay))

        self.stamping_y_delay_label = QLabel(self)
        self.stamping_y_delay_label.setGeometry(QRect(200, 75, 100, 25))
        self.stamping_y_delay_label.setText("Stamping Y delay:")

        self.stamping_y_delay_input = QLineEdit(self)
        self.stamping_y_delay_input.setGeometry(QRect(300, 75, 50, 25))
        self.stamping_y_delay_input.setValidator(self.int_validator)
        self.stamping_y_delay_input.setText(str(self.stamping_y_delay))

        self.stamping_light_on_label = QLabel(self)
        self.stamping_light_on_label.setGeometry(QRect(200, 100, 100, 25))
        self.stamping_light_on_label.setText("Stamping light ON:")
        self.stamping_light_on_input = QLineEdit(self)
        self.stamping_light_on_input.setGeometry(QRect(300, 100, 50, 25))
        self.stamping_light_on_input.setValidator(self.int_validator)
        self.stamping_light_on_input.setText(str(self.stamping_light_on))

        self.stamping_light_off_label = QLabel(self)
        self.stamping_light_off_label.setGeometry(QRect(200, 125, 100, 25))
        self.stamping_light_off_label.setText("Stamping light OFF:")

        self.stamping_light_off_input = QLineEdit(self)
        self.stamping_light_off_input.setGeometry(QRect(300, 125, 50, 25))
        self.stamping_light_off_input.setValidator(self.int_validator)
        self.stamping_light_off_input.setText(str(self.stamping_light_off))

        self.stamping_flush_on_label = QLabel(self)
        self.stamping_flush_on_label.setGeometry(QRect(200, 150, 100, 25))
        self.stamping_flush_on_label.setText("Stamping flush ON:")

        self.stamping_flush_on_input = QLineEdit(self)
        self.stamping_flush_on_input.setGeometry(QRect(300, 150, 50, 25))
        self.stamping_flush_on_input.setValidator(self.int_validator)
        self.stamping_flush_on_input.setText(str(self.stamping_flush_on))

        self.stamping_flush_off_label = QLabel(self)
        self.stamping_flush_off_label.setGeometry(QRect(200, 175, 100, 25))
        self.stamping_flush_off_label.setText("Stamping flush OFF:")

        self.stamping_flush_off_input = QLineEdit(self)
        self.stamping_flush_off_input.setGeometry(QRect(300, 175, 50, 25))
        self.stamping_flush_off_input.setValidator(self.int_validator)
        self.stamping_flush_off_input.setText(str(self.stamping_flush_off))

        self.stamping_x_steps_label = QLabel(self)
        self.stamping_x_steps_label.setGeometry(QRect(200, 200, 100, 25))
        self.stamping_x_steps_label.setText("Stamping X steps:")

        self.stamping_x_steps_input = QLineEdit(self)
        self.stamping_x_steps_input.setGeometry(QRect(300, 200, 50, 25))
        self.stamping_x_steps_input.setValidator(self.int_validator)
        self.stamping_x_steps_input.setText(str(self.stamping_x_steps))

        self.stamping_y_steps_label = QLabel(self)
        self.stamping_y_steps_label.setGeometry(QRect(200, 225, 100, 25))
        self.stamping_y_steps_label.setText("Stamping Y steps:")

        self.stamping_y_steps_input = QLineEdit(self)
        self.stamping_y_steps_input.setGeometry(QRect(300, 225, 50, 25))
        self.stamping_y_steps_input.setValidator(self.int_validator)
        self.stamping_y_steps_input.setText(str(self.stamping_y_steps))

        self.stamping_batch_size_label = QLabel(self)
        self.stamping_batch_size_label.setGeometry(QRect(200, 250, 100, 25))
        self.stamping_batch_size_label.setText("Stamping Batch size:")

        self.stamping_batch_size_input = QLineEdit(self)
        self.stamping_batch_size_input.setGeometry(QRect(300, 250, 50, 25))
        self.stamping_batch_size_input.setValidator(self.int_validator)
        self.stamping_batch_size_input.setText(str(self.stamping_batch_size))

        # Apply button
        self.sfl_stamping_button = QPushButton(self)
        self.sfl_stamping_button.setGeometry(QRect(200, 300, 100, 30))
        self.sfl_stamping_button.setToolTip("Click to start stamping")
        self.sfl_stamping_button.setText("Stamping ON")
        self.sfl_stamping_button.clicked.connect(self.switch_stamping)

        # sfl switch button
        self.sfl_switch_button = QPushButton('SFL ON', self)
        self.sfl_switch_button.setToolTip('SFL ON')
        self.sfl_switch_button.move(10, 160)
        self.sfl_switch_button.setFixedHeight(40)
        self.sfl_switch_button.clicked.connect(self.sfl_switch)

        # sfl light switch button
        self.sfl_light_button = QPushButton('Light ON', self)
        self.sfl_light_button.setToolTip('Light ON')
        self.sfl_light_button.move(10, 210)
        self.sfl_light_button.setFixedHeight(40)
        self.sfl_light_button.clicked.connect(self.light_switch)

        # sfl flush switch button
        self.sfl_flush_button = QPushButton('Flush ON', self)
        self.sfl_flush_button.setToolTip('Flush ON')
        self.sfl_flush_button.move(10, 260)
        self.sfl_flush_button.setFixedHeight(40)
        self.sfl_flush_button.clicked.connect(self.flush_switch)

        # sfl pulse button
        self.sfl_pulse_button = QPushButton('Pulse', self)
        self.sfl_pulse_button.setToolTip('Pulse')
        self.sfl_pulse_button.move(10, 310)
        self.sfl_pulse_button.setFixedHeight(40)
        self.sfl_pulse_button.clicked.connect(self.pulse)

        # Apply button
        self.validate_button = QPushButton(self)
        self.validate_button.setGeometry(QRect(10, 360, 60, 30))
        self.validate_button.setToolTip("Click to save settings")
        self.validate_button.setText("Apply")
        self.validate_button.clicked.connect(self.validate_settings)

    def validate_settings(self):
        self.sfl_pulse = int(self.sfl_pulse_input.text())
        self.sfl_flush_on = int(self.sfl_flush_on_input.text())
        self.sfl_flush_off = int(self.sfl_flush_off_input.text())
        self.sfl_light_on = int(self.sfl_light_on_input.text())
        self.sfl_light_off = int(self.sfl_light_off_input.text())
        self.sfl_radius = int(self.sfl_radius_input.text())
        self.stamping_dx = int(self.stamping_dx_input.text())
        self.stamping_dy = int(self.stamping_dy_input.text())
        self.stamping_x_delay = int(self.stamping_x_delay_input.text())
        self.stamping_y_delay = int(self.stamping_y_delay_input.text())
        self.stamping_light_on = int(self.stamping_light_on_input.text())
        self.stamping_light_off = int(self.stamping_light_off_input.text())
        self.stamping_flush_on = int(self.stamping_flush_on_input.text())
        self.stamping_flush_off = int(self.stamping_flush_off_input.text())
        self.stamping_x_steps = int(self.stamping_x_steps_input.text())
        self.stamping_y_steps = int(self.stamping_y_steps_input.text())
        self.stamping_batch_size = int(self.stamping_batch_size_input.text())

        self.change_params.emit(self.sfl_light_on, self.sfl_light_off, self.sfl_flush_on, self.sfl_flush_off,
                                self.sfl_pulse, self.sfl_radius, self.stamping_dx, self.stamping_dy,
                                self.stamping_x_delay, self.stamping_y_delay, self.stamping_light_on,
                                self.stamping_light_off, self.stamping_flush_on, self.stamping_flush_off,
                                self.stamping_x_steps, self.stamping_y_steps, self.stamping_batch_size)

    def pulse(self):
        self.pulse_signal.emit()

    def flush_switch(self):
        self.flush_switch_signal.emit()

    def light_switch(self):
        self.light_switch_signal.emit()

    def sfl_switch(self):
        self.sfl_switch_signal.emit()

    def switch_stamping(self):
        if self.sfl_stamping_button.text() == "Stamping ON":
            self.stamping_switch_signal.emit("start")
            self.sfl_stamping_button.setText("Stamping OFF")
        else:
            self.stamping_switch_signal.emit("end")
            self.sfl_stamping_button.setText("Stamping ON")
