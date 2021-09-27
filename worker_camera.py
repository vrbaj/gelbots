"""
This module implements the camera worker, that is running in separate thread
and grabbing images from camera and sets its parameters.
"""
import time
from datetime import datetime

import cv2
from PyQt5.QtCore import QThread, QMutex, pyqtSignal

from gelbots_dataclasses import CameraParams
from error_handling import exception_handler
# from tifffile import imsave


class CameraWorker(QThread):
    """
    Class that represents the camera. The function run is grabbing and saving the images.
    """

    image_ready = pyqtSignal()

    def __init__(self, camera,  camera_params: CameraParams):
        super().__init__()
        self.grab_flag = False  # saving frames to file
        self.quit_flag = False  # flag to kill worker
        self.change_params_flag = False  # flag to change camera settings
        self.status = True
        self.frame_number = 0
        self.save_roi = False
        self.roi_origin = (0, 0)
        self.roi_endpoint = (0, 0)

        # camera params
        self.camera_params = camera_params
        self.last_save_time = 0

        self.mutex = QMutex()
        self.raw_image = []
        self.back_ground = []
        try:
            self.camera = cv2.VideoCapture(camera, cv2.CAP_DSHOW)
            self.update_params()
            # ix = 0
            # while ix < 100:
            #     self.camera.read()
            #     ix = ix + 1
            # ret, self.back_ground = self.camera.read()
        except Exception as ex:
            print("Cam exp: ", ex)
        print("camera init done")
        # self.background_subtractor = cv2.createBackgroundSubtractorMOG2()

    @exception_handler
    def run(self):
        while not self.quit_flag:
            if self.change_params_flag:
                try:
                    self.update_params()
                    self.change_params_flag = False
                except Exception as ex:
                    print("Exception in update params ", ex)
            self.mutex.lock()
            self.raw_image = self.get_image()
            if self.grab_flag:
                actual_time = time.time()
                if actual_time - self.last_save_time > self.camera_params.save_interval:
                    self.last_save_time = actual_time
                    try:
                        # imsave(self.grab_directory + "/" + self.grab_namespace +
                        #        "{0:08d}.tiff".format(self.frame_number), self.raw_image)
                        # imsave(self.grab_directory + "/" +
                        # str(datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")[:-3])
                        #        + ".tiff", self.raw_image)
                        file_name = str(datetime.now().strftime(
                            "%Y_%m_%d_%H_%M_%S_%f")[:-3]) + ".bmp"
                        if not self.save_roi:
                            cv2.imwrite(self.camera_params.save_path +
                                        "/" + self.camera_params.save_namespace +
                                        file_name,
                                        self.raw_image)
                        else:
                            cv2.imwrite(self.camera_params.save_path +
                                        "/" + self.camera_params.save_namespace +
                                        file_name,
                                        self.raw_image[self.roi_origin[1]:self.roi_endpoint[1],
                                        self.roi_origin[0]:self.roi_endpoint[0], :])
                        self.frame_number += 1
                    except Exception as ex:
                        print(ex)
            self.mutex.unlock()
            self.image_ready.emit()
            time.sleep(1 / self.camera_params.cam_fps_value)

        self.camera.release()
        self.camera = None
        self.status = False

        self.quit()
        self.wait()

    def get_image(self):
        try:
            _, image2 = self.camera.read()
            # image2 = cv2.imread("1920x1080.png")
            # print("going to subb")
            # image = []
            # image = cv2.subtract(image2, self.back_ground)
            # image2 = cv2.resize(image2, (1200, 800))
            # cv2.imshow("pred odectenim", image2)
            # cv2.waitKey(1)
            #
            # print(image)
            return image2
        except Exception as ex:
            print(ex)
            print("in get image")

    def update_params(self):
        try:
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_params.cam_width_value)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_params.cam_height_value)
            self.camera.set(cv2.CAP_PROP_FPS, self.camera_params.cam_fps_value)
            self.camera.set(cv2.CAP_PROP_GAIN, self.camera_params.cam_gain_value)
            self.camera.set(cv2.CAP_PROP_EXPOSURE, self.camera_params.cam_exposure_value)
            self.camera.set(cv2.CAP_PROP_BRIGHTNESS, self.camera_params.cam_brightness_value)

        except Exception as ex:
            # self.camera.get(cv2.CAP_PROP_BRIGHTNESS)
            print("Exception in update_params method> ", ex)
