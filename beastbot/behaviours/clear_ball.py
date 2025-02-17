import math

from rlbot_flatbuffers import ControllerState

from controllers.aim_cone import AimCone
from behaviours.utsystem import Choice
from utility import predict, rendering
from utility.info import Field
from utility.rlmath import clip01, remap, lerp
from utility.vec import Vec3


class ClearBall(Choice):
    def __init__(self, bot):
        if bot.team == 0:
            # blue
            ra = 0.85 * math.pi
            la = 0.15 * math.pi
            self.aim_cone = AimCone(
                Vec3(math.cos(ra), math.sin(ra), 0),
                Vec3(math.cos(la), math.sin(la), 0)
            )
        else:
            # orange
            ra = -0.15 * math.pi
            la = -0.85 * math.pi
            self.aim_cone = AimCone(
                Vec3(math.cos(ra), math.sin(ra), 0),
                Vec3(math.cos(la), math.sin(la), 0)
            )

    def utility(self, bot) -> float:
        team_sign = bot.info.team_sign

        length = team_sign * Field.LENGTH / 2
        ball_own_half_01 = clip01(remap(-length, length, -0.2, 1.2, bot.info.ball.pos.y))

        reachable_ball = predict.ball_predict(bot, predict.time_till_reach_ball(bot.info.my_car, bot.info.ball))
        car_to_ball = reachable_ball.pos - bot.info.my_car.pos
        in_position = self.aim_cone.contains_direction(car_to_ball, math.pi / 8)

        return ball_own_half_01 * in_position

    def exec(self, bot) -> ControllerState:
        car = bot.info.my_car
        shoot_controls = bot.shoot.with_aiming(bot, self.aim_cone, predict.time_till_reach_ball(bot.info.my_car, bot.info.ball))
        hit_pos = bot.shoot.ball_when_hit.pos

        if bot.do_rendering:
            self.aim_cone.draw(bot, hit_pos, r=0, g=170, b=255)

        if bot.shoot.can_shoot:
            if bot.shoot.using_curve and bot.do_rendering:
                rendering.draw_bezier(bot, [car.pos, bot.shoot.curve_point, hit_pos])
            return shoot_controls

        else:
            # go home-ish
            own_goal = lerp(bot.info.own_goal, bot.info.ball.pos, 0.5)
            return bot.drive.go_towards_point(bot, own_goal, target_vel=1460, slide=True, boost_min=0, can_keep_speed=True)
