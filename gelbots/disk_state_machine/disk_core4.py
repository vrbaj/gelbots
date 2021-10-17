"""
This module implements state machine to control disks automatic shooting
"""

import time
import math

import cv2
import numpy as np
from PyQt5.QtCore import QThread, QMutex, pyqtSignal

from disk_state_machine.state_interface import State
from disk_state_machine.core_states import StateMachineInitialization, ObtainTargetDisk, ObtainImage,\
    ObtainShootingRegion, MoveSteppers, RecomputeCoordinates, LaserShot


class DiskCore(QThread):
    def __init__(self):
        self.state = StateMachineInitialization()

    def on_event(self, event):
        self.state = self.state.on_event(event)