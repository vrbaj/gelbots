import cv2
import numpy as np
import time
import math
import astar
import rrtstar
from PyQt5.QtCore import QThread, QMutex, pyqtSignal


class DiskCore(QThread):
    # REGION_OFFSET = 10

    STEPPER_CONST = 6.6666666
    # signals
    gray_image_request = pyqtSignal()
    steppers_request = pyqtSignal(int, int)
    coords_update = pyqtSignal(list, list)
    laser_shot = pyqtSignal()
    auto_done = pyqtSignal()

    def __init__(self, laser, laser_time, offset, magnification, target_list, disk_list):
        super(DiskCore, self).__init__()
        self.wait_time = 2.5  # seconds
        self.image_to_process = None
        self.disk_locs = None
        self.path = None
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
        goal = [0, 0]
        # logic for disk moving
        print("thread started")
        while self.auto_mode:
            self.MAG_STEPPER_CONST = self.STEPPER_CONST * 4 / self.mag
            for disk_idx, disk in enumerate(self.disk_list):
                if not self.auto_mode:
                    break
                # self.auto_mode = True
                # not_finished = True
                self.target_disk_x = disk[0]
                self.target_disk_y = disk[1]
                print("target list: ", self.target_list)
                print("target: ", self.target_list[disk_idx])
                goal[0] = self.target_list[disk_idx][0]
                goal[1] = self.target_list[disk_idx][1]


                # find disk locations and start patht planning
                self.image_to_process = []
                self.disk_locs = []
                self.path = []
                self.gray_image_request.emit()
                self.disk_locs = self.find_disks(self.image_to_process)

                height = np.size(self.image_to_process, 0)
                width = np.size(self.image_to_process, 1)
                area_x = [0, width - 1]
                area_y = [0, height - 1]

                start = self.nearest_disk([disk[0], disk[1]], self.disk_locs)
                self.disk_locs.remove(start)
                start = list(start)
                robot_radius = 27.0

                K = 0
                if K:
                    resolution = 5.0
                    a_star = astar.AStarPlanner(area_x, area_y, self.disk_locs, resolution, robot_radius)
                    self.path = a_star.planning(start, goal)
                else:
                    expand_dis = 20
                    resolution = 5
                    goal_sample_rate = 5
                    max_iter = 2500
                    connect_circle_dist = 100.0
                    search_until_max_iter = True

                    rrt_star = rrtstar.RRTStar(
                        start,
                        goal,
                        self.disk_locs,
                        robot_radius,
                        area_x,
                        area_y,
                        expand_dis,
                        resolution,
                        goal_sample_rate,
                        max_iter,
                        connect_circle_dist,
                        search_until_max_iter)
                    self.path = rrt_star.planning(animation=False)



                print("disk loop started")
                # do the loop for every sub_goal in path.
                for id_t, target in enumerate(self.path):
                    not_finished = True
                    while not_finished:  # self.auto_mode:
                        print(self.auto_step)
                        if not self.auto_mode:
                            break
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

                            previous_position_x = disk[0]
                            previous_position_y = disk[1]
                            [x, y] = self.nearest_disk([disk[0], disk[1]], self.disk_locs)
                            if abs(x - previous_position_x) > 30 * self.mag or abs(y - previous_position_y) > 30 * self.mag:
                                print('wtf')
                                x = previous_position_x
                                y = previous_position_y

                            disk[0] = x
                            disk[1] = y
                            f = open("moving_stats.txt", "a")
                            try:
                                f.write("autostep 1: " + str([disk[0], disk[1]]) + ";" + str(
                                    self.region_offset) + "\n")
                                f.close()
                            except Exception as exp:
                                print(exp)
                            if abs(target[0] - x) < 5 and abs(target[1] - y) < 5:
                                # self.auto_mode = False
                                not_finished = False
                            elif abs(disk[0] - x) > 15 or abs(disk[1] - y) > 15:
                                self.auto_step = -1
                            else:
                                self.auto_step = 2

                        elif self.auto_step == 2:
                            # TODO estimate shooting region
                            shooting_x, shooting_y = self.estimate_shooting_region([disk[0], disk[1]],
                                                                                   [target[0], target[1]])
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
                            print("move servo passed")

                        elif self.auto_step == 4:
                            try:
                                # TODO recompute coordinates of goal, disk and update
                                print('steps', steps_x, steps_y)
                                self.recompute_goal(steps_x, steps_y)
                                print("recompute goal done")
                                self.recompute_disk(steps_x, steps_y)
                                print("recompute disk done")
                                self.recompute_path(steps_x, steps_y)
                                print("recompute path done")
                                self.coords_update.emit(self.disk_list, self.target_list)
                                print("signal emit done")

                                self.auto_step = 5
                                disk[0] = self.disk_list[disk_idx][0]
                                disk[1] = self.disk_list[disk_idx][1]
                                target[0] = self.path[id_t][0]
                                target[1] = self.path[id_t][1]
                            except Exception as ex:
                                print(ex)
                        elif self.auto_step == 5:
                            # TODO shoot with laser and wait
                            f = open("moving_stats.txt", "a")
                            try:
                                f.write("autostep 5: " + str([disk[0], disk[1]]) + ";" + "\n")
                                f.close()
                            except Exception as exp:
                                print(exp)
                            print("saving done")
                            try:
                                self.laser_shot.emit()
                            except Exception as ex:
                                print(ex)

                            print("laser shot emit")
                            print("laser blink time: ", self.laser_blink_time)
                            time.sleep(self.laser_blink_time / 1000 + self.wait_time)
                            print("sleep done")
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

    @staticmethod
    def nearest_disk(coordinates, list_centers):
        """
        function to find nearest disk to given coordinates
        :param coordinates: list of coordinates
        :param list_centers: list of disk centers
        :return: location of nearest disk [x, y]
        """
        nearest_disk = None
        min_distance = 99999.0
        for disk in list_centers:
            distance = sum((a * 1.0 - b * 1.0) ** 2 for a, b in zip(coordinates, disk)) ** .5
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
            print("tree1")
            desired_x = desired_x1
            desired_y = desired_y1
        else:
            print("tree2")
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
        time_to_sleep = (abs(x) + abs(y)) * 0.001 + 5
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

        try:

            for idx, target in enumerate(self.target_list):
                self.target_list[idx][0] = (target[0] - stepper_x / self.MAG_STEPPER_CONST)
                self.target_list[idx][1] = (target[1] + stepper_y / self.MAG_STEPPER_CONST)
                # self.goal_x = (self.goal_x - stepper_x / self.MAG_STEPPER_CONST)
                # self.goal_y = (self.goal_y + stepper_y / self.MAG_STEPPER_CONST)

            # self.coords_update.emit(self.disk_list, self.target_list)
        except Exception as ex:
            print(ex)

    def recompute_disk(self, stepper_x, stepper_y):
        try:

            for idx, disk in enumerate(self.disk_list):
                self.disk_list[idx][0] = (disk[0] - stepper_x / self.MAG_STEPPER_CONST)
                self.disk_list[idx][1] = (disk[1] + stepper_y / self.MAG_STEPPER_CONST)
            # self.target_disk_x = (self.target_disk_x - stepper_x / self.MAG_STEPPER_CONST)
            # self.target_disk_y = (self.target_disk_y + stepper_y / self.MAG_STEPPER_CONST)

            # self.coords_update.emit(self.disk_list, self.target_list)
        except Exception as ex:
            print(ex)

    def recompute_path(self, stepper_x, stepper_y):
        try:

            for idx, sub_goal in enumerate(self.path):
                self.path[idx][0] = (sub_goal[0] - stepper_x / self.MAG_STEPPER_CONST)
                self.path[idx][1] = (sub_goal[1] + stepper_y / self.MAG_STEPPER_CONST)
            # self.target_disk_x = (self.target_disk_x - stepper_x / self.MAG_STEPPER_CONST)
            # self.target_disk_y = (self.target_disk_y + stepper_y / self.MAG_STEPPER_CONST)

            # self.coords_update.emit(self.disk_list, self.target_list)
        except Exception as ex:
            print(ex)
