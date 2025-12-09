import math

from utility.info import GRAVITY, Ball, Field, Car
from utility.rlmath import clip, lerp, clip01
from utility.vec import norm, proj_onto_size, xy, Vec3


class DummyObject:
    """ Holds a position and velocity. The base can be either a physics object from the rlbot framework or any object
     that has a pos and vel attribute. """

    def __init__(self, base=None):
        if base is not None:
            # Position
            if hasattr(base, "location"):
                self.pos = Vec3(base.location.x,
                                base.location.y,
                                base.location.z)
            else:
                self.pos = Vec3.from_vec(base.pos)

            # Velocity
            if hasattr(base, "velocity"):
                self.vel = Vec3(base.velocity.x,
                                base.velocity.y,
                                base.velocity.z)
            else:
                self.vel = Vec3.from_vec(base.vel)

        else:
            self.pos = Vec3(0, 0, 0)
            self.vel = Vec3(0, 0, 0)


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
    trajectory = bot.ball_prediction
    t = int(clip(360 * time / 6, 1, len(trajectory.slices))) - 1
    return DummyObject(trajectory.slices[t].physics)


def next_ball_landing(bot, obj=None, size=Ball.RADIUS) -> UncertainEvent:
    """ Returns a UncertainEvent describing the next ball landing. If obj==None the current ball is used, otherwise the
    given obj is used. """
    if obj is None:
        obj = bot.info.ball
        landing = arrival_at_height(obj, size, "DOWN")
        t = landing.time if landing.happens else 0
        moved_obj = ball_predict(bot, t)

    else:
        landing = arrival_at_height(obj, size, "DOWN")
        t = landing.time if landing.happens else 0
        moved_obj = fall(obj, t)

    return UncertainEvent(landing.happens, t, data={"obj": moved_obj})


def arrival_at_height(obj, height: float, dir: str="ANY", g=GRAVITY.z) -> UncertainEvent:
    """ Returns if and when the ball arrives at a given height. The dir argument can be set to a string
    saying ANY, DOWN, or UP to specify which direction the ball should be moving when arriving. """

    is_close = abs(height - obj.pos.z) < 3
    if is_close and dir == "ANY":
        return UncertainEvent(True, 0)

    D = 2 * g * height - 2 * g * obj.pos.z + obj.vel.z ** 2

    # Check if height is above current pos.z, because then it might never get there
    if obj.pos.z < height and dir != "DOWN":
        turn_time = -obj.vel.z / (2 * g)
        turn_point_height = fall(DummyObject(obj), turn_time).pos.z

        # Return false if height is never reached or was in the past
        if turn_point_height < height or turn_time < 0 or D < 0:
            return UncertainEvent(False, 1e300)

        # The height is reached on the way up
        return UncertainEvent(True, (-obj.vel.z + math.sqrt(D)) / g)

    if dir != "UP" and 0 < D:
        # Height is reached on the way down
        return UncertainEvent(True, -(obj.vel.z + math.sqrt(D)) / g)
    else:
        # Never fulfils requirements
        return UncertainEvent(False, 1e300)


def will_ball_hit_goal(bot):
    ball = bot.info.ball
    if ball.vel.y == 0:
        return UncertainEvent(False, 1e306)

    time = (Field.LENGTH / 2 - abs(ball.pos.y)) / abs(ball.vel.y)
    hit_pos = ball_predict(bot, time).pos
    hits_goal = abs(hit_pos.x) < Field.GOAL_WIDTH / 2 + Ball.RADIUS

    return UncertainEvent(hits_goal, time)


def rough_ball_eta(bot, car):
    """ Estimate when we can reach the ball in 2d. """
    t = 0
    for _ in range(5):
        ball = ball_predict(bot, t)
        car_to_ball = xy(ball.pos - car.pos)
        dist = norm(car_to_ball) - Ball.RADIUS / 2
        vel_f = proj_onto_size(car.vel, car_to_ball)
        vel_amp = lerp(vel_f, norm(car.vel), 0.58)
        t = clip(linear_eta(vel_amp, dist, car.boost / Car.BOOST_USE_RATE), 0, 6.0)

    # Combine slightly with old prediction to prevent rapid changes
    result = lerp(t, car.last_expected_time_till_reach_ball, 0.22)
    car.last_expected_time_till_reach_ball = t
    return result


def _solve_exp_segment(v0: float, x0: float, v_inf: float) -> float:
    """Solve for t in x(t) = x0 when v(t) = v_inf - (v_inf - v0) * exp(-t)"""
    A = v_inf - v0

    # Cheap initial guess
    t = x0 / max(v0, 1.0)

    # One iteration of Newton's method
    E = math.exp(-t)
    x_err = v_inf * t + (v0 - v_inf) * (1 - E) - x0
    v_err = v_inf - A * E
    t = t - x_err / v_err

    # Second iteration
    # E = math.exp(-t)
    # x_err = v_inf * t + (v0 - v_inf) * (1 - E) - x0
    # v_err = v_inf - A * E
    # t = t - x_err / v_err

    return t


def _solve_quad_segment(v0: float, x0: float, a: float) -> float:
    """Solve for t in x(t) = v0 * t + 0.5 * a * t^2 = x0"""
    # Cheap initial guess
    t = x0 / max(v0, 1.0)

    # One iteration of Newton's method
    x_err = v0 * t + 0.5 * a * t * t - x0
    v_err = v0 + a * t
    return t - x_err / v_err


def linear_eta(v0: float, x0: float, boost_dur: float) -> float:
    """Calculate linear ETA based on initial velocity, distance, and boost duration"""
    D = Car.THROTTLE_ACCELERATION_AT_LIMIT
    THR_MAX = Car.MAX_THROTTLE_SPEED
    B = Car.BOOST_ACCELERATION
    v_inf = D + B

    t_sum = 0.0

    # CASE E: v0 >= max_speed
    if v0 >= Car.MAX_SPEED:
        return x0 / Car.MAX_SPEED

    # CASE A: v0 < THR_MAX and boost_dur > 0 (throttle and boost)
    if v0 < THR_MAX and boost_dur > 0:
        # Check if target hit during exponential phase
        t_dest = _solve_exp_segment(v0, x0, v_inf)
        if t_dest >= 0.0 and t_dest <= boost_dur:
            return t_dest

        t_to_max_throttle = math.log((v_inf - v0) / (v_inf - THR_MAX))
        T = min(t_to_max_throttle, boost_dur)

        # Compute state at end of case A
        exp_T = math.exp(-T)
        vT = v_inf - (v_inf - v0) * exp_T
        xT = v_inf * T + (v0 - v_inf) * (1 - exp_T)

        x0 -= xT
        v0 = vT
        boost_dur -= T
        t_sum += T

    # CASE B: v0 < THR_MAX and boost_dur == 0 (throttle)
    if v0 < THR_MAX and boost_dur <= 0:
        t_dest = _solve_exp_segment(v0, x0, D)
        t_to_max_throttle = math.log((D - v0) / (D - THR_MAX))

        # Do we reach destination before THR_MAX?
        if t_dest >= 0.0 and t_dest < t_to_max_throttle:
            return t_dest

        # Compute state at end of case B
        exp_T = math.exp(-t_to_max_throttle)
        vT = D - (D - v0) * exp_T
        xT = D * t_to_max_throttle + (v0 - D) * (1 - exp_T)

        x0 -= xT
        v0 = vT
        t_sum += t_to_max_throttle

    # CASE C: v0 >= THR_MAX and boost_dur > 0 (boost)
    if v0 >= THR_MAX and boost_dur > 0:
        # Do we reach destination before out of boost?
        t_dest = _solve_quad_segment(v0, x0, B)
        if t_dest >= 0.0 and t_dest <= boost_dur:
            return t_dest

        # Do we hit max speed during boost?
        t_to_max_speed = (Car.MAX_SPEED - v0) / B
        if t_to_max_speed <= boost_dur:
            x0 -= v0 * t_to_max_speed + 0.5 * B * t_to_max_speed * t_to_max_speed
            return t_sum + t_to_max_speed + x0 / Car.MAX_SPEED

        # We run out of boost first
        x0 -= v0 * boost_dur + 0.5 * B * boost_dur * boost_dur
        v0 = v0 + B * boost_dur
        boost_dur = 0
        t_sum += boost_dur

    # CASE D: THR_MAX <= v0 < vmax and boost_dur == 0 (no accel)
    return t_sum + x0 / v0