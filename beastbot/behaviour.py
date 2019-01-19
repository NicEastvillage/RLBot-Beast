from RLUtilities.Simulation import Car, Input

import predict
from moves import AimCone
from plans import DodgePlan
from rlmath import *


class Carry:
    def __init__(self):
        self.is_dribbling = False
        self.flick_timer = 0

        # Constants
        self.extra_utility_bias = 0.2
        self.wait_before_flick = 0.26
        self.flick_init_jump_duration = 0.07
        self.required_distance_to_ball_for_flick = 173
        self.offset_bias = 36

    def utility(self, bot):
        car = bot.info.my_car
        ball = bot.info.ball

        car_to_ball = car.pos - ball.pos

        bouncing_b = ball.pos[Z] > 130 or abs(ball.vel[Z]) > 300
        if not bouncing_b:
            return 0

        dist_01 = clip01(1 - norm(car_to_ball) / 3000)

        head_dir = lerp(vec3(0, 0, 1), car.forward(), 0.1)
        ang = angle_between(head_dir, car_to_ball)
        ang_01 = clip01(1 - ang / (math.pi / 2))

        return clip01(0.6 * ang_01
                              + 0.4 * dist_01
                              #  - 0.3 * bot.analyzer.team_mate_has_ball_01
                              + self.is_dribbling * self.extra_utility_bias)

    def execute(self, bot):
        self.is_dribbling = True

        car = bot.info.my_car
        ball = bot.info.ball
        ball_landing = predict.next_ball_landing(bot)
        ball_to_goal = bot.info.enemy_goal - ball.pos

        # Decide on target pos and speed
        target = ball_landing.data["pos"] - self.offset_bias * normalize(ball_to_goal)
        dist = norm(target - bot.info.my_car.pos)
        speed = 1400 if ball_landing.time == 0 else dist / ball_landing.time

        # Do a flick?
        car_to_ball = ball.pos - car.pos
        dist = norm(car_to_ball)
        if dist <= self.required_distance_to_ball_for_flick:
            self.flick_timer += 0.016666
            if self.flick_timer > self.wait_before_flick:
                bot.plan = DodgePlan(bot.info.enemy_goal)  # use flick_init_jump_duration?
        else:
            self.flick_timer = 0

            # dodge on far distances
            if dist > 2450 and speed > 1410:
                ctt_n = normalize(target - car.pos)
                vtt = dot(bot.info.my_car.vel, ctt_n) / dot(ctt_n, ctt_n)
                if vtt > 750:
                    bot.plan = DodgePlan(target)

        controls = bot.drive.go_towards_point(bot, target, target_vel=speed, slide=False, boost=False, can_keep_speed=False, can_dodge=True, wall_offset_allowed=0)
        bot.controls = controls

        if bot.do_rendering:
            bot.renderer.draw_line_3d(car.pos, target, bot.renderer.pink())

    def reset(self):
        self.is_dribbling = False
        self.flick_timer = 0


class ShootAtGoal:
    def __init__(self):
        self.aim_cone = None
        self.ball_to_goal_right = None
        self.ball_to_goal_left = None

    def utility(self, bot):
        ball_soon = predict.ball_predict(bot, 1)

        arena_length2 = bot.info.team_sign * FIELD_LENGTH / 2
        own_half_01 = clip01(remap(arena_length2, -arena_length2, 0.0, 1.1, ball_soon.pos[Y]))

        reachable_ball = predict.ball_predict(bot, predict.time_till_reach_ball(bot.info.my_car, bot.info.ball))
        self.ball_to_goal_right = bot.info.enemy_goal_right - reachable_ball.pos
        self.ball_to_goal_left = bot.info.enemy_goal_left - reachable_ball.pos
        self.aim_cone = AimCone(self.ball_to_goal_right, self.ball_to_goal_left)
        car_to_ball = reachable_ball.pos - bot.info.my_car.pos
        in_position = self.aim_cone.contains_direction(car_to_ball)

        return clip01(own_half_01 + 0.1 * in_position)

    def execute(self, bot):

        car_now = bot.info.my_car
        ball_now = bot.info.ball

        reach_time = predict.time_till_reach_ball(car_now, ball_now)
        reachable_ball = predict.ball_predict(bot, reach_time)
        car_to_rball = reachable_ball.pos - car_now.pos

        # Check if close enough to dodge. A dodge happens after 0.3 sec
        ball_soon_pos = predict.ball_predict(bot, 0.25).pos
        car_soon = Car(car_now)
        car_soon.step(Input(), 0.25)
        car_to_ball_soon = ball_soon_pos - car_soon.pos

        # Aim cone was calculated in utility
        if norm(car_to_ball_soon) < 240 + BALL_RADIUS and self.aim_cone.contains_direction(car_to_ball_soon):
            bot.drive.start_dodge()

        goto, goto_time = self.aim_cone.get_goto_point(bot, car_now.pos, reachable_ball.pos)
        dist = norm(car_to_rball)

        self.aim_cone.draw(bot, reachable_ball.pos, b=0)
        if goto is None or dist < 450:

            # Avoid enemy corners. Just wait
            if reachable_ball.pos[Y] * -bot.info.team_sign > 4350 and abs(reachable_ball.pos[X]) > 900 and not dist < 450:
                wait_point = reachable_ball.pos * 0.5  # a point 50% closer to the center of the field
                wait_point = lerp(wait_point, ball_now.pos + vec3(0, bot.info.team_sign * 3000, 0), 0.5)
                bot.renderer.draw_line_3d(car_now.pos, wait_point, bot.renderer.yellow())
                bot.controls = bot.drive.go_towards_point(bot, wait_point, norm(car_now.pos - wait_point), slide=True, boost=False, can_keep_speed=True, can_dodge=False)
                return

            if is_closer_to_goal_than(car_now.pos, ball_now.pos, bot.info.team):

                # Chase
                goal_to_ball = normalize(reachable_ball.pos - bot.info.enemy_goal)
                offset_ball = reachable_ball.pos + goal_to_ball * BALL_RADIUS
                bot.renderer.draw_line_3d(car_now.pos, offset_ball, bot.renderer.yellow())
                bot.controls = bot.drive.go_towards_point(bot, offset_ball, target_vel=2200, slide=False, boost=True)
                return

            else:
                # return home
                bot.controls = bot.drive.go_towards_point(bot, bot.info.own_goal, target_vel=2200, slide=True, boost=norm(car_now.vel) < 1800, can_keep_speed=True)
                return
        else:
            # Shoot !
            speed = dist / (reach_time * goto_time * 0.95)
            bot.controls = bot.drive.go_towards_point(bot, goto, target_vel=speed, slide=True, boost=True, can_keep_speed=False)
            return


class ClearBall:
    def __init__(self, bot):
        if bot.team == 0:
            # blue
            self.aim_cone = AimCone(.8 * math.pi, .2 * math.pi)
        else:
            # orange
            self.aim_cone = AimCone(-.1 * math.pi, -.9 * math.pi)

    def utility(self, bot):
        team_sign = bot.info.team_sign

        length = team_sign * FIELD_LENGTH / 2
        ball_own_half_01 = clip01(remap(-length, length, -0.2, 1.2, bot.info.ball.pos[Y]))

        reachable_ball = predict.ball_predict(bot, predict.time_till_reach_ball(bot.info.my_car, bot.info.ball))
        car_to_ball = reachable_ball.pos - bot.info.my_car.pos
        in_position = self.aim_cone.contains_direction(car_to_ball)

        return ball_own_half_01 * in_position

    def execute(self, bot):
        reach_time = predict.time_till_reach_ball(bot.info.my_car, bot.info.ball)
        reachable_ball = predict.ball_predict(bot, reach_time)
        goto, goto_time = self.aim_cone.get_goto_point(bot, bot.info.my_car.pos, reachable_ball.pos)

        self.aim_cone.draw(bot, reachable_ball.pos, r=0, g=170, b=255)

        if goto is None:
            # go home-ish
            own_goal = lerp(bot.info.own_goal, bot.info.ball.pos, 0.5)
            bot.controls = bot.drive.go_towards_point(bot, own_goal, target_vel=1460, slide=True, boost=True, can_keep_speed=True)
        else:
            dist = norm(bot.info.my_car.pos - reachable_ball.pos)
            speed = dist / (reach_time * goto_time)
            bot.controls = bot.drive.go_towards_point(bot, goto, target_vel=speed, slide=True, boost=True, can_keep_speed=False)
