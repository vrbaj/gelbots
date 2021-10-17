from disk_state_machine.state_interface import State


class StateMachineInitialization(State):
    """
    Initialization of state machine.
    """

    def process_state(self):
        image = []


    def on_event(self, event):
        if event == "initialization_finished":
            return ObtainImage()

        return self


class ObtainImage(State):
    """
    The state which indicates that there are limited device capabilities.
    """

    def process_state(self):
        pass

    def on_event(self, event):
        if event == "image_obtained":
            return ObtainTargetDisk()

        return self


class ObtainTargetDisk(State):
    """
    The state which indicates that there are no limitations on device
    capabilities.
    """

    def process_state(self):
        pass

    def on_event(self, event):
        if event == "disk_obtained":
            return ObtainShootingRegion()

        return self


class ObtainShootingRegion(State):
    """
    The state which indicates that there are no limitations on device
    capabilities.
    """

    def process_state(self):
        pass

    def on_event(self, event):
        if event == "shooting_region_obtained":
            return MoveSteppers()

        return self


class MoveSteppers(State):
    """
    The state which indicates that there are no limitations on device
    capabilities.
    """

    def process_state(self):
        pass

    def on_event(self, event):
        if event == "steppers_moved":
            return RecomputeCoordinates()

        return self


class RecomputeCoordinates(State):
    """
    The state which indicates that there are no limitations on device
    capabilities.
    """

    def process_state(self):
        pass

    def on_event(self, event):
        if event == "coordinates_recomputed":
            return LaserShot()

        return self


class LaserShot(State):
    """
    The state which indicates that there are no limitations on device
    capabilities.
    """

    def process_state(self):
        pass

    def on_event(self, event):
        if event == "laser_shot":
            return StateMachineInitialization()

        return self

# End of our states.
