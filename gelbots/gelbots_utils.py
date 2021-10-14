import cv2
import configparser

from gelbots_dataclasses import  SflParams, LaserParams, CameraParams

CONFIG_FILE_NAME = "config.ini"


def draw_marks(img, disk_list, target_list, laser_loc, sfl):
    for disk in disk_list:
        img = cv2.drawMarker(img, tuple(disk), (0, 0, 255),
                                    markerType=cv2.MARKER_TILTED_CROSS,
                                    markerSize=20, thickness=1,
                                    line_type=cv2.LINE_AA)
    for target in target_list:
        img = cv2.drawMarker(img, tuple(target), (255, 233, 0),
                                    markerType=cv2.MARKER_DIAMOND,
                                    markerSize=20, thickness=1,
                                    line_type=cv2.LINE_AA)

    img = cv2.drawMarker(img, (laser_loc[0], laser_loc[1]),
                                (255, 0, 0), markerType=cv2.MARKER_STAR,
                                markerSize=20, thickness=1, line_type=cv2.LINE_AA)

    img = cv2.drawMarker(img, (sfl[0],sfl[1]),
                                (0, 255, 0), markerType=cv2.MARKER_CROSS,
                                markerSize=20, thickness=1, line_type=cv2.LINE_AA)
    img = cv2.circle(img, (sfl[0], sfl[1]),
                                 sfl[2], (0, 255, 0), 2)
    return img


def read_config():
    config = configparser.RawConfigParser()

    # TODO this TRY bullshit to function
    laser_params = LaserParams()
    sfl_params = SflParams()
    camera_params = CameraParams()
    config.read(CONFIG_FILE_NAME)
    camera_params.width_value = config.getint("camera", "width", fallback=1920)
    camera_params.height_value = config.getint("camera", "height", fallback=1080)
    camera_params.fps_value = config.getint("camera", "fps", fallback=50)
    camera_params.exposure_value = config.getint("camera", "exposure", fallback=10)
    camera_params.gain_value = float(str(config.get("camera", "gain", fallback=1)).replace(",", "."))
    camera_params.brightness_value = float(str(config.get("camera", "brightness",
                                                                    fallback=0.5)).replace(",", "."))
    camera_params.mag_value = config.getint("camera", "mag", fallback=4)
    laser_params.laser_pulse_n = config.getint("laser", "pulses", fallback=1)
    laser_params.laser_on_time = config.getint("laser", "on_time", fallback=1)
    laser_params.laser_off_time = config.getint("laser", "off_time", fallback=1)
    laser_params.laser_x_loc = config.getint("laser", "x_loc", fallback=0)
    laser_params.laser_y_loc = config.getint("laser", "y_loc", fallback=0)
    laser_params.offset = config.getint("laser", "offset", fallback=10)
    disk_x_loc = config.getint("disk", "x_loc", fallback=0)
    disk_y_loc = config.getint("disk", "y_loc", fallback=0)
    goal_x_loc = config.getint("goal", "x_loc", fallback=0)
    goal_y_loc = config.getint("goal", "y_loc", fallback=0)
    sfl_params.sfl_x_loc = config.getint("sfl", "x_loc", fallback=0)
    sfl_params.sfl_y_loc = config.getint("sfl", "y_loc", fallback=0)
    sfl_params.sfl_radius = config.getint("sfl", "radius", fallback=0)
    steppers_x = config.getint("steppers", "x", fallback=10)
    steppers_y = config.getint("steppers", "y", fallback=10)
    camera_params.save_interval = config.getint("video", "interval", fallback=1)
    camera_params.save_namespace = config.get("video", "namespace", fallback="video")
    camera_params.save_path = config.get("video", "path", fallback="c:/")
    sfl_params.sfl_flush_on = config.getint("sfl", "flush_on", fallback=50)
    sfl_params.sfl_flush_off = config.getint("sfl", "flush_off", fallback=500)
    sfl_params.sfl_light_on = config.getint("sfl", "light_on", fallback=50)
    sfl_params.sfl_light_off = config.getint("sfl", "light_off", fallback=500)
    sfl_params.sfl_pulse = config.getint("sfl", "pulse", fallback=3000)
    # stamping settings
    sfl_params.stamping_dx = config.getint("stamping", "dx", fallback=1)
    sfl_params.stamping_dy = config.getint("stamping", "dy", fallback=1)
    sfl_params.stamping_x_delay = config.getint("stamping", "x_delay", fallback=100)
    sfl_params.stamping_y_delay = config.getint("stamping", "y_delay", fallback=100)
    sfl_params.stamping_light_on = config.getint("stamping", "light_on", fallback=100)
    sfl_params.stamping_light_off = config.getint("stamping", "light_off", fallback=100)
    sfl_params.stamping_flush_on = config.getint("stamping", "flush_on", fallback=100)
    sfl_params.stamping_flush_off = config.getint("stamping", "flush_off", fallback=100)
    sfl_params.stamping_x_steps = config.getint("stamping", "x_steps", fallback=100)
    sfl_params.stamping_y_steps = config.getint("stamping", "y_steps", fallback=100)
    sfl_params.stamping_batch_size = config.getint("stamping", "batch_size", fallback=100)
    returned_data = {"camera": camera_params, "sfl": sfl_params,
                     "laser": laser_params,
                     "steppers": [steppers_x, steppers_y],
                     "disk_target": [disk_x_loc, disk_y_loc, goal_x_loc, goal_y_loc]}
    return returned_data