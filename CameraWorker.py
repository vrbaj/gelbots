from PyQt5.QtCore import QThread, QMutex, pyqtSignal
import time
import cv2
from tifffile import imsave
from datetime import datetime


# opencv 4.1.0.25


class CameraWorker(QThread):
    image_ready = pyqtSignal()

    def __init__(self, camera, width, height, fps, exposure, gain, brightness, saving_interval,
                 saving_namespace, saving_path):
        super(CameraWorker, self).__init__()
        self.grab_flag = False  # saving frames to file
        self.quit_flag = False  # flag to kill worker
        self.change_params_flag = False  # flag to change camera settings
        self.status = True
        self.frame_number = 0

        # camera params
        self.fps = fps
        self.width = width
        self.height = height
        self.exposure = exposure
        self.gain = gain
        self.brightness = brightness
        # grab params
        self.grab_directory = saving_path
        self.grab_period = saving_interval
        self.grab_namespace = saving_namespace

        self.last_save_time = 0

        self.mutex = QMutex()
        self.raw_image = []

        try:
            self.camera = cv2.VideoCapture(camera, cv2.CAP_DSHOW)
            self.update_params()
        except Exception as ex:
            print("Cam exp: ", ex)

    def run(self):
        while True:
            if not self.quit_flag:
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
                    if actual_time - self.last_save_time > self.grab_period:
                        self.last_save_time = actual_time
                        try:
                            # imsave(self.grab_directory + "/" + self.grab_namespace +
                            #        "{0:08d}.tiff".format(self.frame_number), self.raw_image)
                            # imsave(self.grab_directory + "/" + str(datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")[:-3])
                            #        + ".tiff", self.raw_image)
                            cv2.imwrite(self.grab_directory + "/" + self.grab_namespace + str(datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")[:-3]) + ".bmp", self.raw_image)
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
        try:
            ret, image = self.camera.read()
            # image = cv2.imread("1920x1080.png")
            return image
        except Exception as ex:
            print(ex)
            print("in get image")

    def update_params(self):
        try:
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.camera.set(cv2.CAP_PROP_FPS, self.fps)
            self.camera.set(cv2.CAP_PROP_GAIN, self.gain)
            self.camera.set(cv2.CAP_PROP_EXPOSURE, self.exposure)
            self.camera.set(cv2.CAP_PROP_BRIGHTNESS, self.brightness)

        except Exception as ex:
            # self.camera.get(cv2.CAP_PROP_BRIGHTNESS)
            print("Exception in update_params method> ", ex)
