from state_interface import State


class StateMachineInitialization(State):
    """
    Initialization of state machine.
    """

    def on_event(self, event):
        if event == 'device_locked':
            return ObtainImage()

        return self


class ObtainImage(State):
    """
    The state which indicates that there are limited device capabilities.
    """

    def on_event(self, event):
        if event == 'pin_entered':
            return ObtainTargetDisk()

        return self


class ObtainTargetDisk(State):
    """
    The state which indicates that there are no limitations on device
    capabilities.
    """

    def on_event(self, event):
        if event == 'device_locked':
            return ObtainShootingRegion()

        return self


class ObtainShootingRegion(State):
    """
    The state which indicates that there are no limitations on device
    capabilities.
    """

    def on_event(self, event):
        if event == 'device_locked':
            return MoveSteppers()

        return self


class MoveSteppers(State):
    """
    The state which indicates that there are no limitations on device
    capabilities.
    """

    def on_event(self, event):
        if event == 'device_locked':
            return RecomputeCoordinates()

        return self


class RecomputeCoordinates(State):
    """
    The state which indicates that there are no limitations on device
    capabilities.
    """

    def on_event(self, event):
        if event == 'device_locked':
            return LaserShot()

        return self


class LaserShot(State):
    """
    The state which indicates that there are no limitations on device
    capabilities.
    """

    def on_event(self, event):
        if event == 'device_locked':
            return StateMachineInitialization

        return self

# End of our states.
