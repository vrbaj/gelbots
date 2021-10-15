"""
Module for all dataclasses related to gelbots project.
"""
import configparser
from dataclasses import dataclass
from gelbots.error_handling import ErrorLogger


CONFIG_FILE_NAME = "config.ini"

# TODO transform all to properties and add setters?
# TODO use function asdict() for writing settings file?


@dataclass(frozen=False)
class ServoParams:
    """Class for keeping servo settings together"""
    steppers_x: int = 0
    steppers_y: int = 0
    waiting_time: int = 0


@dataclass(frozen=False)
class LaserParams:
    """Class for keeping laser settings together."""
    offset: int = 10
    laser_pulse_n: int = 50
    laser_on_time: int = 50
    laser_off_time: int = 50
    laser_x_loc: int = 50
    laser_y_loc: int = 50

    def get_cycle_time(self):
        return self.laser_pulse_n * (self.laser_on_time * self.laser_off_time)


@dataclass(frozen=False)
class CameraParams:
    """Class for keeping camera settings together."""

    # pylint: disable=too-many-instance-attributes
    # 9 is reasonable in this case.

    width_value: int = 50
    height_value: int = 50
    fps_value: int = 50
    exposure_value: int = 50
    gain_value: float = 0.
    brightness_value: float = 0
    save_interval: int = 0
    mag_value: int = 0
    save_path: str = ""
    save_namespace: str = ""

    def save_to_ini(self):
        """
        Function that opens the config ini file and writes the actual camera settings.
        :return:
        """
        print("entering camera save to ini")
        config = configparser.RawConfigParser()
        config.read(CONFIG_FILE_NAME)
        config.set("camera", "width", str(self.width_value))
        config.set("camera", "height", str(self.height_value))
        config.set("camera", "fps", str(self.fps_value))
        config.set("camera", "exposure", str(self.exposure_value))
        config.set("camera", "gain", str(self.gain_value).replace(".", ","))
        config.set("camera", "brightness", str(self.brightness_value).replace(".", ","))
        config.set("camera", "mag", str(self.mag_value))
        config.set("video", "interval", str(self.save_interval))
        config.set("video", "namespace", str(self.save_namespace))
        config.set("video", "path", str(self.save_path))
        save_config(config)


@dataclass(frozen=False)
class SflParams:
    """Class for keeping sfl settings together."""

    # pylint: disable=too-many-instance-attributes
    # 19 is reasonable in this case.

    sfl_flush_on: int = 0
    sfl_flush_off: int = 0
    sfl_light_on: int = 0
    sfl_light_off: int = 0
    sfl_pulse: int = 0
    sfl_radius: int = 0
    sfl_x_loc: int = 0
    sfl_y_loc: int = 0
    stamping_dx: int = 0
    stamping_dy: int = 0
    stamping_x_delay: int = 0
    stamping_y_delay: int = 0
    stamping_light_on: int = 0
    stamping_light_off: int = 0
    stamping_flush_on: int = 0
    stamping_flush_off: int = 0
    stamping_x_steps: int = 0
    stamping_y_steps: int = 0
    stamping_batch_size: int = 0

    def save_to_ini(self):
        config = configparser.RawConfigParser()
        config.read(CONFIG_FILE_NAME)
        config.set("sfl", "pulse", str(self.sfl_pulse))
        config.set("sfl", "light_on", str(self.sfl_light_on))
        config.set("sfl", "light_off", str(self.sfl_light_off))
        config.set("sfl", "flush_on", str(self.sfl_flush_on))
        config.set("sfl", "flush_off", str(self.sfl_flush_off))
        config.set("sfl", "radius", str(self.sfl_radius))
        config.set("stamping", "dx", str(self.stamping_dx))
        config.set("stamping", "dy", str(self.stamping_dy))
        config.set("stamping", "x_delay", str(self.stamping_x_delay))
        config.set("stamping", "y_delay", str(self.stamping_y_delay))
        config.set("stamping", "light_on", str(self.stamping_light_on))
        config.set("stamping", "light_off", str(self.stamping_light_off))
        config.set("stamping", "flush_on", str(self.stamping_flush_on))
        config.set("stamping", "flush_off", str(self.stamping_flush_off))
        config.set("stamping", "x_steps", str(self.stamping_x_steps))
        config.set("stamping", "y_steps", str(self.stamping_y_steps))
        config.set("stamping", "batch_size", str(self.stamping_batch_size))
        save_config()

    def rasp_repr(self):
        rasp = str(self.stamping_dx) + "," + str(self.stamping_dy) + "," + str(self.stamping_x_steps) +\
               "," + str(self.stamping_y_steps) + "," + str(self.stamping_x_delay) + \
               "," + str(self.stamping_y_delay) + "," + str(self.stamping_light_on) + \
               "," + str(self.stamping_light_off) + "," + str(self.stamping_flush_on) +\
               "," + str(self.stamping_flush_off) + "," + str(self.stamping_batch_size)
        return rasp



@dataclass(frozen=False)
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
    logger = ErrorLogger(__name__)
    try:
        with open(CONFIG_FILE_NAME, mode="w", encoding="utf-8") as configfile:
            config.write(configfile)
    except IOError:
        logger.log_exception("Error in CameraParams class (save_to_ini()) ",
                             "Could not save the parameters.")
