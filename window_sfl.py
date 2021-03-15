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

        # sfl switch button
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
        if self.stampingButton.text() == "Stamping ON":
            self.stamping_switch_signal.emit("start")
            self.stampingButton.setText("Stamping OFF")
        else:
            self.stamping_switch_signal.emit("end")
            self.stampingButton.setText("Stamping ON")
