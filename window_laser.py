from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import QSize, QRect, pyqtSignal
from PyQt5.QtGui import QIntValidator, QFont


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
