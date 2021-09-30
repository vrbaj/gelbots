import sys, socket, copy, os
import cv2_worker
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QLabel, QWidget, QComboBox, QLineEdit, QPushButton
from PyQt5.QtCore import QSize, QRect
from PyQt5.QtGui import QIntValidator, QPixmap, QDoubleValidator
import cv2
import subprocess
import time, datetime
import numpy as np



class ExampleWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        # set default values
        self.save_image_enable = False
        self.raw_image = []
        self.auto_mode_enable = False
        self.shot_emulate = False
        self.RASPI_IP = "192.168.0.101"
        self.RASPI_PORT = 65432
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
        self.pulse_number = 0
        self.pulse_on = 0
        self.pulse_off = 0


        # Set validators
        self.onlyInt = QIntValidator()
        self.onlyDbl = QDoubleValidator()

        # set window properties
        centralWidget = QWidget(self)
        self.setMinimumSize(QSize(1600, 950))
        self.setWindowTitle("Gelbot aimbot")
        self.setCentralWidget(centralWidget)

        # Create combobox and add items.
        self.cameraComboBox = QComboBox(centralWidget)
        self.cameraComboBox.setGeometry(QRect(70, 45, 40, 20))
        self.cameraComboBox.setObjectName(("cameraComboBox"))
        self.refresh_camera_list()
        self.cameraComboBox.currentIndexChanged.connect(self.camera_changed)

        # Create camera combo box label
        self.cameraLabel = QLabel(centralWidget)
        self.cameraLabel.setGeometry(QRect(10, 40, 80, 31))
        self.cameraLabel.setText("Camera:")

        # Create width label
        self.widthLabel = QLabel(centralWidget)
        self.widthLabel.setGeometry(QRect(130, 40, 80, 31))
        self.widthLabel.setText("Width:")

        # Create width input box
        self.widthInput = QLineEdit(centralWidget)
        self.widthInput.move(180, 41)
        self.widthInput.setFixedWidth(40)
        self.widthInput.setValidator(self.onlyInt)
        self.widthInput.editingFinished.connect(self.width_edited)

        # Create height label
        self.heightLabel = QLabel(centralWidget)
        self.heightLabel.setGeometry(QRect(230, 40, 80, 31))
        self.heightLabel.setText("Height:")

        # Create height input box
        self.heightInput = QLineEdit(centralWidget)
        self.heightInput.move(280, 41)
        self.heightInput.setFixedWidth(40)
        self.heightInput.setValidator(self.onlyInt)
        self.heightInput.editingFinished.connect(self.height_edited)

        # Create FPS label
        self.fpsLabel = QLabel(centralWidget)
        self.fpsLabel.setGeometry(QRect(330, 40, 80, 31))
        self.fpsLabel.setText("FPS:")

        # Create fps input box
        self.fpsInput = QLineEdit(centralWidget)
        self.fpsInput.move(380, 41)
        self.fpsInput.setFixedWidth(40)
        self.fpsInput.setValidator(self.onlyInt)
        self.fpsInput.editingFinished.connect(self.fps_edited)

        # Create exposure label
        self.exposureLabel = QLabel(centralWidget)
        self.exposureLabel.setGeometry(QRect(430, 40, 80, 31))
        self.exposureLabel.setText("Exposure:")

        # Create fps input box
        self.exposureInput = QLineEdit(centralWidget)
        self.exposureInput.move(500, 41)
        self.exposureInput.setFixedWidth(40)
        self.exposureInput.setValidator(self.onlyInt)
        self.exposureInput.editingFinished.connect(self.exposure_edited)

        # Create gain label
        self.gainLabel = QLabel(centralWidget)
        self.gainLabel.setGeometry(QRect(800, 40, 80, 31))
        self.gainLabel.setText("Gain:")

        # Create gain input box
        self.gainInput = QLineEdit(centralWidget)
        self.gainInput.move(840, 41)
        self.gainInput.setFixedWidth(40)
        self.gainInput.setValidator(self.onlyDbl)
        self.gainInput.editingFinished.connect(self.gain_edited)

        # Create brightness label
        self.brightnessLabel = QLabel(centralWidget)
        self.brightnessLabel.setGeometry(QRect(900, 40, 80, 31))
        self.brightnessLabel.setText("Brightness:")

        # Create gain input box
        self.brightnessInput = QLineEdit(centralWidget)
        self.brightnessInput.move(980, 41)
        self.brightnessInput.setFixedWidth(40)
        self.brightnessInput.setValidator(self.onlyDbl)
        self.brightnessInput.editingFinished.connect(self.brightness_edited)

        # Create pulse number label
        self.pulseNumberLabel = QLabel(centralWidget)
        self.pulseNumberLabel.setGeometry(QRect(330, 0 , 80, 31))
        self.pulseNumberLabel.setText("Pulse n.:")

        # Create pulse number input box
        self.pulseNumberInput = QLineEdit(centralWidget)
        self.pulseNumberInput.move(400, 0)
        self.pulseNumberInput.setFixedWidth(40)
        self.pulseNumberInput.setValidator(self.onlyInt)
        self.pulseNumberInput.editingFinished.connect(self.pulse_number_edited)

        # Create laser on label
        self.laserOnLabel = QLabel(centralWidget)
        self.laserOnLabel.setGeometry(QRect(500, 0 , 80, 31))
        self.laserOnLabel.setText("On.:")

        # Create laser on input box
        self.laserOnInput = QLineEdit(centralWidget)
        self.laserOnInput.move(600, 0)
        self.laserOnInput.setFixedWidth(40)
        self.laserOnInput.setValidator(self.onlyInt)
        self.laserOnInput.editingFinished.connect(self.laser_on_edited)

        # Create laser on label
        self.laserOffLabel = QLabel(centralWidget)
        self.laserOffLabel.setGeometry(QRect(700, 0 , 80, 31))
        self.laserOffLabel.setText("Off.:")

        # Create laser on input box
        self.laserOffInput = QLineEdit(centralWidget)
        self.laserOffInput.move(800, 0)
        self.laserOffInput.setFixedWidth(40)
        self.laserOffInput.setValidator(self.onlyInt)
        self.laserOffInput.editingFinished.connect(self.laser_off_edited)

        # add pix
        self.imageDisplay = QLabel(self)
        self.imageDisplay.setGeometry(QRect(10, 80, 1200, 800))
        self.imageDisplay.setPixmap(QPixmap("Disk0001.tiff"))
        self.imageDisplay.show()

        # add pix with found disks
        self.disksDisplay = QLabel(self)
        self.disksDisplay.setGeometry(QRect(1230, 80, 600, 480))
        self.disksDisplay.setPixmap(QPixmap("response2020-01-28 15:08:11.933959.png"))
        self.disksDisplay.show()

        # run camera button
        self.runCameraButton = QPushButton('Run camera', self)
        self.runCameraButton.setToolTip('This is an example button')
        self.runCameraButton.move(600, 40)
        self.runCameraButton.clicked.connect(self.run_camera)

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

        # Create log
        self.logger = QtWidgets.QPlainTextEdit(centralWidget)
        self.logger.setGeometry(10, 900, 1000, 40)
        self.logger.setReadOnly(True)
        self.logger.setPlainText("Initialized..")

        # Create combobox for camera resolution and add items.
        self.resolutionComboBox = QComboBox(centralWidget)
        self.resolutionComboBox.setGeometry(QRect(1100, 40, 200, 31))
        self.resolutionComboBox.setObjectName(("resolutionComboBox"))
        self.resolutionComboBox.addItem("800 x 600")
        self.resolutionComboBox.addItem("1920 x 1080")
        self.resolutionComboBox.currentIndexChanged.connect(self.resolution_changed)

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

        #SETTERS
        # set laser  button
        self.setLaserButton = QPushButton('Laser', self)
        self.setLaserButton.setToolTip('Click to set laser location')
        self.setLaserButton.move(1450, 40)
        self.setLaserButton.clicked.connect(self.set_laser_loc)

        # Create laser coordinatex input box
        self.laserCoordInput = QLineEdit(centralWidget)
        self.laserCoordInput.move(1450, 10)
        self.laserCoordInput.setFixedWidth(100)

        # Create goal coordinatex input box
        self.goalCoordInput = QLineEdit(centralWidget)
        self.goalCoordInput.move(1550, 10)
        self.goalCoordInput.setFixedWidth(100)

        # Create disk coordinate input box
        self.diskCoordInput = QLineEdit(centralWidget)
        self.diskCoordInput.move(1650, 10)
        self.diskCoordInput.setFixedWidth(100)


        # set goal  button
        self.setGoalButton = QPushButton('Goal', self)
        self.setGoalButton.setToolTip('Click to set goal location')
        self.setGoalButton.move(1550, 40)
        self.setGoalButton.clicked.connect(self.set_goal_loc)

        # set target disk  button
        self.setDiskButton = QPushButton('Disk', self)
        self.setDiskButton.setToolTip('Click to set goal location')
        self.setDiskButton.move(1650, 40)
        self.setDiskButton.clicked.connect(self.set_target_disk_loc)

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

        # Set camera
        self.camera = cv2.VideoCapture(0)
        time.sleep(0.1)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 800)  # works well
        time.sleep(0.1)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)  # works well
        time.sleep(.2)


        # Set laser loc from previous
        try:
            f = open("../laser_loc.txt", "r")
            self.laser_loc = eval(f.readline())
            print(self.laser_loc)
            self.laserCoordInput.setText(str(self.laser_loc)[1:-1])
        except:
            pass

        self.keyPressEvent = self.keyPressEvent

        # open socket for stream
        #self.k = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.k.connect((self.RASPI_IP, self.RASPI_PORT))

    # Set key press events
    def keyPressEvent(self, e):
        print(e.key())
        self.logger.setPlainText("event " + str(e.key()))
        if e.key() == 65:
            # move left
            self.move_stepper("x-10")
            # try:
            #     self.k.sendalla(bytes("x-10", "UTF-8"))
            # except:
            #     print("dont care about boken pipe shit")

        elif e.key() == 68:
            # move right
            self.move_stepper("x10")
        elif e.key() == 83:
            # move top
            self.move_stepper("y10")
        elif e.key() == 87:
            # move down
            self.move_stepper("y-10")
        elif e.key() == 81:
            self.move_stepper("s")
        elif e.key() == 69:
            self.move_stepper("l")



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
        #print(type(self.gray))
        #print(self.gray)
        if self.save_image_enable:
            cv2.imwrite(os.path.join("25022020","response" + str(datetime.datetime.now()) + ".png"),self.raw_image)

    def save_disk_enabler(self):
        self.save_image_enable = not self.save_image_enable

    def pulse_number_edited(self):
        #TODO exception
        try:
            self.pulse_number = int(self.pulseNumberInput.text())
        except Exception as e:
            print(e)

    def laser_on_edited(self):
        # TODO exception
        try:
            self.pulse_on = int(self.laserOnInput.text())
        except Exception as e:
            print(e)


    def laser_off_edited(self):
        # TODO exception
        try:
            self.pulse_off = int(self.laserOffInput.text())
        except Exception as e:
            print(e)


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

    def set_laser_loc(self):
        self.laser_loc = eval(self.laserCoordInput.text())
        self.logger.setPlainText("laser loc: {} ".format(str(self.laser_loc)))
        f = open("../laser_loc.txt", "w")
        f.write(str(self.laser_loc))
        f.close()

    def set_goal_loc(self):
        self.goal_loc = eval(self.goalCoordInput.text())
        self.logger.setPlainText("goal loc: {}".format(str(self.goal_loc)))

    def set_target_disk_loc(self):
        self.target_disk_loc = eval(self.diskCoordInput.text())
        self.logger.setPlainText("target disk: {}".format(self.target_disk_loc))

    def width_edited(self):
        """Function to set  width of camera image"""
        width_value = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
        try:
            new_width_value = int(self.widthInput.text())
            self.logger.setPlainText("Frame width value changed from {} to {}".format(str(width_value), str(new_width_value)))
        except ValueError:
            self.logger.setPlainText("Width value error")
            new_width_value = width_value
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, new_width_value)
        time.sleep(1)


    def height_edited(self):
        """Function to set height of camera image"""
        height_value = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
        try:
            new_height_value = int(self.heightInput.text())
            self.logger.setPlainText("Frame height value changed from {} to {}".format(str(height_value), str(new_height_value)))
        except ValueError:
            self.logger.setPlainText("Height value error")
            new_height_value = height_value
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, new_height_value)
        time.sleep(1)

    def fps_edited(self):
        """Function to set FPS of camera"""
        fps_value = self.camera.get(cv2.CAP_PROP_FPS)
        camera_id = self.cameraComboBox.currentIndex()
        try:
            new_fps_value = int(self.fpsInput.text())
            self.logger.setPlainText("FPS value changed from {} to {}".format(str(fps_value), str(new_fps_value)))
        except ValueError:
            self.logger.setPlainText("FPS value error")
            new_fps_value = fps_value
        #TODO validate following approach
        self.camera.set(cv2.CAP_PROP_FPS, new_fps_value)
        subprocess.Popen("v4l2-ctl -d /dev/video{} -p {}".format(camera_id, new_fps_value), shell=True)

    def exposure_edited(self):
        camera_id = self.cameraComboBox.currentIndex()
        """Function to set oxposure of camera"""
        # TODO validate following approach
        exposure_value = self.camera.get(cv2.CAP_PROP_EXPOSURE)
        try:
            new_exposure_value = int(self.exposureInput.text())
            self.logger.setPlainText("Exposure value changed from {} to {}".format(str(exposure_value), str(new_exposure_value)))
        except ValueError:
            self.logger.setPlainText("Exposure value error")
            new_exposure_value = exposure_value
        # subprocess.Popen("v4l2-ctl -d /dev/video{} -c exposure_auto=0".format(camera_id), shell=True)
        subprocess.Popen("v4l2-ctl -d /dev/video{} -c exposure_absolute={}".format(camera_id, new_exposure_value), shell=True)

    def gain_edited(self):
        camera_id = self.cameraComboBox.currentIndex()
        """Function to set gain of the camera"""
        # TODO validate following approach
        gain_value = self.camera.get(cv2.CAP_PROP_GAIN)
        try:
            new_gain_value = float(self.gainInput.text().replace(",", "."))
            self.logger.setPlainText("Gain value changed from {} to {}".format(str(gain_value), str(new_gain_value)))
        except ValueError:
            self.logger.setPlainText("Gain value error")
            new_gain_value = gain_value
        self.camera.set(cv2.CAP_PROP_GAIN, new_gain_value)
        # subprocess.Popen("v4l2-ctl -d /dev/video{} -c exposure_auto=0".format(camera_id), shell=True)
        # subprocess.Popen("v4l2-ctl -d /dev/video{} -c exposure_absolute={}".format(camera_id, new_exposure_value), shell=True)

    def brightness_edited(self):
        camera_id = self.cameraComboBox.currentIndex()
        """Function to set gain of the camera"""
        # TODO validate following approach
        brightness_value = self.camera.get(cv2.CAP_PROP_BRIGHTNESS)
        try:
            new_brightness_value = float(self.brightnessInput.text().replace(",", "."))
            self.logger.setPlainText("Brightness value changed from {} to {}".format(str(brightness_value), str(new_brightness_value)))
        except ValueError:
            self.logger.setPlainText("Brightness value error")
            new_brightness_value = brightness_value
        self.camera.set(cv2.CAP_PROP_BRIGHTNESS, new_brightness_value)

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

    def run_camera(self):
        """Function to enable showing of camera image"""
        print("Run camera")

        self.camera_enabled = not self.camera_enabled
        if self.camera_enabled:
            self.runCameraButton.setText("Stop camera")
        else:
            self.runCameraButton.setText("Run camera")

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

    def camera_changed(self):
        try:
            self.camera.release()
            self.camera = cv2.VideoCapture(self.cameraComboBox.currentIndex())
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
            time.sleep(0.1)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
            time.sleep(0.1)
        except:
            self.camera = False


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    mainWin = ExampleWindow()
    mainWin.show()
    sys.exit(app.exec_())

