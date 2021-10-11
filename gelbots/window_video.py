"""
This module is implementing the window with video savings settings.
"""

from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, \
    QPushButton, QFileDialog, QCheckBox, QMessageBox
from PyQt5.QtCore import QSize, QRect, Qt, pyqtSignal
from PyQt5.QtGui import QIntValidator

from error_handling import ErrorLogger


class VideoSettingsWindow(QMainWindow):
    """
    This class is implementing the Video saving setting window that contains all settings
    related to saving images.
    """

    # pylint: disable=too-many-instance-attributes
    # 18 is reasonable in this case.

    closed = pyqtSignal(int, str, str)

    def __init__(self, interval, namespace, path):
        super().__init__()
        self.logger = ErrorLogger()
        self.int_validator = QIntValidator()

        # set variables
        self.save_interval = interval
        self.save_namespace = namespace
        self.save_path = path
        self.roi_enabled = False

        # labels
        self.interval_label = QLabel(self)
        self.seconds_label = QLabel(self)
        self.path_actual_label = QLabel(self)
        self.namespace_label = QLabel(self)
        self.path_label = QLabel(self)
        self.__init_labels()

        # check box to save ROI
        self.roi_checkbox = QCheckBox(self)
        self.roi_checkbox.setText("save roi")
        self.roi_checkbox.setToolTip("Click to save only ROI")
        self.roi_checkbox.setGeometry(QRect(200, 30, 100, 25))
        self.roi_checkbox.setLayoutDirection(Qt.RightToLeft)

        # set window properties
        self.setMinimumSize(QSize(800, 120))
        self.setWindowTitle("Video settings")

        # Create width input box
        self.interval_input = QLineEdit(self)
        self.interval_input.setGeometry(QRect(90, 10, 30, 20))
        self.interval_input.setText(str(self.save_interval))
        self.interval_input.setValidator(self.int_validator)

        # Create namespace input box
        self.namespace_input = QLineEdit(self)
        self.namespace_input.setGeometry(QRect(90, 40, 85, 20))
        self.namespace_input.setText(self.save_namespace)

        # Path button
        self.path_button = QPushButton(self)
        self.path_button.setGeometry(QRect(90, 70, 30, 20))
        self.path_button.setToolTip("Click to choose directory")
        self.path_button.setText("...")
        self.path_button.clicked.connect(self.get_video_path)

        # Apply button
        self.validate_button = QPushButton(self)
        self.validate_button.setGeometry(QRect(739, 90, 60, 30))
        self.validate_button.setToolTip("Click to save settings")
        self.validate_button.setText("Apply")
        self.validate_button.clicked.connect(self.validate_settings)

        # set ROI button
        self.roi_button = QPushButton(self)
        self.roi_button.setGeometry(QRect(739, 40, 60, 30))
        self.roi_button.setToolTip("Click to set ROI for saving video")
        self.roi_button.setText("ROI")
        self.roi_button.clicked.connect(self.roi_pushed)

    def __init_labels(self):
        # Interval label
        self.interval_label.setGeometry(QRect(10, 5, 80, 31))
        self.interval_label.setText("Saving interval:")
        # path actual label
        self.path_actual_label.setGeometry(QRect(130, 65, 650, 31))
        self.path_actual_label.setText(self.save_path)
        # Interval seconds label
        self.seconds_label.setGeometry(QRect(125, 5, 80, 31))
        self.seconds_label.setText("[s]")
        # Namespace label
        self.namespace_label.setGeometry(QRect(30, 35, 80, 31))
        self.namespace_label.setText("Files name:")
        # Path label
        self.path_label.setGeometry(QRect(50, 65, 80, 31))
        self.path_label.setText("Path:")

    def roi_pushed(self):
        """Function to allow saving only ROI image."""
        self.roi_enabled = True

    def get_video_path(self):
        """Function to get the path to directory, where the images for video will be saved."""
        file = str(QFileDialog.getExistingDirectory(self, "Select directory"))
        self.save_path = file
        self.path_actual_label.setText(file)

    def validate_settings(self):
        """
        This function converts the text from input boxes to numbers and emit
        signal to gelbots.py where is the config file overwritten.
        :return:
        """
        try:
            self.save_interval = int(self.interval_input.text())
            self.save_namespace = str(self.namespace_input.text())
            self.save_path = str(self.save_path)
            self.closed.emit(self.save_interval, self.save_namespace, self.save_path)
        except ValueError:
            self.logger.logger.exception("Error in Video window validate settings")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText("Video params are not valid.")
            msg.setWindowTitle("Error")
            msg.exec_()
