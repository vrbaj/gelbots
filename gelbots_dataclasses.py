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
    width_value: int


@dataclass
class SflParams:
    """Class for keeping sfl settings together."""
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

