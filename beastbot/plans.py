import time

from RLUtilities.Maneuvers import AerialTurn
from rlbot.agents.base_agent import SimpleControllerState

from rlmath import *


class DodgePlan:
    def __init__(self, target=None, boost=False):
        self.target = target
        self.boost = boost
        self.controls = SimpleControllerState()
        self.start_time = time.time()
        self.finished = False
        self.almost_finished = False

        self._t_first_unjump = 0.10
        self._t_aim = 0.13
        self._t_second_jump = 0.18
        self._t_second_unjump = 0.46
        self._t_finishing = 1.0  # After this, Fix orientation until lands on ground

        self._t_steady_again = 0.25  # Time on ground before steady and ready again
        self._max_speed = 2000  # Don't boost if above this speed
        self._boost_ang_req = 0.25

    def execute(self, bot):
        ct = time.time() - self.start_time

        # Target is allowed to be a function that takes bot as a parameter. Check what it is
        if callable(self.target):
            target = self.target(bot)
        else:
            target = self.target

        # Get car and reset controls
        car = bot.info.my_car
        self.controls.throttle = 1
        self.controls.yaw = 0
        self.controls.pitch = 0
        self.controls.jump = False

        # To boost or not to boost, that is the question
        car_to_target = target - car.pos
        vel_p = proj_onto_size(car.vel, car_to_target)
        angle = angle_between(car_to_target, car.forward())
        self.controls.boost = self.boost and angle < self._boost_ang_req and vel_p < self._max_speed

        # States of dodge (note reversed order)
        # Land on ground
        if ct >= self._t_finishing:
            self.almost_finished = True
            if car.on_ground:
                self.finished = True
            # TODO return fix_orientation(data)
            return self.controls

        elif ct >= self._t_second_unjump:
            # Stop pressing jump and rotate and wait for flip is done
            pass

        elif ct >= self._t_aim:
            if ct >= self._t_second_jump:
                self.controls.jump = 1

            # Direction, yaw, pitch, roll
            if self.target is None:
                self.controls.roll = 0
                self.controls.pitch = -1
                self.controls.yaw = 0
            else:
                target_local = dot(car_to_target, car.theta)
                target_local[Z] = 0

                direction = normalize(target_local)

                self.controls.roll = 0
                self.controls.pitch = -direction[X]
                self.controls.yaw = sign(car.theta[2, 2]) * direction[Y]

        # Stop pressing jump
        elif ct >= self._t_first_unjump:
            pass

        # First jump
        else:
            self.controls.jump = 1

        return self.controls


class KickoffPlan:
    def __init__(self):
        self.finished = False

    def execute(self, bot):
        DODGE_DIST = 190

        # Since ball is at (0,0) we don't we a car_to_ball variable like we do so many other places
        car = bot.info.my_car
        dist = norm(car.pos)
        vel_p = -proj_onto_size(car.vel, car.pos)

        point = vec3(0, 0, 0)

        # Dodge when close to (0, 0). The dodge itself should happen in about 0.3 seconds
        if dist - DODGE_DIST < vel_p * 0.3:
            bot.drive.start_dodge()

        # Make two dodges when spawning far back
        elif dist > 3900 and vel_p > 780:
            bot.drive.start_dodge()

        # Pickup boost when spawning back corner by driving a bit towards the middle boost pad first
        elif abs(car.pos[X]) > 200 and abs(car.pos[Y]) > 2880:
            # The pads exact location is (0, 2816), but don't have to be exact
            point[Y] = bot.info.team_sign * 2790

        bot.controls = bot.drive.go_towards_point(bot, point, target_vel=2300, slide=False, boost=True, can_dodge=False)
        self.finished = not bot.info.is_kickoff


class RecoverPlan:
    def __init__(self):
        self.finished = False
        self.aerialturn = None

    def execute(self, bot):
        if self.aerialturn is None:
            self.aerialturn = AerialTurn(bot.info.my_car)

        self.aerialturn.step(0.01666)
        bot.controls = self.aerialturn.controls
        self.finished = self.aerialturn.finished
