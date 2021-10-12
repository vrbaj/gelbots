"""
Module for all dataclasses related to gelbots project.
"""
import configparser
from dataclasses import dataclass
from error_handling import ErrorLogger


CONFIG_FILE_NAME = "config.ini"

# TODO transform all to properties and add setters?
# TODO use function asdict() for writing settings file?


@dataclass(frozen=True)
class LaserParams:
    """Class for keeping laser settings together."""
    offset: int
    laser_pulse_n: int
    laser_on_time: int
    laser_off_time: int
    laser_x_loc: int
    laser_y_loc: int

    def get_cycle_time(self):
        return self.laser_pulse_n * (self.laser_on_time * self.laser_off_time)


@dataclass(frozen=True)
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

    def save_to_ini(self):
        """
        Function that opens the config ini file and writes the actual camera settings.
        :return:
        """
        config = configparser.RawConfigParser()
        config.read(CONFIG_FILE_NAME)
        config.set("camera", "width", str(self.width_value))
        config.set("camera", "height", str(self.height_value))
        config.set("camera", "fps", str(self.fps_value))
        config.set("camera", "exposure", str(self.exposure_value))
        config.set("camera", "gain", str(self.gain_value).replace(".", ","))
        config.set("camera", "brightness", str(self.brightness_value).replace(".", ","))
        config.set("video", "interval", str(self.save_interval))
        config.set("video", "namespace", str(self.save_namespace))
        config.set("video", "path", str(self.save_path))
        save_config(config)


@dataclass(frozen=True)
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


@dataclass(frozen=True)
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


def save_config(config):
    logger = ErrorLogger()
    try:
        with open(CONFIG_FILE_NAME, mode="w", encoding="utf-8") as configfile:
            config.write(configfile)
    except IOError:
        logger.log_exception("Error in CameraParams class (save_to_ini()) ",
                             "Could not save the parameters.")
