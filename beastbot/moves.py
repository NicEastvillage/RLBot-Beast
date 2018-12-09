import time

from RLUtilities.Maneuvers import Drive
from RLUtilities.Simulation import Car
from rlbot.agents.base_agent import SimpleControllerState

from rlmath import *
from route import Route


class PIDControl:
    def __init__(self):
        self.last_error = 0

    def calc(self, error, p_strength=1, d_strength=5):
        derivative = error - self.last_error
        val = p_strength * error - d_strength * derivative + error ** 3
        self.last_error = error
        return min(max(-1, val), 1)


class DodgeControl:
    def __init__(self):
        self.is_dodging = False
        self.target = None
        self.boost = False
        self.controls = SimpleControllerState()
        self.last_start_time = time.time()
        self.last_end_time = time.time()

        self._t_first_unjump = 0.10
        self._t_aim = 0.13
        self._t_second_jump = 0.18
        self._t_second_unjump = 0.3
        self._t_wait_flip = 0.46
        self._t_finishing = 1.0  # fix orientation until lands on ground

        self._t_ready = 0.33  # time on ground before ready again
        self._max_speed = 1900
        self._boost_ang_req = 0.25

    def can_dodge(self, bot):
        return time.time() >= self.last_end_time + self._t_ready and bot.info.my_car.on_ground and not self.is_dodging

    def begin_dodge(self, bot, target, boost=False):
        if not self.can_dodge(bot):
            return

        self.is_dodging = True
        self.last_start_time = time.time()
        self.target = target
        self.boost = boost
        bot.ignore_ori_till = self.last_start_time + self._t_finishing

    def continue_dodge(self, bot) -> SimpleControllerState:
        ct = time.time()

        # target is allowed to be a function that takes bot as a parameter. Check what it is
        if callable(self.target):
            target = self.target(bot)
        else:
            target = self.target


        self.controls.throttle = 1
        self.controls.jump = False
        self.controls.pitch = 0
        self.controls.yaw = 0

        my_pos = bot.info.my_car.pos
        car_to_point = target - my_pos
        vel = proj_onto_size(bot.info.my_car.vel, car_to_point)
        face_ang = angle_between(car_to_point, bot.info.my_car.forward())
        self.controls.boost = self.boost and face_ang < self._boost_ang_req and vel < self._max_speed

        if ct >= self.last_start_time + self._t_finishing:
            if bot.info.my_car.on_ground:
                self.end_dodge()
            return fix_orientation(bot)

        elif ct >= self.last_start_time + self._t_wait_flip:
            pass

        elif ct >= self.last_start_time + self._t_second_unjump:
            pass

        elif ct >= self.last_start_time + self._t_aim:
            if ct >= self.last_start_time + self._t_second_jump:
                self.controls.jump = True

            car_to_point_u = norm(xy(car_to_point))
            car_forward = bot.info.my_car.forward()
            ang = math.atan2(car_forward[1], car_forward[0])
            car_to_point_rel = rotated_2d(car_to_point_u, -ang)
            self.controls.pitch = -car_to_point_rel.x
            self.controls.yaw = car_to_point_rel.y

        elif ct >= self.last_start_time + self._t_first_unjump:
            pass

        elif ct >= self.last_start_time:
            self.controls.jump = 1

        return self.controls

    def end_dodge(self):
        self.last_end_time = time.time()
        self.is_dodging = False
        self.target = None
        self.boost = False


# ----------------------------------- Executors ---------------------------------------


def go_towards_point(bot, point: vec3, target_vel=1430, slide=False, boost=False, get_down=True, can_keep_speed=True) -> SimpleControllerState:
    REQUIRED_SLIDE_ANG = 1.65

    controls = SimpleControllerState()

    car = bot.info.my_car

    # Get down from wall by choosing a point
    if get_down and angle_between(car.up(), vec3(0, 0, 1)) < math.pi * 0.31:
        point = lerp(xy(car.pos), xy(point), 0.5)

    car_to_point = point - car.pos

    # The vector from the car to the point in local coordinates:
    # point_local[0]: how far in front of my car
    # point_local[1]: how far to the left of my car
    # point_local[2]: how far above my car
    point_local = dot(point.pos - car.pos, car.theta)

    # Angle to point in local xy plane
    angle = math.atan2(point_local[1], point_local[0])
    dist = norm(point_local)
    vel_towards_point = proj_onto_size(car.vel, car_to_point)

    # Is in turn radius deadzone?
    tr = turn_radius(abs(vel_towards_point + 50))  # small bias
    tr_side = -1 * sign(angle)
    tr_center_local = vec3(0, tr * tr_side, 0)
    point_is_in_turn_radius_deadzone = norm(point - tr_center_local) < tr

    if point_is_in_turn_radius_deadzone:
        # Hard turn
        controls.throttle = 0 if vel_towards_point > 250 else 0.2
        controls.steer = sign(angle)

    else:
        # Should drop speed or just keep up the speed?
        if can_keep_speed and target_vel < vel_towards_point:
            target_vel = vel_towards_point

        # Turn and maybe slide
        controls.steer = clip(angle * 2.5, -1.0, 1.0)
        if slide and dist > 300 and abs(angle) > REQUIRED_SLIDE_ANG:
            controls.handbrake = True
            controls.steer = sign(angle)

        # Overshoot target vel for quick adjustment
        target_vel = lerp(vel_towards_point, target_vel, 1.2)

        # Find appropriate throttle/boost
        if vel_towards_point < target_vel:
            controls.throttle = 1
            if boost and vel_towards_point + 25 < target_vel \
                    and not controls.handbrake and is_heading_towards2(angle, dist):

                controls.boost = True

        else:
            vel_delta = target_vel - vel_towards_point
            controls.throttle = clip(vel_delta / 300, -1, 1)

    return controls


def fix_orientation(bot, point: vec3=None):
    controller = SimpleControllerState()

    strength = 0.22
    car = bot.info.my_car
    vel_2d = xy(car.vel)
    omega = car.omega

    if point is None and norm(vel_2d) != 0:
        point = bot.info.my_car.pos + normalize(vel_2d) * 200

    pitch_error = -omega[1] * strength
    controller.pitch = bot.pid_pitch.calc(pitch_error)

    roll_error = -omega[2] * strength
    controller.roll = bot.pid_roll.calc(roll_error)

    if point is not None:
        # yaw rotation can f up the other's so we scale it down until we are more confident about landing on the wheels
        car_to_point = point - car.pos
        yaw_error = angle_between(xy(car.forward()), xy(car_to_point)) * strength * 1.5
        land_on_wheels01 = 1 - angle_between(car.up(), vec3(0, 0, 1)) / (math.pi * 2)
        controller.yaw = data.agent.pid_yaw.calc(yaw_error) * (land_on_wheels01**6)

    # !
    controller.throttle = 1
    return controller


def consider_dodge(bot, point, min_dist=1000) -> bool:
    if bot.dodge_control.can_dodge(bot):
        car = bot.info.my_car
        car_to_point = point - car.pos
        point_local = dot(point.pos - car.pos, car.theta)
        angle = math.atan2(point_local[1], point_local[0])
        vel_f = proj_onto_size(car.vel, car_to_point)
        dist = norm(point_local)
        req_dist = max(min_dist, vel_f + 700)  # TODO Find dodge impulse size

        if 400 < vel_f < 2200 and req_dist < dist and is_heading_towards2(angle, dist):
            boost = car.boost > 40 and dist > 4000
            bot.dodge_control.begin_dodge(bot, point, boost)
            return True

    return False


def go_to_and_stop(bot, point: vec3, target_vel=1430, slide=False, boost=False, get_down=True, can_keep_speed=True) -> SimpleControllerState:

    car = bot.info.my_car
    point_local = dot(point.pos - car.pos, car.theta)
    angle = math.atan2(point_local[1], point_local[0])
    dist = norm(point_local)

    controls = go_towards_point(bot, point, target_vel, slide, boost, get_down, can_keep_speed)

    if not is_heading_towards2(angle, dist):
        return controls

    vel_f = proj_onto_size(car.vel, car.forward())
    ex_brake_dist = (vel_f**2) / 2800

    if dist < ex_brake_dist:
        controls.throttle = -1
    if dist < ex_brake_dist * 1.5:
        controls.boost = False

    return controls


def stop_moving(bot):
    if not bot.info.my_car.on_ground:
        return fix_orientation(bot)

    controller_state = SimpleControllerState()

    # We are on the ground. Now negate all velocity
    vel_f = proj_onto_size(bot.info.my_car.vel, bot.info.my_car.forward())
    if abs(vel_f) > 200:
        controller_state.throttle = -sign(vel_f)

    return controller_state


# TODO Not sure if this works
def jump_to_face(bot, point, allowed_angle=0.4, stop=True):
    if stop and norm(bot.info.my_car.vel) > 50:
        return stop_moving(bot)

    point_local = dot(point.pos - bot.info.my_car.pos, bot.info.my_car.theta)
    angle_local = math.atan2(point_local[1], point_local[0])
    if angle_local < allowed_angle:
        return SimpleControllerState()

    if bot.info.my_car.on_ground:
        controller_state = SimpleControllerState()
        controller_state.jump = 1
        return controller_state

    return fix_orientation(bot, point)


# ----------------------------------------- Helper functions --------------------------------


def is_heading_towards(car: Car, point: vec3):
    point_local = dot(point.pos - car.pos, car.theta)
    angle = math.atan2(point_local[1], point_local[0])
    dist = norm(point_local)
    return is_heading_towards2(angle, dist)


def is_heading_towards2(ang, dist):
    # The further away the car is the less accurate the angle is required
    required_ang = 0.05 + 0.0001 * dist
    return abs(ang) <= required_ang


def turn_radius(v):
    if v == 0:
        return 0
    return 1.0 / kappa(v)


def kappa(v):
    if 0.0 <= v < 500.0:
        return 0.006900 - 5.84e-6 * v
    elif 500.0 <= v < 1000.0:
        return 0.005610 - 3.26e-6 * v
    elif 1000.0 <= v < 1500.0:
        return 0.004300 - 1.95e-6 * v
    elif 1500.0 <= v < 1750.0:
        return 0.003025 - 1.10e-6 * v
    elif 1750.0 <= v < 2500.0:
        return 0.001800 - 0.40e-6 * v
    else:
        return 0.0
