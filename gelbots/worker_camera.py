"""
This module implements the camera worker, that is running in separate thread
and grabbing images from camera and sets its parameters.
"""
import time
from datetime import datetime

import cv2
from PyQt5.QtCore import QThread, QMutex, pyqtSignal
from PyQt5.QtWidgets import QMessageBox

from gelbots_dataclasses import CameraParams, CameraWorkerParams
from error_handling import exception_handler, ErrorLogger

# from tifffile import imsave


class CameraWorker(QThread):
    """
    Class that represents the camera. The function run is grabbing and saving the images.
    """

    image_ready = pyqtSignal()

    def __init__(self, camera,  camera_params: CameraParams):
        super().__init__()
        self.camera_params = camera_params

        self.logger = ErrorLogger()
        self.camera_worker_params = CameraWorkerParams
        self.mutex = QMutex()
        self.raw_image = []
        try:
            self.camera = cv2.VideoCapture(camera, cv2.CAP_DSHOW)
            self.update_params()
        except Exception:
            self.logger.logger.exception("Error"
                                         " during camera parameters"
                                         " setting and test image grabbing")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText("Failed to init camera.")
            msg.setWindowTitle("Error")
            msg.exec_()
            raise

    @exception_handler
    def run(self):
        """
        Loop to grab images from camera and send them to gelbots.py. If
        saving is enabled, the image (or ROI) is saved to disk as bmp file.
        :return:
        """
        while not self.camera_worker_params.quit_flag:
            if self.camera_worker_params.change_params_flag:
                self.update_params()
                self.camera_worker_params.change_params_flag = False
            self.mutex.lock()
            self.raw_image = self.get_image()
            if self.camera_worker_params.grab_flag:
                actual_time = time.time()
                if actual_time - self.camera_worker_params.last_save_time > \
                        self.camera_params.save_interval:
                    self.camera_worker_params.last_save_time = actual_time
                    try:
                        file_name = str(datetime.now().strftime(
                            "%Y_%m_%d_%H_%M_%S_%f")[:-3]) + ".bmp"
                        if not self.camera_worker_params.save_roi:
                            cv2.imwrite(self.camera_params.save_path +
                                        "/" + self.camera_params.save_namespace +
                                        file_name,
                                        self.raw_image)
                        else:
                            cv2.imwrite(self.camera_params.save_path +
                                        "/" + self.camera_params.save_namespace +
                                        file_name,
                                        self.raw_image[self.camera_worker_params.roi_origin[1]:
                                                       self.camera_worker_params.roi_endpoint[1],
                                        self.camera_worker_params.roi_origin[0]:
                                        self.camera_worker_params.roi_endpoint[0], :])
                        self.camera_worker_params.frame_number += 1
                    except Exception:
                        self.logger.logger.exception("Error during saving image")
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Critical)
                        msg.setText("Error")
                        msg.setInformativeText("Failed to save an image.")
                        msg.setWindowTitle("Error")
                        msg.exec_()
                        raise

            self.mutex.unlock()
            self.image_ready.emit()
            time.sleep(1 / self.camera_params.fps_value)

        self.camera.release()
        self.camera = None
        self.camera_worker_params.status = False

        self.quit()
        self.wait()

    def get_image(self):
        """
        Function to obtain image from the camera.
        :return:
        """
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
        except Exception:
            self.logger.logger.exception("Error during obtaining image from camera.")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText("Failed to get image from camera.")
            msg.setWindowTitle("Error")
            msg.exec_()
            raise

    def update_params(self):
        """
        Function to set camera parameters.
        :return:
        """
        try:
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_params.width_value)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_params.height_value)
            self.camera.set(cv2.CAP_PROP_FPS, self.camera_params.fps_value)
            self.camera.set(cv2.CAP_PROP_GAIN, self.camera_params.gain_value)
            self.camera.set(cv2.CAP_PROP_EXPOSURE, self.camera_params.exposure_value)
            self.camera.set(cv2.CAP_PROP_BRIGHTNESS, self.camera_params.brightness_value)
        except Exception:
            self.logger.logger.exception("Error during camera parameters setting")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText("Failed to set camera parameters.")
            msg.setWindowTitle("Error")
            msg.exec_()
            raise
