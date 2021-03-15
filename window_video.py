from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton, QFileDialog, QCheckBox
from PyQt5.QtCore import QSize, QRect, Qt, pyqtSignal
from PyQt5.QtGui import QIntValidator


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
        try:
            self.save_interval = int(self.intervalInput.text())
            self.save_namespace = str(self.namespaceInput.text())
            self.save_path = str(self.save_path)
            self.closed.emit(self.save_interval, self.save_namespace, self.save_path)
        except Exception as exp:
            print("error while validating video settings: ", exp)