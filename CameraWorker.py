from PyQt5.QtCore import QThread, QMutex, pyqtSignal
from datetime import datetime
import time
import cv2
from tifffile import imsave
import numpy as np
from os import path


class CameraWorker(QThread):
    image_ready = pyqtSignal()

    def __init__(self, camera, width, height, fps, exposure, gain, brightness):
    #def __init__(self, camera):
        super(CameraWorker, self).__init__()
        self.grab_flag = False  # saving frames to file
        self.quit_flag = False  # flag to kill worker
        self.change_params_flag = False  # flat to change camera settings
        self.status = True
        self.frame_number = 0

        # camera params
        # TODO set all camera params according to __init__ args
        self.fps = fps
        self.width = width
        self.height = height
        self.exposure = exposure
        self.gain = gain
        self.brightness = brightness

        # grab params
        self.grab_directory = ""
        self.grab_period = 0.1

        self.mutex = QMutex()
        self.raw_image = []

        try:
            self.camera = cv2.VideoCapture(camera, cv2.CAP_DSHOW)
            print("EXP:", self.camera.get(cv2.CAP_PROP_EXPOSURE))
            self.update_params()
            time.sleep(0.1)
            print(self.camera.get(cv2.CAP_PROP_FPS))

        except Exception as ex:
            print("Cam exp: ", ex)

    def run(self):
        while True:
            if not self.quit_flag:
                if self.change_params_flag:
                    try:
                        self.update_params()
                        print(self.width)
                        print(self.height)
                        self.change_params_flag = False
                    except Exception as ex:
                        print("Exception in update params ", ex)
                self.mutex.lock()
                self.raw_image = self.get_image()
                if self.grab_flag:
                    try:
                        imsave("video_tiff/video{0:08d}.tiff".format(self.frame_number), self.raw_image)
                        self.frame_number += 1
                    except Exception as ex:
                        print(ex)
                self.mutex.unlock()
                self.image_ready.emit()

                time.sleep(1 / self.fps)
            else:
                self.camera.release()
                self.camera = None
                self.status = False
                break

        self.quit()
        self.wait()

    def get_image(self):
        ret, image = self.camera.read()
        return image

    def update_params(self):
        try:
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.camera.set(cv2.CAP_PROP_FPS, self.fps)
            self.camera.set(cv2.CAP_PROP_GAIN, self.gain)
            self.camera.set(cv2.CAP_PROP_EXPOSURE, self.exposure)
            self.camera.set(cv2.CAP_PROP_BRIGHTNESS, self.brightness)
        except Exception as ex:
            print("Exception in update_params method> ", ex)