import cv2
import numpy as np
import time
import math
from PyQt5.QtCore import QThread, QMutex, pyqtSignal


class DiskCore2(QThread):
    # REGION_OFFSET = 10

    STEPPER_CONST = 6.6666666
    # signals
    gray_image_request = pyqtSignal()
    steppers_request = pyqtSignal(int, int)
    coords_update = pyqtSignal(int, int, int, int)
    laser_shot = pyqtSignal()
    auto_done = pyqtSignal()

    def __init__(self, laser, laser_time, offset, magnification, target_list, disk_list):
        super(DiskCore2, self).__init__()
        self.image_to_process = None
        self.disk_locs = None
        self.status = True
        self.auto_mode = False
        self.auto_step = -1
        self.target_disk_x = 0
        self.target_disk_y = 0
        self.goal_x = 0
        self.goal_y = 0
        self.laser_x = laser[0]
        self.laser_y = laser[1]
        self.laser_blink_time = laser_time
        self.region_offset = offset
        self.mag = magnification
        self.MAG_STEPPER_CONST = self.STEPPER_CONST * 4 / self.mag
        self.target_list = target_list
        self.disk_list = disk_list

        self.mutex = QMutex()

        # raspberry worker or signal to gui?

    def run(self):
        self.status = True
        shooting_x = 0
        shooting_y = 0
        steps_x = 0
        steps_y = 0
        # logic for disk moving
        while self.auto_mode:
            self.MAG_STEPPER_CONST = self.STEPPER_CONST * 4 / self.mag
            for disk_idx, disk in enumerate(self.disk_list):
                self.target_disk_x = disk[0]
                self.target_disk_y = disk[1]
                self.goal_x = self.target_list[disk_idx][0]
                self.goal_y = self.target_list[disk_idx][1]
                while self.auto_mode:
                    print(self.auto_step)
                    if self.auto_step == -1:

                        self.auto_step = 0
                        self.image_to_process = []
                        self.disk_locs = []
                        self.gray_image_request.emit()
                    elif self.auto_step == 0:
                        # STEP 0: Obtain image
                        if self.image_to_process is not None:
                            # find disk locations
                            self.disk_locs = self.find_disks(self.image_to_process)
                            if len(self.disk_locs) == 0:
                                # TODO return to initial position or acquire next image?
                                self.image_to_process = None
                                self.gray_image_request.emit()
                            else:
                                self.auto_step = 1

                    elif self.auto_step == 1:

                        previous_position_x = self.target_disk_x
                        previous_position_y = self.target_disk_y
                        [x, y] = self.nearest_disk([self.target_disk_x, self.target_disk_y], self.disk_locs)
                        if abs(x - previous_position_x) > 30 * self.mag or abs(y - previous_position_y) > 30 * self.mag:
                            print('wtf')
                            x = previous_position_x
                            y = previous_position_y

                        self.target_disk_x = x
                        self.target_disk_y = y
                        f = open("moving_stats.txt", "a")
                        try:
                            f.write("autostep 1: " + str([self.target_disk_x, self.target_disk_y]) + ";" + str(
                                self.region_offset) + "\n")
                            f.close()
                        except Exception as exp:
                            print(exp)
                        if abs(self.goal_x - x) < 5 and abs(self.goal_y - y) < 5:
                            self.auto_mode = False
                        elif abs(self.target_disk_x - x) > 15 or abs(self.target_disk_y - y) > 15:
                            self.auto_step = -1
                        else:
                            self.auto_step = 2

                    elif self.auto_step == 2:
                        # TODO estimate shooting region
                        shooting_x, shooting_y = self.estimate_shooting_region([self.target_disk_x, self.target_disk_y],
                                                                               [self.goal_x, self.goal_y])
                        f = open("moving_stats.txt", "a")
                        try:
                            f.write("shooting reg." + str([shooting_x, shooting_y]) + ";" + "\n")
                            f.close()
                        except Exception as exp:
                            print(exp)
                        print("shooting x", shooting_x)
                        print("shootin y", shooting_y)

                        self.auto_step = 3
                    elif self.auto_step == 3:
                        # TODO move steppers and wait
                        steps_x, steps_y = self.get_steps(shooting_x, shooting_y)
                        self.move_servo(steps_x, steps_y)

                    elif self.auto_step == 4:
                        # TODO recompute coordinates of goal, disk and update
                        print('steps', steps_x, steps_y)
                        self.recompute_goal(steps_x, steps_y)
                        self.recompute_disk(steps_x, steps_y)
                        self.coords_update.emit(self.goal_x, self.goal_y, self.target_disk_x, self.target_disk_y)
                        self.auto_step = 5

                    elif self.auto_step == 5:
                        # TODO shoot with laser and wait
                        f = open("moving_stats.txt", "a")
                        try:
                            f.write("autostep 5: " + str([self.target_disk_x, self.target_disk_y]) + ";" + "\n")
                            f.close()
                        except Exception as exp:
                            print(exp)
                        self.laser_shot.emit()
                        time.sleep(self.laser_blink_time / 1000 + 0.6)
                        self.auto_step = -1

                    time.sleep(0.1)
        print("exit core")
        self.quit()
        self.wait()

    def find_disks(self, image):
        # TODO find disks centers
        start_time = time.time()
        # image = cv2.medianBlur(image, 5)
        # cimg = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        scaled_min_radius = int(18 * self.mag / 4)
        scaled_max_radius = int(40 * self.mag / 4)
        disk_locs = []
        circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, 1, 40,
                                   param1=50, param2=30, minRadius=scaled_min_radius, maxRadius=scaled_max_radius)
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                # find center
                # if 50 < i[2] < 80:
                disk_locs.append((i[0], i[1]))
            print(time.time() - start_time)
        return disk_locs

    def nearest_disk(self, coords, locs):
        """
        function to find nearest disk to given coordinates
        :param coords: list of coordinates
        :param locs: list of disk centers
        :return: location of nearest disk [x, y]
        """
        nearest_disk = None
        min_distance = 99999.0
        for disk in locs:
            distance = sum((a * 1.0 - b * 1.0) ** 2 for a, b in zip(coords, disk)) ** .5
            if distance < min_distance:
                nearest_disk = disk
                min_distance = distance
        return nearest_disk

    def estimate_shooting_region(self, disk, goal):
        dx = goal[0] - disk[0]
        dy = goal[1] - disk[1]
        # q = 0
        if dx == 0:
            k = 9999999999
        else:
            k = dy / dx
        q = goal[1] - k * goal[0]
        # direction_vector = [dx, dy]
        desired_x1 = disk[0] + self.region_offset / math.sqrt(1 + k ** 2)
        desired_y1 = k * desired_x1 + q
        desired_x2 = disk[0] - self.region_offset / math.sqrt(1 + k ** 2)
        desired_y2 = k * desired_x2 + q
        if math.sqrt((desired_x1 - goal[0]) ** 2
                     + (desired_y1 - goal[1]) ** 2) > math.sqrt((desired_x2 - goal[0]) ** 2
                                                                + (desired_y2 - goal[1]) ** 2):
            desired_x = desired_x1
            desired_y = desired_y1
        else:
            desired_x = desired_x2
            desired_y = desired_y2
        # if abs(dx) < 3:
        #     desired_x = disk[0]
        # else:
        #     if dx > 0:
        #         desired_x = disk[0] - np.sign(dx) * self.region_offset
        #     else:
        #         desired_x = disk[0] - np.sign(dx) * self.region_offset
        # if abs(dy) < 3:
        #     desired_y = disk[1]
        # else:
        #     if dy > 0:
        #         desired_y = disk[1] - np.sign(dy) * self.region_offset
        #     else:
        #         desired_y = disk[1] - np.sign(dy) * self.region_offset

        return desired_x, desired_y

    def move_servo(self, x, y):
        self.steppers_request.emit(x, y)
        time_to_sleep = (abs(x) + abs(y)) * 0.001 + 1
        print("time to sleep", time_to_sleep)
        time.sleep(time_to_sleep)
        self.auto_step = 4

    def shoot(self):
        pass

    def get_steps(self, desired_x, desired_y):
        steps_x = int(self.MAG_STEPPER_CONST * (- self.laser_x + desired_x))
        steps_y = int(self.MAG_STEPPER_CONST * (self.laser_y - desired_y))
        return steps_x, steps_y

    def recompute_goal(self, stepper_x, stepper_y):
        for target in self.target_list:
            target[0] = (target[0] - stepper_x / self.MAG_STEPPER_CONST)
            target[1] = (target[1] - stepper_x / self.MAG_STEPPER_CONST)
            # self.goal_x = (self.goal_x - stepper_x / self.MAG_STEPPER_CONST)
            # self.goal_y = (self.goal_y + stepper_y / self.MAG_STEPPER_CONST)

    def recompute_disk(self, stepper_x, stepper_y):
        for disk in self.disk_list:
            disk[0] = (disk[0] - stepper_x / self.MAG_STEPPER_CONST)
            disk[1] = (disk[1] - stepper_y / self.MAG_STEPPER_CONST)
        # self.target_disk_x = (self.target_disk_x - stepper_x / self.MAG_STEPPER_CONST)
        # self.target_disk_y = (self.target_disk_y + stepper_y / self.MAG_STEPPER_CONST)
