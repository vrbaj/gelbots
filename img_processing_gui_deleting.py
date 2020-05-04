import sys, socket, copy, os
import cv2_worker
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, QComboBox, QLineEdit, QPushButton
from PyQt5.QtCore import QSize, QRect, Qt
from PyQt5.QtGui import QIntValidator, QPixmap, QDoubleValidator
import cv2
import subprocess
import time, datetime
import numpy as np


class ExampleWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        # set default values
        self.auto_mode_enable = False
        self.shot_emulate = False
        self.RASPI_BUF = 10
        self.STEPPER_CONST = 6.6666666
        self.desired_laser_coord = (0, 0)
        self.find_disks_roi_enabled = False
        self.gray = []
        self.template_image = []
        self.original_template_image = []

        # add pix with found disks
        self.disksDisplay = QLabel(self)
        self.disksDisplay.setGeometry(QRect(1230, 80, 600, 480))
        self.disksDisplay.setPixmap(QPixmap("response2020-01-28 15:08:11.933959.png"))
        self.disksDisplay.show()


        self.timerShowImage = QtCore.QTimer(self)
        self.timerShowImage.timeout.connect(self.show_image)
        self.timerShowImage.start(10)  # 10 Hz

        self.timerAuto = QtCore.QTimer(self)
        self.timerAuto.timeout.connect(self.auto_mode)
        #self.timerAuto.stop()



        # estimate steps button
        self.computeStepsButton = QPushButton('Steps', self)
        self.computeStepsButton.setToolTip('Click to compute steps')
        self.computeStepsButton.move(1350, 600)
        self.computeStepsButton.clicked.connect(self.get_steps)

        # recompute goal button
        self.recomputeGoalButton = QPushButton('New goal', self)
        self.recomputeGoalButton.setToolTip('Click to recompute goal coord')
        self.recomputeGoalButton.move(1450, 600)
        self.recomputeGoalButton.clicked.connect(self.recompute_goal)


        # auto  button
        self.autoButton = QPushButton('Auto', self)
        self.autoButton.setToolTip('Automatic mode')
        self.autoButton.move(1650, 800)
        self.autoButton.clicked.connect(self.auto_mode_enabler)


    def auto_mode(self):
        print("fucking auto ", datetime.datetime.now())
        if self.shot_emulate:
            self.shot_emulate = False
            self.find_disks_enabled = True
            self.show_image()
            self.get_steps()
            self.show_image()
            self.shot()

    def auto_mode_enabler(self):
        if self.timerAuto.isActive():
            self.timerAuto.stop()
        else:
            self.timerAuto.start(1000)
            self.shot_emulate = True


    def recompute_target_coord(self):
        max_distance = 999999
        print("okokokokok>", self.target_disk_loc)
        new_target_loc = self.target_disk_loc
        self.target_disk_loc = (int(round(self.target_disk_loc[0] - self.stepper_x / self.STEPPER_CONST)),
                        int(round(self.target_disk_loc[1] - self.stepper_y / self.STEPPER_CONST)))
        print("WTFWTFWTFWTFWTF ", new_target_loc)
        for disk in self.disk_locations:
            distance = np.linalg.norm(np.asarray(disk) - np.asarray(self.target_disk_loc))
            if distance < max_distance:
                max_distance = distance
                new_target_loc = disk
        self.target_disk_loc = new_target_loc

    def resolution_changed(self):
        """Function to set  resolution of camera image"""
        new_width_value = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
        new_height_value = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
        chosen_resolution = self.resolutionComboBox.currentText()
        print("chosen resolution>", chosen_resolution)
        if chosen_resolution == "1920 x 1080":
            new_width_value = 1920
            new_height_value = 1080
            self.laser_loc = (int(self.laser_loc[0] + 640), int(self.laser_loc[1] + 300))
            self.goal_loc = (int(self.goal_loc[0] + 640), int(self.goal_loc[1] + 300))
            self.target_disk_loc = (int(self.target_disk_loc[0] + 640), int(self.target_disk_loc[1] + 300))
        elif chosen_resolution == "800 x 600":
            new_width_value = 800
            new_height_value = 600
            self.laser_loc = (int(self.laser_loc[0] - 640), int(self.laser_loc[1] - 300))
            self.goal_loc = (int(self.goal_loc[0] - 640), int(self.goal_loc[1] - 300))
            self.target_disk_loc = (int(self.target_disk_loc[0] - 640), int(self.target_disk_loc[1] - 300))
        print(new_width_value)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, new_width_value)
        time.sleep(0.1)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, new_height_value)
        time.sleep(0.1)

    def get_camera_list(self):
        """Wrapping function to get camera list"""
        return cv2_worker.get_available_cameras()

    def refresh_camera_list(self):
        """Function for refreshing cameraComboBox"""
        camera_list = self.get_camera_list()
        for idx, item in enumerate(camera_list):
            self.cameraComboBox.addItem(str(idx))

    def show_image(self):
        """Function for showing camera image in the GUI"""
        if self.camera_enabled:
            new_image = cv2_worker.get_image(self.camera)
            self.raw_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2GRAY)
            # print(new_image.shape)
            i = 0
            if self.find_disks_enabled:
                print("111111")
                gray = cv2.cvtColor(new_image, cv2.COLOR_BGR2GRAY)

                self.disk_locations = cv2_worker.find_disks(gray)
                print("disks:", self.disk_locations)
                for max_loc in self.disk_locations:

                    print("max loc", max_loc)
                    gray = cv2.drawMarker(gray, max_loc, (255, 255, 255), markerType=cv2.MARKER_CROSS, markerSize=20,
                                          thickness=1, line_type=cv2.LINE_AA)

                    cv2.putText(gray, str(max_loc), max_loc , cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 2, cv2.LINE_AA)
                gray = cv2.drawMarker(gray, self.goal_loc, (0, 0, 255), markerType=cv2.MARKER_STAR, markerSize=20,
                                      thickness=1, line_type=cv2.LINE_AA)
                cv2.imshow("disks and their locations", gray)
                self.gray = gray
                #cv2.imwrite("response" + str(datetime.datetime.now()) + ".png", gray)
                height, width = gray.shape[:2]
                print("height: ", height, " width:", width)
                bytes_per_line = width
                image_for_pixmap = QtGui.QImage(gray, width, height, QtGui.QImage.Format_Grayscale8)
                self.disksDisplay.setPixmap(QPixmap.fromImage(image_for_pixmap))
                self.disksDisplay.show()
                self.find_disks_enabled = False
                self.recompute_target_coord()
            if self.find_disks_roi_enabled:
                gray = cv2.cvtColor(new_image, cv2.COLOR_BGR2GRAY)
                self.disk_locations = cv2_worker.find_disks_roi(gray, self.target_disk_loc)
                print("disks:", self.disk_locations)
                for max_loc in self.disk_locations:
                    print("max loc", max_loc)
                    gray = cv2.drawMarker(gray, max_loc, (255, 255, 255), markerType=cv2.MARKER_CROSS, markerSize=20,
                                          thickness=1, line_type=cv2.LINE_AA)

                    cv2.putText(gray, str(max_loc), max_loc, cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 2,
                                cv2.LINE_AA)
                gray = cv2.drawMarker(gray, self.goal_loc, (0, 0, 255), markerType=cv2.MARKER_STAR, markerSize=20,
                                      thickness=1, line_type=cv2.LINE_AA)
                cv2.imwrite("response" + str(datetime.datetime.now()) + ".png", gray)
                cv2.imshow("disks and their locations", gray)
                height, width = gray.shape[:2]
                print("height: ", height, " width:", width)
                bytes_per_line = width
                image_for_pixmap = QtGui.QImage(gray, width, height, QtGui.QImage.Format_Grayscale8)
                self.disksDisplay.setPixmap(QPixmap.fromImage(image_for_pixmap))
                self.disksDisplay.show()
                self.find_disks_roi_enabled = False
                #self.recompute_target_coord()


            cv2.imshow("raw", new_image)
            image = cv2.resize(new_image, (1200, 800))
            height, width, channel = image.shape
            bytes_per_line = 3 * width
            image_for_pixmap = QtGui.QImage(image, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
            self.imageDisplay.setPixmap(QPixmap(image_for_pixmap))
            self.imageDisplay.show()

        # # Create combobox for camera resolution and add items.
        # self.resolutionComboBox = QComboBox(centralWidget)
        # self.resolutionComboBox.setGeometry(QRect(1100, 40, 200, 31))
        # self.resolutionComboBox.setObjectName(("resolutionComboBox"))
        # self.resolutionComboBox.addItem("800 x 600")
        # self.resolutionComboBox.addItem("1920 x 1080")
        # self.resolutionComboBox.currentIndexChanged.connect(self.resolution_changed)