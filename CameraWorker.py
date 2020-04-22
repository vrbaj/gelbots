from PyQt5.QtCore import QThread, QMutex, pyqtSignal
from datetime import datetime
import time
import cv2
from tifffile import imsave
import numpy as np
from os import path


class CameraWorker(QThread):
    image_ready = pyqtSignal()

    def __init__(self, camera):
        super(CameraWorker, self).__init__()
        self.grab_flag = False  # saving frames to file
        self.quit_flag = False  # flag to kill worker
        self.change_params_flag = False  # flat to change camera settings
        self.status = True
        self.frame_number = 0

        # camera params
        # TODO set all camera params from config file
        self.fps = 50
        self.width = 1920
        self.height = 1080
        # self.camera.set(cv2.CAP_PROP_FPS, new_fps_value)


        self.mutex = QMutex()
        self.raw_image = []

        try:
            self.camera = cv2.VideoCapture(camera, cv2.CAP_DSHOW)
        except Exception as ex:
            print(ex)

    def run(self):
        while True:
            if not self.quit_flag:
                if self.change_params_flag:
                    # TODO set all possible params of camera from config file
                    print(self.width)
                    print(self.height)
                    self.change_params_flag = False
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
                #cv2.destroyAllWindows()
                #time.sleep(0.01)
                break

        self.quit()
        self.wait()

    def get_image(self):
        ret, image = self.camera.read()
        return image