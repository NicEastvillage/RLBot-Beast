from RLUtilities.Maneuvers import AirDodge

from rlmath import *

class DodgePlan:
    def __init__(self, bot, target=None):
        self.target = target
        self.dodge = AirDodge(bot.info.my_car, target=self._resolve_target())
        self.finished = False

    def _resolve_target(self):
        return self.target() if callable(self.target) else self.target

    def execute(self, bot):
        self.dodge.target = self._resolve_target()
        self.dodge.step(0.01666)
        bot.controls = self.dodge.controls
        self.finished = self.dodge.finished


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
        elif dist > 3900 and vel_p > 730:
            bot.drive.start_dodge()

        # Pickup boost when spawning back corner by driving a bit towards the middle boost pad first
        elif abs(car.pos[X]) > 200 and abs(car.pos[Y]) > 2880:
            # The pads exact location is (0, 2816), but don't have to be exact
            point[Y] = bot.info.team_sign * 2790

        bot.controls = bot.drive.go_towards_point(bot, point, target_vel=2300, slide=False, boost=True, can_dodge=False)
        self.finished = not bot.info.is_kickoff
