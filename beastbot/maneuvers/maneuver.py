from rlbot_flatbuffers import ControllerState


class Maneuver:
    def __init__(self):
        self.done = False

    def exec(self, bot) -> ControllerState:
        raise NotImplementedError

    # TODO Some kind of interrupt when something unexpected happens
