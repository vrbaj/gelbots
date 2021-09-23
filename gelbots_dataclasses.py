"""
Module for all dataclasses related to gelbots project.
"""
from dataclasses import dataclass


@dataclass
class LaserParams:
    """Class for keeping laser settings."""
    offset: int
    laser_pulse_n: int
    laser_on_time: int
    laser_off_time: int
    laser_x_loc: int
    laser_y_loc: int


@dataclass
class CameraParams:
    """Class for keeping camera settings."""
    width_value: int
