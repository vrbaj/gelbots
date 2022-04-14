import configparser
import socket
import sys
import time
from copy import deepcopy

import cv2
import keyboard
import numpy as np
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QLabel, QWidget, QComboBox,\
    QLineEdit, QPushButton, QFrame, QCheckBox, QRubberBand, QProgressDialog
from PyQt5.QtCore import QSize, QRect, Qt, QPoint
from PyQt5.QtGui import QIntValidator, QPixmap, QDoubleValidator

from gelbots.error_handling import exception_handler, ErrorLogger
from gelbots.qt_factory import QtFactory
from gelbots import worker_raspi, window_laser, disk_core2 as disk_core, window_video, worker_camera, window_sfl, \
    window_formation
from gelbots.gelbots_dataclasses import LaserParams, SflParams, CameraParams
from gelbots.gelbots_utils import draw_marks, read_config


class GelbotsWindow(QMainWindow):

    CONFIG_FILE_NAME = "config.ini"
    PIXMAP_HEIGHT = int(1 * 720)
    PIXMAP_WIDTH = int(1280)

    # pylint: disable = E1101

    def __init__(self, progress):
        progress.setValue(30)

        try:
            QMainWindow.__init__(self)

            self.logger = ErrorLogger(__name__)
            self.hook = keyboard.on_press(self.keyboard_event_received)
            self.draw_roi = False
            # variables
            self.image_to_display = []
            self.gray_image = []
            self.move_laser_enabled = False
            self.set_goal_enabled = False
            self.set_disk_enabled = False
            self.set_sfl_enabled = False
            self.add_disk_formation = False
            self.add_target_formation = False
            self.draw_marks_enabled = True
            self.set_laser_enabled = False
            self.automode_enabled = False
            self.checker_memory = False
            self.target_list = []
            self.disk_list = []
            progress.setLabelText("Reading config")
            progress.setValue(40)
            try:
                self.config = configparser.RawConfigParser()
                self.config.read("config.ini")
            except Exception as ex:
                print(ex)
            try:
                #TODO this TRY bullshit to function
                config_data = read_config()
                self.laser_params = config_data["laser"]
                self.sfl_params = config_data["sfl"]
                self.camera_params = config_data["camera"]
                self.servo_params = config_data["steppers"]
                self.servo_params.waiting_time = 2000


            except Exception as ex:
                print(ex)
            # set window properties
            central_widget = QWidget(self)
            self.setMinimumSize(QSize(1800, 1030))
            self.setWindowTitle("Gelbot aimbot v1")
            self.setCentralWidget(central_widget)
            # Set validators
            self.int_validator = QIntValidator()
            self.double_validator = QDoubleValidator()
            progress.setLabelText("Initializing graphic..")
            progress.setValue(50)
            # labels
            self.camera_label = QtFactory.get_object(QLabel, central_widget, text="Camera:", geometry=QRect(10, 5, 80, 31))
            self.camera_width_label = QtFactory.get_object(QLabel, central_widget, text="Width:", geometry=QRect(120, 5, 80, 31))
            self.camera_height_label = QtFactory.get_object(QLabel, central_widget, text="Height:", geometry=QRect(200, 5, 80, 31))
            self.camera_fps_label = QtFactory.get_object(QLabel, central_widget, text="FPS:", geometry=QRect(280, 5, 80, 31))
            self.camera_exposure_label = QtFactory.get_object(QLabel, central_widget, text="Exposure:", geometry=QRect(350, 5, 80, 31))
            self.camera_gain_label = QtFactory.get_object(QLabel, central_widget, text="Gain:", geometry=QRect(450, 5, 80, 31))
            self.steppers_x_label = QtFactory.get_object(QLabel, central_widget, text="Manual steps X:", geometry=QRect(1600, 5, 80, 31))
            self.camera_brightness_label = QtFactory.get_object(QLabel, central_widget, text="Brightness:", geometry=QRect(540, 5, 80, 31))
            self.steppers_y_label = QtFactory.get_object(QLabel, central_widget, text="Manual steps Y:", geometry=QRect(1600, 35, 80, 31))
            self.mag_label = QtFactory.get_object(QLabel, central_widget, text="Magnification", geometry=QRect(10, 30, 80, 25))
            # buttons
            self.laser_button = QtFactory.get_object(QPushButton, central_widget,
                                                     text="Laser ON", tooltip="Laser switch",
                                                     position=(1750, 35), func=self.laser_switch)
            self.run_camera_button = QtFactory.get_object(QPushButton, central_widget, text="Run camera",
                                                          tooltip="Click to switch camera", position=(650, 10),
                                                          func=self.run_camera)
            self.red_button = QtFactory.get_object(QPushButton, central_widget, text="Red button",
                                                   tooltip="Click to stop all raspberry processes",
                                                   position=(1000, 30), func=self.red_button_function)
            self.auto_mode_button = QtFactory.get_object(QPushButton, central_widget,
                                                         text="Auto ON", tooltip="Auto mode switch",
                                                         position=(1750, 5), func=self.automode)
            self.save_video_button = QtFactory.get_object(QPushButton, central_widget,
                                                          text="Video settings", tooltip="Click to set video settings",
                                                          position=(1300, 30), func=self.save_video_settings)
            self.laser_settings_button = QtFactory.get_object(QPushButton, central_widget, text="Laser settings",
                                                              tooltip="Click to set laser settings",
                                                              position=(1750, 150), func=self.show_laser_settings)
            self.sfl_settings_button = QtFactory.get_object(QPushButton, central_widget, text="SFL settings",
                                                            tooltip="Click to set SFL settings",
                                                            position=(1750, 200), func=self.show_sfl_settings)
            self.find_disks_button = QtFactory.get_object(QPushButton, central_widget, text="Find disks",
                                                          tooltip="Click to find disks", position=(1300, 5),
                                                          func=self.find_disks)
            self.formation_window_button = QtFactory.get_object(QPushButton, central_widget, text="Formation editor",
                                                                tooltip="Click to setup formation",
                                                                position=(1750, 300), func=self.show_formation_window)
            # inputs
            self.camera_width_input = QtFactory.get_object(QLineEdit, central_widget,
                                                           text=self.camera_params.width_value, position=(155, 10),
                                                           validator="int", func=self.width_edited)
            self.camera_height_input = QtFactory.get_object(QLineEdit, central_widget,
                                                            text=self.camera_params.height_value, position=(235, 10),
                                                            validator="int", func=self.height_edited)
            self.camera_fps_input = QtFactory.get_object(QLineEdit, central_widget, text=self.camera_params.fps_value,
                                                         position=(305, 10), validator="int", func=self.fps_edited)
            self.camera_exposure_input = QtFactory.get_object(QLineEdit, central_widget, position=(400, 10),
                                                              text=self.camera_params.exposure_value, validator="int",
                                                              func=self.exposure_edited)
            self.camera_gain_input = QtFactory.get_object(QLineEdit, central_widget, position=(480, 10),
                                                          text=self.camera_params.gain_value, validator="float",
                                                          func=self.gain_edited)
            self.camera_brightness_input = QtFactory.get_object(QLineEdit, central_widget, position=(600, 10),
                                                                text=self.camera_params.brightness_value,
                                                                validator="float", func=self.brightness_edited)
            self.steppers_x_input = QtFactory.get_object(QLineEdit, central_widget, text=self.servo_params.steppers_x,
                                                         position=(1680, 10), validator="int",
                                                         func=self.steppers_x_edited)
            self.steppers_y_input = QtFactory.get_object(QLineEdit, central_widget, text=self.servo_params.steppers_y,
                                                         position=(1680, 40), validator="int",
                                                         func=self.steppers_y_edited)
            # checkbox
            self.move_laser_checkbox = QtFactory.get_object(QCheckBox, central_widget, geometry=QRect(850, 30, 100, 25),
                                                            func=self.laser_checkbox_click, text="Move laser",
                                                            tooltip="Click to image to move laser to desired position")
            self.set_sfl_checkbox = QtFactory.get_object(QCheckBox, central_widget, geometry=QRect(1000, 5, 100, 25),
                                                         func=self.set_sfl_checkbox_click, text="Set sfl",
                                                         tooltip="Click to image to set sfl position")
            self.set_disk_formation_checkbox = QtFactory.get_object(QCheckBox, central_widget, text="Add disk",
                                                                    geometry=QRect(1800, 500, 100, 25),
                                                                    tooltip="Click to image to add disk to formation",
                                                                    func=self.disk_formation_checkbox_click)
            self.set_disk_formation_checkbox = QtFactory.get_object(QCheckBox, central_widget, text="Add target",
                                                                    geometry=QRect(1800, 530, 100, 25),
                                                                    tooltip="Click to image to add target to formation",
                                                                    func=self.goal_formation_checkbox_click)
            self.save_video_checkbox = QtFactory.get_object(QCheckBox, central_widget, geometry=QRect(850, 5, 100, 25),
                                                            text="Save video", func=self.save_video_checkbox_click,
                                                            tooltip="Click to save/stop saving the video on the disk")
            self.set_laser_checkbox = QtFactory.get_object(QCheckBox, central_widget, geometry=QRect(1100, 35, 100, 25),
                                                           text="Set laser", func=self.set_laser_checkbox_click,
                                                           tooltip="Click to image to set laser position")
            self.draw_marks_checkbox = QtFactory.get_object(QCheckBox, central_widget, geometry=QRect(1100, 5, 100, 25),
                                                            text="Draw marks", func=self.draw_marks_checkbox_click,
                                                            tooltip="Click to draw marks into image", checked=True)
            self.mag_4_checkbox = QtFactory.get_object(QCheckBox, central_widget, geometry=QRect(70, 30, 40, 25),
                                                       text="4x", tooltip="Click to set magnification",
                                                       func=lambda: self.mag_click(self.mag_4_checkbox))
            self.mag_10_checkbox = QtFactory.get_object(QCheckBox, central_widget, geometry=QRect(110, 30, 40, 25),
                                                        text="10x", tooltip="Click to set magnification",
                                                        func=lambda: self.mag_click(self.mag_10_checkbox))
            self.mag_20_checkbox = QtFactory.get_object(QCheckBox, central_widget, geometry=QRect(150, 30, 40, 25),
                                                        text="20x", tooltip="Click to set magnification",
                                                        func=lambda: self.mag_click(self.mag_20_checkbox))
            self.mag_40_checkbox = QtFactory.get_object(QCheckBox, central_widget, geometry=QRect(190, 30, 40, 25),
                                                        text="40x", tooltip="Click to set magnification",
                                                        func=lambda: self.mag_click(self.mag_40_checkbox))


            # Create combobox and add items.
            self.camera_combo_box = QComboBox(central_widget)
            self.camera_combo_box.setGeometry(QRect(60, 10, 40, 20))
            self.camera_combo_box.setObjectName("cameraComboBox")
            self.camera_combo_box.currentIndexChanged.connect(self.camera_changed)
            try:
                progress.setLabelText("Scanning camera devices...")
                progress.setValue(75)
                self.refresh_camera_list()
                self.camera_worker = None
            except Exception as ex:
                print(ex)

            # add pix
            self.image_display = QLabel(self)
            self.image_display.setGeometry(QRect(10, 60, self.PIXMAP_WIDTH, self.PIXMAP_HEIGHT))
            self.image_display.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            self.image_display.mousePressEvent = self.click_to_get_coords
            self.image_display.mouseMoveEvent = self.mouseMoveEvent
            self.image_display.mouseReleaseEvent = self.mouseReleaseEvent

            # Create log
            self.message_text = QtWidgets.QPlainTextEdit(central_widget)
            self.message_text.setGeometry(10, 1050, 1280, 30)
            self.message_text.setReadOnly(True)
            self.message_text.setPlainText("Initialized..")

            # status label of raspi
            self.raspi_status_label = QLabel(central_widget)
            self.raspi_status_label.setGeometry(QRect(1500, 5, 80, 30))
            self.raspi_status_label.setText("Raspberri")
            self.raspi_status_label.setAutoFillBackground(True)
            self.raspi_status_label.setStyleSheet("background-color:green;")
            self.raspi_status_label.setAlignment(Qt.AlignCenter)
            self.raspi_status_label.setFrameShape(QFrame.Panel)
            self.raspi_status_label.setFrameShadow(QFrame.Sunken)
            self.raspi_status_label.setLineWidth(2)
            self.raspi_status_label.mousePressEvent = self.init_raspi

            # start Raspi communication thread
            self.raspi_comm = worker_raspi.RaspiWorker()
            self.raspi_comm.signal_comm_err.connect(self.raspi_fail)
            self.raspi_comm.start()
            # start Disk Core thread

            self.disk_core = disk_core.DiskCore([self.laser_params.laser_x_loc, self.laser_params.laser_y_loc],
                                                self.laser_params.laser_pulse_n * (self.laser_params.laser_on_time + self.laser_params.laser_off_time), self.laser_params.offset,
                                                self.camera_params.mag_value, self.target_list, self.disk_list,
                                                self.servo_params.waiting_time)

            self.disk_core.gray_image_request.connect(self.core_image_request)
            self.disk_core.steppers_request.connect(self.move_steppers)
            self.disk_core.coords_update.connect(self.update_coords)
            self.disk_core.laser_shot.connect(self.blink_laser_n)
            self.disk_core.auto_done.connect(self.automode_finished)

            self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
            self.origin = QPoint()
            self.endpoint = QPoint()

            # formation window
            self.formation_window = window_formation.FormationWindow()
            self.formation_window.change_params.connect(self.formation_change)

            # video settings window
            self.video_settings_window = window_video.VideoSettingsWindow(self.camera_params.save_interval,
                                                                          self.camera_params.save_namespace,
                                                                          self.camera_params.save_path)
            self.video_settings_window.closed.connect(self.video_settings_close)

            # laser settings window
            self.laser_settings_window = window_laser.LaserSettingsWindow(self.laser_params)
            self.laser_settings_window.change_params.connect(self.laser_settings_changed)
            self.laser_settings_window.laser_control_signal.connect(self.laser_control)

            self.sfl_settings_window = window_sfl.SflSettingsWindow(self.sfl_params)
            self.sfl_settings_window.change_params.connect(self.sfl_settings_changed)

            self.sfl_settings_window.sfl_switch_signal.connect(self.sfl_switch)
            self.sfl_settings_window.pulse_signal.connect(self.pulse)
            self.sfl_settings_window.flush_switch_signal.connect(self.flush_switch)
            self.sfl_settings_window.light_switch_signal.connect(self.light_switch)
            self.sfl_settings_window.stamping_switch_signal.connect(self.stamping_switch)

            try:
                # TODO rethink eval() usage
                eval("self.mag_" + str(self.camera_params.mag_value) + "_checkbox.setChecked(True)")
            except AttributeError:
                self.logger.log_exception("config.ini file is inconsistent. Unexpected magnification value.",
                                          "Unexpected magnification value. Select proper magnification value.")

            self.checkbox_mag_group = QtWidgets.QButtonGroup(self)
            for item in [4, 10, 20, 40]: eval("self.checkbox_mag_group.addButton(self.mag_"+ str(item) + "_checkbox)")
            self.checkbox_mag_group.setExclusive(True)
            self.showMaximized()
            progress.setLabelText("Initializing camera...")
            progress.setValue(90)
            self.run_camera()
            progress.setValue(100)
        except Exception as ex:
            print(ex)

    def cam_params_edited(self, param_name):
        # TODO promyslet jestli nejde narvat vsechno sem
        # if self.camera_params.brightness_value is not None:
        #     try:
        #         brightness_value = self.camera_worker.camera_worker_params.brightness_value
        #         new_value = float(self.camera_brightness_input.text().replace(",", "."))
        #
        #         self.camera_worker.camera_params.brightness_value = new_brightness_value
        #         self.camera_worker.camera_worker_params.change_params_flag = True
        #         self.config.set("camera", "brightness", str(new_brightness_value).replace(".", ","))
        #         self.camera_params.save_to_ini()
        #     except ValueError:
        #         self.logger.log_exception("Error in brightness_edited", "Brightness value error.")
        pass

    def start_formation(self):
        pass

    def formation_change(self, disks_list, targets_list):
        self.disk_list = disks_list
        self.target_list = targets_list

    def show_formation_window(self):
        self.formation_window.close()
        self.formation_window.show()

    def stamping_switch(self, command):
        if command == "start":
            self.raspi_comm.requests_queue.append(self.sfl_params.rasp_repr())
        elif command == "end":
            self.raspi_comm.requests_queue.append("c")

    @exception_handler
    def keyboard_event_received(self, event):
        keyboard_pressed = event.name
        if keyboard_pressed in ["a", "s", "d", "w"]:
            if keyboard_pressed in ["a", "d"]:
                constant, raspi_command = (1, "x") if keyboard_pressed == "a" else (-1, "x")
                stepper, axis = [constant * self.servo_params.steppers_x, 0], self.servo_params.steppers_x
            elif keyboard_pressed in ["s", "w"]:
                constant, raspi_command = (1, "y") if keyboard_pressed == "w" else (-1, "y")
                stepper, axis = [0, constant * self.servo_params.steppers_y], self.servo_params.steppers_y
            if raspi_command == "x":
                self.raspi_comm.requests_queue.append("x" + str(constant * axis) + ",0")
            else:
                self.raspi_comm.requests_queue.append("x0," + str(constant * axis))
            self.disk_core.recompute_goal(stepper[0], stepper[1])
            self.disk_core.recompute_disk(stepper[0], stepper[1])
            self.disk_list = deepcopy(self.disk_core.disk_list)
            self.target_list = deepcopy(self.disk_core.target_list)
            self.update_coords(self.disk_list, self.target_list)
            # TODO update_coords rewrite and add param to determine the translation
        elif keyboard_pressed == "q":
            self.raspi_comm.requests_queue.append("s")
        elif keyboard_pressed == "e":
            self.raspi_comm.requests_queue.append("l")

    @exception_handler
    def mag_click(self, mag):

        mag_text = mag.text()

        mag_value = int(mag_text.replace("x", ""))

        if mag.isChecked and mag_value != self.camera_params.mag_value:

            self.camera_params.mag_value = self.disk_core.mag = mag_value

            self.camera_params.save_to_ini()

    def set_sfl_checkbox_click(self, state):
        self.set_sfl_enabled = state

    def laser_control(self, command):
        self.raspi_comm.requests_queue.append(command)

    @exception_handler
    def sfl_settings_changed(self, sfl_params: SflParams):
        self.sfl_params = sfl_params
        self.sfl_params.save_to_ini()

    def laser_settings_changed(self, laser_params: LaserParams):
        self.laser_params = laser_params
        self.disk_core.region_offset = self.laser_params.offset
        self.laser_params.save_to_ini()

    def pulse(self):
        self.raspi_comm.requests_queue.append("a" + "," +
                                              str(self.sfl_params.sfl_light_on) +
                                              "," + str(self.sfl_params.sfl_pulse))

    def sfl_pulse_edited(self):
        self.sfl_pulse = int(self.sflPulseInput.text())
        self.message_text.setPlainText("sfl pulse: {} ".format(str(self.sfl_pulse)))
        self.config.set("sfl", "pulse", self.sfl_pulse)
        self.update_config_file()

    def flush_switch(self):
        if self.sfl_settings_window.sfl_flush_button.text() == "Flush ON":
            self.sfl_settings_window.sfl_flush_button.setText("Flush OFF")
            self.raspi_comm.requests_queue.append("n")
        else:
            self.raspi_comm.requests_queue.append("m")
            self.sfl_settings_window.sfl_flush_button.setText("Flush ON")

    def light_switch(self):
        if self.sfl_settings_window.sfl_light_button.text() == "Light ON":
            self.sfl_settings_window.sfl_light_button.setText("Light OFF")
            self.raspi_comm.requests_queue.append("j")
        else:
            self.raspi_comm.requests_queue.append("h")
            self.sfl_settings_window.sfl_light_button.setText("Light ON")

    def sfl_switch(self):
        if self.sfl_settings_window.sfl_switch_button.text() == "SFL ON":
            self.sfl_settings_window.sfl_switch_button.setText("SFL OFF")
            self.raspi_comm.requests_queue.append("p" + "," + str(self.sfl_params.sfl_flush_on) + "," + str(self.sfl_params.sfl_flush_off) +
                                                  "," + str(self.sfl_params.sfl_light_on) + "," + str(self.sfl_params.sfl_light_off))
        else:
            self.raspi_comm.requests_queue.clear()
            self.raspi_comm.requests_queue.append("o")
            self.sfl_settings_window.sfl_switch_button.setText("SFL ON")

    def sfl_light_on_edited(self):
        self.sfl_settings_window.sfl_light_on = int(self.sflLightOnInput.text())
        self.message_text.setPlainText("sfl light on: {} ".format(str(self.sfl_light_on)))
        self.config.set("sfl", "light_on", self.sfl_light_on)
        self.update_config_file()

    def sfl_light_off_edited(self):
        self.sfl_light_off = int(self.sflLightOffInput.text())
        self.message_text.setPlainText("sfl light off: {} ".format(str(self.sfl_light_off)))
        self.config.set("sfl", "light_off", self.sfl_light_off)
        self.update_config_file()

    def sfl_flush_on_edited(self):
        self.sfl_flush_on = int(self.sflFlushOnInput.text())
        self.message_text.setPlainText("sfl flush on: {} ".format(str(self.sfl_flush_on)))
        self.config.set("sfl", "flush_on", self.sfl_flush_on)
        self.update_config_file()

    def sfl_flush_off_edited(self):
        self.sfl_flush_off = int(self.sflFlushOffInput.text())
        self.message_text.setPlainText("sfl flush off: {} ".format(str(self.sfl_flush_off)))
        self.config.set("sfl", "flush_off", self.sfl_flush_off)
        self.update_config_file()

    def laser_switch(self):
        if self.laser_button.text() == "Laser ON":
            self.raspi_comm.requests_queue.append("s")
            self.laser_button.setText("Laser OFF")
        else:
            self.raspi_comm.requests_queue.append("l")
            self.laser_button.setText("Laser ON")

    def automode_finished(self):
        self.formation_window.automode_status = False

    def update_coords(self, disk_list, target_list):
        self.disk_list = []
        self.target_list = []
        for item in disk_list:
            int_coords = []
            for coord in item:
                int_coords.append(int(coord))
            self.disk_list.append(int_coords)
        for item in target_list:
            int_coords = []
            for coord in item:
                int_coords.append(int(coord))
            self.target_list.append(int_coords)
        self.formation_window.targets_list = deepcopy(self.target_list)
        self.formation_window.disks_list = deepcopy(self.disk_list)
        self.formation_window.refill_lists()

    def move_steppers(self, x, y):
        # self.raspi_comm.requests_queue.append("x" + str(x))
        # self.raspi_comm.requests_queue.append("y" + str(y))
        self.raspi_comm.requests_queue.append("x" + str(x) + "," + str(y))

    @exception_handler
    def automode(self, _):
        if self.auto_mode_button.text() == "Auto ON":
            if len(self.disk_list) == len(self.target_list):
                self.auto_mode_button.setText("Auto OFF")
                self.automode_enabled = True
                self.disk_core.auto_mode = True
                self.disk_core.auto_step = -1

                self.disk_core.laser_x = self.laser_params.laser_x_loc
                self.disk_core.laser_y = self.laser_params.laser_y_loc
                self.disk_core.target_list = self.target_list
                self.disk_core.disk_list = self.disk_list
                self.formation_window.automode_status = True
                self.disk_core.start()
            else:
                error_dialog = QtWidgets.QErrorMessage()
                error_dialog.showMessage("The number of targets has to be same as number of disks!")
                error_dialog.setWindowTitle("Error")
                error_dialog.exec_()
        else:
            self.auto_mode_button.setText("Auto ON")
            self.automode_enabled = False
            self.disk_core.auto_mode = False
            self.formation_window.automode_status = False

    def core_image_request(self):
        self.disk_core.image_to_process = np.copy(self.gray_image)

    def find_disks(self):
        # TODO include this into utils?
        helpy_im = self.gray_image
        locs = self.disk_core.find_disks(helpy_im)
        if len(locs) > 0:
            for max_loc in locs:
                helpy_im = cv2.drawMarker(helpy_im, max_loc, (255, 255, 255), markerType=cv2.MARKER_CROSS,
                                          markerSize=20, thickness=1, line_type=cv2.LINE_AA)

                cv2.putText(helpy_im, str(max_loc), max_loc, cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 2,
                            cv2.LINE_AA)
            helpy_im = cv2.resize(helpy_im, (1280, 720))
            cv2.imshow("Disk locations", helpy_im)
            cv2.waitKey(0)

    def set_laser_checkbox_click(self, state):
        self.set_laser_enabled = state

    def draw_marks_checkbox_click(self, state):
        self.draw_marks_enabled = state

    def save_video_checkbox_click(self, state):
        if self.camera_worker is not None:
            self.camera_worker.camera_worker_params.grab_flag = state

    def laser_checkbox_click(self, state):
        self.move_laser_enabled = state

    def disk_checkbox_click(self, state):
        self.set_disk_enabled = state

    def disk_formation_checkbox_click(self, state):
        self.add_disk_formation = state

    def goal_formation_checkbox_click(self, state):
        self.add_target_formation = state

    def goal_checkbox_click(self, state):
        self.set_goal_enabled = state

    @exception_handler
    def click_to_get_coords(self, event):
        x_pixmap = event.pos().x()
        y_pixmap = event.pos().y()
        x_scale = self.camera_params.width_value / self.PIXMAP_WIDTH
        y_scale = self.camera_params.height_value / self.PIXMAP_HEIGHT
        # x_scale = 1
        # y_scale = 1
        x_image = int(x_pixmap * x_scale)
        y_image = int(y_pixmap * y_scale)
        print("clicked")
        if self.move_laser_enabled:
            steps_x = x_image - self.laser_params.laser_x_loc
            steps_y = y_image - self.laser_params.laser_y_loc
            self.raspi_comm.requests_queue.append("x" + str(int(6.6666 * steps_x/2.5)) + "," + str(int(6.6666 * steps_y/2.5)))
            #self.raspi_comm.requests_queue.append("x" + str(int(6.6666 * steps_x/2.5)))
        elif self.set_laser_enabled:
            self.laser_params.laser_x_loc = x_image
            self.laser_params.laser_y_loc = y_image
            self.laser_settings_window.laser_coordx_input.setText(str(x_image))
            self.laser_settings_window.laser_coordy_input.setText(str(y_image))
            self.laser_params.save_to_ini()
        elif self.video_settings_window.roi_enabled:
            if event.button() == QtCore.Qt.LeftButton:
                self.origin = QPoint(x_pixmap, y_pixmap)
                self.rubber_band.setGeometry(QRect(QPoint(x_pixmap + 10, y_pixmap + 60), QSize()))
                self.rubber_band.show()
        elif self.set_sfl_enabled:
            print("entering set sfl enabled")
            self.sfl_params.sfl_x_loc = x_image
            self.sfl_params.sfl_y_loc = y_image
            print("got coords")
            self.sfl_params.save_to_ini()
            print("sfl saved")
        elif self.add_disk_formation:
            locs = self.disk_core.find_disks(self.gray_image)
            if len(locs) > 0:
                nearest_disk = self.disk_core.nearest_disk([x_image, y_image], locs)
                self.disk_list.append([nearest_disk[0], nearest_disk[1]])
                self.formation_window.add_disk(str([nearest_disk[0], nearest_disk[1]]))
        elif self.add_target_formation:
            self.target_list.append([x_image, y_image])
            self.disk_core.target_list.append([x_image, y_image])
            self.formation_window.add_target(str([x_image, y_image]))

    @exception_handler
    # TODO tenhle onClose shit dat primo do window_xxxx.py
    def video_settings_close(self, save_interval, save_namespace, save_path):
        self.camera_params.save_interval = self.camera_worker.camera_params.save_interval = save_interval
        self.camera_params.save_namespace = self.camera_worker.camera_params.save_namespace = save_namespace
        self.camera_params.save_path = self.camera_worker.camera_params.save_path = save_path
        self.camera_params.save_to_ini()

    @exception_handler
    def save_video_settings(self, _):
        """
        Function to show Video settings window.
        :return:
        """
        self.video_settings_window.show()

    @exception_handler
    def show_laser_settings(self, _):
        """
        Function to show Laser settings window.
        :return:
        """
        self.laser_settings_window.show()

    @exception_handler
    def show_sfl_settings(self, _):
        # TODO potrebuju na tohle fakt funkci?
        """
        Function to show Sfl settings window.
        :return:
        """
        self.sfl_settings_window.show()

    def steppers_x_edited(self):
        """Function to set steppers steps for manual control"""
        try:
            self.servo_params.steppers_x = int(self.steppers_x_input.text())
            self.message_text.setPlainText("stepper x: {} ".format(str(self.servo_params.steppers_x)))
            self.config.set("steppers", "x", self.servo_params.steppers_x)
            self.update_config_file()
        except ValueError:
            self.logger.log_exception("Error in steppers_x_edited.", "Stepper X value error.")

    def steppers_y_edited(self):
        """Function to set steppers steps for manual control"""
        try:
            self.servo_params.steppers_y = int(self.steppers_y_input.text())
            self.message_text.setPlainText("stepper y: {} ".format(str(self.servo_params.steppers_y)))
            self.config.set("steppers", "y", self.servo_params.steppers_y)
            self.update_config_file()
        except ValueError:
            self.logger.log_exception("Error in steppers_y_edited.", "Stepper Y value error.")

    def red_button_function(self):
        """
        Function to send Red button request to Raspberry PI.
        :return:
        """
        self.raspi_comm.requests_queue.clear()
        self.raspi_comm.requests_queue.append("r")

    def init_raspi(self, _):
        """
        Function to initialize communication with Raspberry PI after click
        on raspberry label.
        :param _: click event
        :return:
        """
        self.raspi_status_label.setStyleSheet("background-color:green;")
        if not self.raspi_comm.raspi_status:
            self.raspi_comm = worker_raspi.RaspiWorker()
            self.raspi_comm.signal_comm_err.connect(self.raspi_fail)
            self.raspi_comm.start()

    def blink_laser_n(self):
        """
        Function that send Raspberry PI request to blink laser n times with time_on and time_off period.
        :return:
        """
        time_on = int(self.laser_params.laser_on_time)
        time_off = int(self.laser_params.laser_off_time)
        n = int(self.laser_params.laser_pulse_n)
        self.raspi_comm.requests_queue.append("q" + "," + str(time_on) + "," + str(time_off) + "," + str(n))

    def raspi_fail(self):
        """
        Function that set the label that visualizes the RPI status and terminate the
        thread, that is communication with RPI.
        :return:
        """
        self.message_text.setPlainText("Communication with Raspberry PI failed.")
        self.raspi_status_label.setStyleSheet("background-color:red;")
        self.raspi_comm.terminate()

    def laser_on_edited(self):
        """Function to set the time on for laser"""
        try:
            laser_on = self.laser_on_time
            self.laser_params.laser_on_time = int(self.laserOnInput.text())
            self.message_text.setPlainText(
              "Laser on time value changed from {} to {}".format(str(laser_on), str(self.laser_on_time)))
            self.config.set("laser", "on_time", str(self.laser_on_time))
            self.update_config_file()
        except ValueError as e:
            self.logger.log_exception("Error in laser_on_edited.", "Laser on time value error.")

    def laser_off_edited(self):
        """Function to set the time on for laser"""
        try:
            laser_off = self.laser_off_time
            self.laser_params.laser_off_time = int(self.laserOffInput.text())
            self.message_text.setPlainText(
              "Laser off time value changed from {} to {}".format(str(laser_off), str(self.laser_off_time)))
            self.config.set("laser", "off_time", str(self.laser_off_time))
            self.update_config_file()
        except ValueError:
            self.logger.log_exception("Error in laser_off_edited.", "Laser off error.")

    def pulse_number_edited(self):
        """Function to set the number of laser pulses"""
        try:
            pulse_number = self.laser_pulse_n
            self.laser_params.laser_pulse_n = int(self.pulseNumberInput.text())
            self.message_text.setPlainText(
              "Laser pulse number value changed from {} to {}".format(str(pulse_number), str(self.laser_pulse_n)))
            self.config.set("laser", "pulses", self.laser_pulse_n)
            self.update_config_file()
        except ValueError:
            self.logger.log_exception("Error in pulse_number_edited.", "Pulse number error.")

    @exception_handler
    def brightness_edited(self):
        """Function to set brightness of the camera"""
        if self.camera_params.brightness_value is not None:
            print("brightness passed 1")
            try:
                brightness_value = self.camera_worker.camera_params.brightness_value
                new_brightness_value = float(self.camera_brightness_input.text().replace(",", "."))
                self.message_text.setPlainText(
                  "Brightness value changed from {} to {}".format(str(brightness_value), str(new_brightness_value)))
                self.camera_worker.camera_params.brightness_value = new_brightness_value
                self.camera_worker.camera_worker_params.change_params_flag = True
                self.config.set("camera", "brightness", str(new_brightness_value).replace(".", ","))

                self.update_config_file()
            except ValueError:
                self.logger.log_exception("Error in brightness_edited", "Brightness value error.")

    def gain_edited(self):
        """Function to set gain of the camera"""
        if self.camera_worker is not None:
            try:
                gain_value = self.camera_worker.camera_params.gain_value
                new_gain_value = float(self.camera_gain_input.text().replace(",", "."))
                self.message_text.setPlainText("Gain value changed from {} to {}".format(str(gain_value),
                                                                                         str(new_gain_value)))
                self.camera_worker.camera_params.gain_value = new_gain_value
                self.camera_worker.change_params_flag = True
                self.config.set("camera", "gain", str(new_gain_value).replace(".", ","))
                self.update_config_file()
            except ValueError:
                self.logger.log_exception("Error in gain_edited", "Gain value error.")

    def exposure_edited(self):
        """Function to set Exposure of camera"""
        if self.camera_worker is not None:
            try:
                exposure_value = self.camera_worker.camera_params.exposure_value
                new_exposure_value = int(self.camera_exposure_input.text())
                self.message_text.setPlainText("Exposure value changed from {} to {}".format(str(exposure_value),
                                                                                             str(new_exposure_value)))
                self.camera_worker.camera_params.exposure_value = new_exposure_value
                self.camera_worker.camera_worker_params.change_params_flag = True
                self.config.set("camera", "exposure", str(new_exposure_value))
                self.update_config_file()
            except ValueError:
                self.logger.log_exception("Error in exposure_edited", "Exposure value error")

    def fps_edited(self):
        """Function to set FPS of camera"""
        if self.camera_worker is not None:
            try:
                fps_value = self.camera_worker.camera_params.fps_value
                new_fps_value = int(self.camera_fps_input.text())
                self.message_text.setPlainText("FPS value changed from {} to {}".format(str(fps_value),
                                                                                        str(new_fps_value)))
                self.camera_worker.camera_params.fps_value = new_fps_value
                self.camera_worker.change_params_flag = True
                self.config.set("camera", "fps", str(new_fps_value))
                self.update_config_file()
            except ValueError:
                self.logger.log_exception("Error in fps_edited.", "FPS value error.")

    def width_edited(self):
        """Function to set  width of camera image"""
        if self.camera_worker is not None:
            try:
                width_value = self.camera_worker.camera_params.width_value
                new_width_value = int(self.camera_width_input.text())
                self.message_text.setPlainText("Frame width value changed from {} to {}".format(str(width_value),
                                                                                                str(new_width_value)))
                self.camera_worker.camera_params.width_value = new_width_value
                self.camera_worker.camera_worker_params.change_params_flag = True
                self.config.set("camera", "width", str(new_width_value))
                self.update_config_file()
            except ValueError:
                self.logger.log_exception("Error in width_edited function.", "Width value error.")

    def height_edited(self):
        """Function to set  height of camera image"""
        if self.camera_worker is not None:
            try:
                height_value = self.camera_worker.camera_params.height_value
                new_height_value = int(self.camera_height_input.text())
                self.message_text.setPlainText("Frame height value changed from {} to {}".format(str(height_value),
                                                                                                 str(new_height_value)))
                self.camera_params.height_value = new_height_value
                self.camera_worker.camera_params.height_value = new_height_value
                self.camera_worker.camera_worker_params.change_params_flag = True
                self.camera_params.save_to_ini()
            except ValueError:
                self.logger.log_exception("Error in height_edited function", "Height value error.")

    def run_camera(self):
        """
        Function to start the camera_worker (see worker_camera.py) that
        is responsible for camera settings and image obtaining.
        :return:
        """
        if self.camera_combo_box.count() > 0:
            if self.run_camera_button.text() == "Run camera":
                self.camera_combo_box.setEnabled(False)
                self.camera_worker = worker_camera.CameraWorker(self.camera_combo_box.currentIndex(),
                                                                self.camera_params)
                self.camera_worker.image_ready.connect(self.obtain_image)
                self.camera_worker.start()
                self.run_camera_button.setText("Stop camera")
            else:
                self.camera_worker.image_ready.disconnect(self.obtain_image)
                self.camera_worker.camera_worker_params.quit_flag = True
                self.camera_combo_box.setEnabled(True)
                self.run_camera_button.setText("Run camera")

    # @exception_handler
    def obtain_image(self):
        """Function to get camera image from camera worker. The conversion to grayscale is done."""
        try:
            self.camera_worker.mutex.lock()
            self.image_to_display = np.copy(self.camera_worker.raw_image)
            if self.video_settings_window.roi_checkbox.isChecked():
                self.camera_worker.camera_worker_params.save_roi = True
            else:
                self.camera_worker.camera_worker_params.save_roi = False
            self.camera_worker.mutex.unlock()
            self.gray_image = cv2.cvtColor(self.image_to_display, cv2.COLOR_BGR2GRAY)
            self.image_to_display = cv2.cvtColor(self.gray_image, cv2.COLOR_GRAY2RGB)
            if self.draw_marks_enabled:
                # TODO wrap draw markers into function that will check the coordinates (if it is inside of img)
                self.image_to_display = draw_marks(self.image_to_display, self.disk_list, self.target_list,
                           [self.laser_params.laser_x_loc, self.laser_params.laser_y_loc],
                           [self.sfl_params.sfl_x_loc, self.sfl_params.sfl_y_loc, self.sfl_params.sfl_radius])

                x_scale = self.camera_params.width_value / self.PIXMAP_WIDTH
                y_scale = self.camera_params.height_value / self.PIXMAP_HEIGHT
                if self.draw_roi:
                    rectangle_startpoint_x = int(x_scale * self.origin.x())
                    rectangle_startpoint_y = int(y_scale * self.origin.y())
                    rectangle_endpoint_x = int(x_scale * self.endpoint.x())
                    rectangle_endpoint_y = int(y_scale * self.endpoint.y())
                    # self.camera_worker.roi_origin = (rectangle_startpoint_x, rectangle_startpoint_y)
                    # self.camera_worker.roi_endpoint = (rectangle_endpoint_x, rectangle_endpoint_y)
                    self.camera_worker.camera_worker_params.roi_endpoint = (self.endpoint.x(), self.endpoint.y())
                    self.camera_worker.camera_worker_params.roi_origin = (self.origin.x(), self.origin.y())
                    self.image_to_display = cv2.rectangle(self.image_to_display, (self.origin.x(),
                                                                      self.origin.y()),
                                                    (self.endpoint.x(), self.endpoint.y()),
                                                    (255, 20, 147), 2)
            height, width = self.gray_image.shape[:2]
            image_for_pixmap = QtGui.QImage(self.image_to_display, width, height, QtGui.QImage.Format_RGB888)
            self.image_display.setPixmap(QPixmap(image_for_pixmap).scaled(self.PIXMAP_WIDTH, self.PIXMAP_HEIGHT))
        except Exception as ex:
            print("obtain image: ", ex)

    def camera_changed(self):
        """
        This function emits a signal to CameraWorker thread, that the working camera was changed.
        :return: No return
        """
        # TODO WTF funguje to?
        print("emit signal to camera worker with index> ", self.camera_combo_box.currentIndex())

    def refresh_camera_list(self):
        """
        This function finds available cameras in Windows 10 OS
        and fill camera combo box with the indexes of available cameras.
        :return: No return
        """
        arr = []
        for index in range(3):
            cap = cv2.VideoCapture(index)
            if cap is None or not cap.isOpened():
                pass
            else:
                arr.append(index)
            cap.release()
        for idx, item in enumerate(arr):
            self.camera_combo_box.addItem((str(idx)))

    def update_config_file(self):
        """
        Function that opens the config ini file and writes the actual settings.
        :return:
        """
        try:
            with open(self.CONFIG_FILE_NAME, mode="w", encoding="utf-8") as configfile:
                self.config.write(configfile)
        except IOError:
            self.logger.log_exception("Error in gelbots.py during update_config_file",
                                      "Could not save the parameters.")

    def closeEvent(self, event):
        """
        Closing the main window shut down the camera.
        :param event:
        :return:
        """
        if self.raspi_comm.raspi_status:
            self.raspi_comm.k.shutdown(socket.SHUT_RDWR)
            self.raspi_comm.k.close()
        if self.camera_worker is not None:
            self.camera_worker.camera_worker_params.quit_flag = True
            time.sleep(0.5)
        sys.exit()

    def mouseMoveEvent(self, event):
        if not self.origin.isNull() and self.video_settings_window.roi_enabled:
            self.rubber_band.setGeometry(QRect(QPoint(self.origin.x() + 10, self.origin.y() + 60),
                                               QPoint(event.pos().x()+10, event.pos().y()+60)))

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.video_settings_window.roi_enabled:
            self.rubber_band.hide()
            self.endpoint = QPoint(event.pos())
            self.video_settings_window.roi_enabled = False
            self.draw_roi = True


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    progress = QProgressDialog("Main window initializing","cancel", 0, 100)
    progress.setWindowModality(Qt.WindowModal)
    progress.setCancelButton(None)
    progress.setWindowFlags(QtCore.Qt.FramelessWindowHint)
    progress.setWindowFlags(progress.windowFlags() | QtCore.Qt.WindowStaysOnTopHint )
    progress.show()
    progress.setValue(10)
    progress.setGeometry(760, 500, 300, 100)
    progress.setWindowTitle("Loading")
    progress.show()
    main_window = GelbotsWindow(progress)
    main_window.show()
    sys.exit(app.exec_())
