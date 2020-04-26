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
        self.TEMPLATE_SIZE = 60
        self.stepper_x = 0
        self.stepper_y = 0
        self.camera_enabled = False
        self.find_disks_enabled = False
        self.disk_locations = []
        self.goal_loc = (300, 300)
        self.target_disk_loc = (150, 150)
        self.laser_loc = (100, 100) # default value
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

        # save disk centers button
        self.saveButton = QPushButton('Save img', self)
        self.saveButton.setToolTip('Save imige with disk centers')
        self.saveButton.move(1750,40)
        self.saveButton.clicked.connect(self.save_disk_enabler)

        self.timerShowImage = QtCore.QTimer(self)
        self.timerShowImage.timeout.connect(self.show_image)
        self.timerShowImage.start(10)  # 10 Hz

        self.timerSaveImage = QtCore.QTimer(self)
        self.timerSaveImage.timeout.connect(self.save_disks)
        self.timerSaveImage.start(500)  # 10 Hz

        self.timerAuto = QtCore.QTimer(self)
        self.timerAuto.timeout.connect(self.auto_mode)
        #self.timerAuto.stop()

        # find disks button
        self.findDisksButton = QPushButton('Find disks', self)
        self.findDisksButton.setToolTip('Click to find disks')
        self.findDisksButton.move(1350, 40)
        self.findDisksButton.clicked.connect(self.find_disks)

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

        # get template  button
        self.getTemplateButton = QPushButton('Template', self)
        self.getTemplateButton.setToolTip('Click capture templates')
        self.getTemplateButton.move(1650, 600)
        self.getTemplateButton.clicked.connect(self.get_template)

        # auto  button
        self.autoButton = QPushButton('Auto', self)
        self.autoButton.setToolTip('Automatic mode')
        self.autoButton.move(1650, 800)
        self.autoButton.clicked.connect(self.auto_mode_enabler)

        # shot emulate  button
        self.shotButton = QPushButton('Shot', self)
        self.shotButton.setToolTip('Shot emulate')
        self.shotButton.move(1650, 900)
        self.shotButton.clicked.connect(self.shot)


    def shot(self):
        print("I SHOT!!!!!!!!!!")
        for i in range(self.pulse_number):
            print("shot n.: ", i)
            print(self.pulse_on / 1000)
            self.move_stepper("s")
            time.sleep(self.pulse_on / 1000)
            self.move_stepper("l")
            time.sleep(self.pulse_off / 1000)
            pass
        print("shooting done")
        self.shot_emulate = True

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

    def get_disk_template(self, event, x, y, flags, param):
        pass
        # grab references to the global variables
        # performed
        if event == cv2.EVENT_LBUTTONDOWN:
            self.template_image = copy.deepcopy(self.original_template_image)
            template_to_save = self.original_template_image[y:y + self.TEMPLATE_SIZE,
                               x:x + self.TEMPLATE_SIZE]
            template_to_save = cv2.cvtColor(template_to_save, cv2.COLOR_BGR2GRAY)
            cv2.imwrite(os.path.join("disk_templates", str(datetime.datetime.now()) + ".png"), template_to_save)
        if event == cv2.EVENT_MOUSEMOVE:
            self.template_image = copy.deepcopy(self.original_template_image)
            cv2.rectangle(self.template_image, (x, y), (x + self.TEMPLATE_SIZE, y + self.TEMPLATE_SIZE),  (0, 255, 255))

    def get_template(self):
        self.template_image = cv2_worker.get_image(self.camera)
        self.original_template_image = self.template_image
        cv2.namedWindow("template win")

        cv2.setMouseCallback("template win", self.get_disk_template)
        while True:
            # display the image and wait for a keypress
            cv2.imshow("template win", self.template_image)
            key = cv2.waitKey(1) & 0xFF
            # if the 'c' key is pressed, break from the loop
            if key == ord("c"):
                cv2.destroyAllWindows()
                break

    def save_disks(self):
        if self.save_image_enable:
            cv2.imwrite(os.path.join("25022020","response" + str(datetime.datetime.now()) + ".png"),self.raw_image)

    def save_disk_enabler(self):
        self.save_image_enable = not self.save_image_enable

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

    def move_stepper(self, steps):
        k = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        k.connect((self.RASPI_IP, self.RASPI_PORT))
        k.sendall(bytes(steps, "UTF-8"))
        k.close()

    def recompute_goal(self):
        self.goal_loc = (int(round(self.goal_loc[0] - self.stepper_x / self.STEPPER_CONST)),
                         int(round(self.goal_loc[1] - self.stepper_y / self.STEPPER_CONST)))
        #self.target_disk_loc = (int(round(self.target_disk_loc[0] - self.stepper_x / self.STEPPER_CONST)),
        #                 int(round(self.target_disk_loc[1] - self.stepper_y / self.STEPPER_CONST)))

    def get_steps(self):
        dx = self.goal_loc[0] - self.target_disk_loc[0]
        dy = self.goal_loc[1] - self.target_disk_loc[1]
        if abs(dx) < 3:
            desired_x = self.target_disk_loc[0]
        else:
            if dx > 0:
                desired_x = self.target_disk_loc[0] - np.sign(dx) * 7
            else:
                desired_x = self.target_disk_loc[0] - np.sign(dx) * 7
        if abs(dy) < 3:
            desired_y = self.target_disk_loc[1]
        else:
            if dy > 0:
                desired_y = self.target_disk_loc[1] - np.sign(dy) * 7
            else:
                desired_y = self.target_disk_loc[1] - np.sign(dy) * 7

        self.desired_laser_coord = (desired_x, desired_y)
        self.stepper_x = int((self.STEPPER_CONST * (self.desired_laser_coord[0] - self.laser_loc[0])))
        self.stepper_y = int((self.STEPPER_CONST * (self.desired_laser_coord[1] - self.laser_loc[1])))
        self.logger.setPlainText("Servo steps> x: {}, y: {}".format(str(self.stepper_x), str(self.stepper_y)))
        x_str = "x" + str(self.stepper_x)
        y_str = "y" + str(self.stepper_y)
        self.move_stepper(x_str)
        self.move_stepper(y_str)
        time.sleep(1)
        self.recompute_goal()
        #self.recompute_target_coord()
        #self.find_disks_roi_enabled = True
        self.find_disks_enabled = True


    def set_goal_loc(self):
        self.goal_loc = eval(self.goalCoordInput.text())
        self.logger.setPlainText("goal loc: {}".format(str(self.goal_loc)))

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
            for max_loc in self.disk_locations:
                new_image = cv2.drawMarker(new_image, max_loc, (0, 0, 255), markerType=cv2.MARKER_CROSS, markerSize=20,
                                           thickness=1, line_type=cv2.LINE_AA)

            new_image = cv2.drawMarker(new_image, self.goal_loc, (0, 255, 255), markerType=cv2.MARKER_DIAMOND, markerSize=20,
                                       thickness=1, line_type=cv2.LINE_AA)
            new_image = cv2.drawMarker(new_image, self.target_disk_loc, (255, 255, 0), markerType=cv2.MARKER_TILTED_CROSS,
                                       markerSize=20,
                                       thickness=1, line_type=cv2.LINE_AA)
            new_image = cv2.drawMarker(new_image, self.laser_loc, (255, 0, 0), markerType=cv2.MARKER_STAR,
                                       markerSize=20,
                                       thickness=1, line_type=cv2.LINE_AA)
            new_image = cv2.drawMarker(new_image, self.desired_laser_coord, (0, 255, 0), markerType=cv2.MARKER_STAR,
                                       markerSize=20,
                                       thickness=1, line_type=cv2.LINE_AA)

            cv2.imshow("raw", new_image)
            image = cv2.resize(new_image, (1200, 800))
            height, width, channel = image.shape
            bytes_per_line = 3 * width
            image_for_pixmap = QtGui.QImage(image, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
            self.imageDisplay.setPixmap(QPixmap(image_for_pixmap))
            self.imageDisplay.show()

    def find_disks(self):
        "Function for enabling find disk routine"
        self.find_disks_enabled = True

        # # Create combobox for camera resolution and add items.
        # self.resolutionComboBox = QComboBox(centralWidget)
        # self.resolutionComboBox.setGeometry(QRect(1100, 40, 200, 31))
        # self.resolutionComboBox.setObjectName(("resolutionComboBox"))
        # self.resolutionComboBox.addItem("800 x 600")
        # self.resolutionComboBox.addItem("1920 x 1080")
        # self.resolutionComboBox.currentIndexChanged.connect(self.resolution_changed)