
from rlmath import *


class DummyObject:
    """ Holds a position and velocity. The base can be either a physics object from the rlbot framework or any object
     that has a pos and vel attribute. """

    def __init__(self, base=None):
        if base is not None:
            # Position
            if hasattr(base, "location"):
                self.pos = vec3(base.location.x,
                                base.location.y,
                                base.location.z)
            else:
                self.pos = base.pos

            # Velocity
            if hasattr(base, "velocity"):
                self.vel = vec3(base.velocity.x,
                                base.velocity.y,
                                base.velocity.z)
            else:
                self.vel = base.vel

        else:
            self.pos = vec3(0, 0, 0)
            self.vel = vec3(0, 0, 0)


class UncertainEvent:
    """ UncertainEvents are used by prediction methods to describe their result: If something happens and when
     The class contains a few useful methods to compare UncertainEvents """

    def __init__(self, happens, time, data=None):
        self.happens = happens
        self.time = time
        self.data = data

    def happens_before_time(self, time: float) -> bool:
        return self.happens and self.time < time

    def happens_before(self, other) -> bool:
        return (self.happens and not other.happens) or (other.happens and self.happens_before_time(other.time))

    def happens_after_time(self, time: float) -> bool:
        return not self.happens or self.time > time

    def happens_after(self, other) -> bool:
        return self.happens and (not other.happens or other.time < self.time)


def fall(obj, time: float, g=GRAVITY):
    """ Moves the given object as if were falling. The position and velocity will be modified """
    obj.pos = 0.5 * g * time * time + obj.vel * time + obj.pos
    obj.vel = g * time + obj.vel
    return obj


def ball_predict(bot, time: float) -> DummyObject:
    """ Returns a DummyObject describing the expected position and velocity of the ball """
    t = int(clip(360 * time / 6, 0, 360)) - 1
    path = bot.get_ball_prediction_struct()
    return DummyObject(path.slices[t].physics)


def next_ball_landing(bot, size=BALL_RADIUS):
    landing = arrival_at_height(bot.info.ball, size, "DOWN")
    t = landing.time if landing.happens else 0
    pos = ball_predict(bot, t).pos
    return UncertainEvent(landing.happens, t, data={"pos": pos})


def arrival_at_height(obj, height: float, dir: str="ANY", g=GRAVITY[Z]) -> UncertainEvent:
    """ Returns if and when the ball arrives at a given height. The dir argument can be set to a string
    saying ANY, DOWN, or UP to specify which direction the ball should be moving when arriving. """

    is_close = abs(height - obj.pos[Z]) < 3
    if is_close and dir == "ANY":
        return UncertainEvent(True, 0)

    D = 2 * g * height - 2 * g * obj.pos[Z] + obj.vel[Z] ** 2

    # Check if height is above current pos.z, because then it might never get there
    if obj.pos[Z] < height and dir != "DOWN":
        turn_time = -obj.vel[Z] / (2 * g)
        turn_point_height = fall(DummyObject(obj), turn_time).pos[Z]

        # Return false if height is never reached or was in the past
        if turn_point_height < height or turn_time < 0 or D < 0:
            return UncertainEvent(False, 1e300)

        # The height is reached on the way up
        return UncertainEvent(True, (-obj.vel[Z] + math.sqrt(D)) / g)

    if dir != "UP" and 0 < D:
        # Height is reached on the way down
        return UncertainEvent(True, -(obj.vel[Z] + math.sqrt(D)) / g)
    else:
        # Never fulfils requirements
        return UncertainEvent(False, 1e300)
