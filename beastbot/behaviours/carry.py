import math

from rlbot_flatbuffers import ControllerState

from behaviours.utsystem import Choice
from maneuvers.dodge import DodgeManeuver
from utility import predict
from utility.rlmath import clip01, lerp
from utility.vec import norm, Vec3, angle_between, normalize, dot


class Carry(Choice):
    def __init__(self):
        self.is_dribbling = False
        self.flick_timer = 0

        # Constants
        self.extra_utility_bias = 0.2
        self.wait_before_flick = 0.28
        self.flick_init_jump_duration = 0.07
        self.required_distance_to_ball_for_flick = 173
        self.offset_bias = 38

    def utility(self, bot) -> float:
        car = bot.info.my_car
        ball = bot.info.ball

        car_to_ball = car.pos - ball.pos

        bouncing_b = ball.pos.z > 130 or abs(ball.vel.z) > 300
        if not bouncing_b:
            return 0

        dist_01 = clip01(1 - norm(car_to_ball) / 3000)

        head_dir = lerp(Vec3(0, 0, 1), car.forward, 0.1)
        ang = angle_between(head_dir, car_to_ball)
        ang_01 = clip01(1 - ang / (math.pi / 2))

        return clip01(0.6 * ang_01
                              + 0.4 * dist_01
                              #  - 0.3 * bot.analyzer.team_mate_has_ball_01
                              + self.is_dribbling * self.extra_utility_bias)

    def exec(self, bot) -> ControllerState:
        self.is_dribbling = True

        car = bot.info.my_car
        ball = bot.info.ball
        ball_landing = predict.next_ball_landing(bot)
        ball_to_goal = bot.info.enemy_goal - ball.pos

        # Decide on target pos and speed
        target = ball_landing.data["obj"].pos - self.offset_bias * normalize(ball_to_goal)
        dist = norm(target - bot.info.my_car.pos)
        speed = 1400 if ball_landing.time == 0 else dist / ball_landing.time

        # Do a flick?
        car_to_ball = ball.pos - car.pos
        dist = norm(car_to_ball)
        enemy, enemy_dist = bot.info.closest_enemy(ball.pos)
        if dist <= self.required_distance_to_ball_for_flick:
            self.flick_timer += bot.info.dt
            if self.flick_timer > self.wait_before_flick and enemy_dist < 900:
                bot.maneuver = DodgeManeuver(bot, bot.info.enemy_goal)  # use flick_init_jump_duration?
        else:
            self.flick_timer = 0

        if bot.do_rendering:
            bot.renderer.draw_line_3d(car.pos, target, bot.renderer.pink)

        return bot.drive.go_towards_point(bot, target, target_vel=speed, slide=False, can_keep_speed=False, can_dodge=True, wall_offset_allowed=0)

    def reset(self):
        self.is_dribbling = False
        self.flick_timer = 0
