from RLUtilities.LinearAlgebra import *

import moves
from rlmath import proj_onto_size


class KickOffPlan:
    def __init__(self):
        self.finished = False

    def execute(self, bot):
        my_pos = bot.info.my_car.pos

        bot.renderer.draw_line_3d(my_pos, (0, 0, 0), bot.renderer.create_color(255, 255, 255, 255))

        car_to_ball = -1 * my_pos
        dist = norm(car_to_ball)
        vel_f = proj_onto_size(bot.info.my_car.vel, car_to_ball)

        # Consider dodge - A dodge is strong around 0.25 seconds in, so what is the distance in 0.3 seconds?
        if dist - 190 < vel_f * 0.3 and bot.dodge_control.can_dodge(bot):
            bot.dodge_control.begin_dodge(bot, vec3(), True)
            bot.controls = bot.dodge_control.continue_dodge(bot)

        # Make two dodges when spawning far back
        elif dist > 3900 and vel_f > 730 and bot.dodge_control.can_dodge(bot):
            bot.dodge_control.begin_dodge(bot, vec3(), True)
            bot.controls = bot.dodge_control.continue_dodge(bot)

        # Pickup boost when spawning back corner
        elif abs(my_pos[0]) > 200 and abs(my_pos[2]) > 2880:
            # The pads location is about (0, 2816)
            # Force the car to go slightly closer to the x=0
            pad_loc = vec3(0, bot.tsgn * 2790, 0)
            bot.controls = moves.go_towards_point(bot, pad_loc, False, True)

        # Just drive towards (0, 0)
        else:
            bot.controls = moves.go_towards_point(bot, vec3(), False, True)

        # is done?
        if not bot.info.is_kickoff:
            self.finished = True
