"""
Module for all dataclasses related to gelbots project.
"""
from dataclasses import dataclass


@dataclass
class LaserParams:
    """Class for keeping laser settings together."""
    offset: int
    laser_pulse_n: int
    laser_on_time: int
    laser_off_time: int
    laser_x_loc: int
    laser_y_loc: int


@dataclass
class CameraParams:
    """Class for keeping camera settings together."""

    # pylint: disable=too-many-instance-attributes
    # 9 is reasonable in this case.

    width_value: int
    height_value: int
    fps_value: int
    exposure_value: int
    gain_value: float
    brightness_value: float
    save_interval: int
    save_path: str
    save_namespace: str


@dataclass
class SflParams:
    """Class for keeping sfl settings together."""

    # pylint: disable=too-many-instance-attributes
    # 19 is reasonable in this case.

    sfl_flush_on: int
    sfl_flush_off: int
    sfl_light_on: int
    sfl_light_off: int
    sfl_pulse: int
    sfl_radius: int
    sfl_x_loc: int
    sfl_y_loc: int
    stamping_dx: int
    stamping_dy: int
    stamping_x_delay: int
    stamping_y_delay: int
    stamping_light_on: int
    stamping_light_off: int
    stamping_flush_on: int
    stamping_flush_off: int
    stamping_x_steps: int
    stamping_y_steps: int
    stamping_batch_size: int

    def rasp_repr(self):
        rasp = str(self.stamping_dx) + "," + str(self.stamping_dy) + "," + str(self.stamping_x_steps) +\
               "," + str(self.stamping_y_steps) + "," + str(self.stamping_x_delay) + \
               "," + str(self.stamping_y_delay) + "," + str(self.stamping_light_on) + \
               "," + str(self.stamping_light_off) + "," + str(self.stamping_flush_on) +\
               "," + str(self.stamping_flush_off) + "," + str(self.stamping_batch_size)
        return rasp


@dataclass
class CameraWorkerParams:
    """Class for keeping camera worker params together."""

    # pylint: disable=too-many-instance-attributes
    # 9 is reasonable in this case.

    grab_flag: bool = False  # saving frames to file
    quit_flag: bool = False  # flag to kill worker
    change_params_flag: bool = False  # flag to change camera settings
    status: bool = True
    frame_number: int = 0
    save_roi: bool = False
    roi_origin: tuple = (0, 0)
    roi_endpoint: tuple = (0, 0)
    last_save_time: int = 0
