import math
import moves
import rlmath
import rlutility as rlu
import easing
import predict
import datalibs
import route
from vec import Vec3

from rlbot.agents.base_agent import SimpleControllerState


class Dribbling:
    def utility(self, data):
        # every 1500 is 0.1
        enemy_dist = data.enemy.location.dist(data.ball.location)
        enemy_dist_u = enemy_dist * 0.00006

        dist01 = rlu.dist_01(data.car.dist_to_ball)
        dist01 = 1 - easing.smooth_stop(4, dist01)

        car_to_ball = data.ball.location - data.car.location
        above_ang = car_to_ball.ang_to(Vec3(z=1))
        aa01 = easing.fix(1 - 1.5 * above_ang / math.pi)

        return easing.fix(0.76 * aa01 + enemy_dist_u) * (data.ball.location.z > 25)

    def execute(self, data):
        ball_land_eta = max(predict.time_of_arrival_at_height(data.ball, datalibs.BALL_RADIUS + 1).time, 0)
        ball_land_loc = predict.move_ball(data.ball.copy(), ball_land_eta).location

        bias = (ball_land_loc - datalibs.get_goal_location(data.enemy, data)).rescale(20)
        dest = ball_land_loc + bias
        data.renderer.draw_line_3d(data.car.location.tuple(), dest.tuple(), data.renderer.create_color(255, 255, 0, 255))
        data.renderer.draw_line_3d(data.ball.location.tuple(), dest.tuple(), data.renderer.create_color(255, 255, 0, 255))
        return moves.go_towards_point_with_timing(data, dest, ball_land_eta, True)

    def __str__(self):
        return "Dribble"


class KickOff:
    def utility(self, data):
        return data.packet.game_info.is_kickoff_pause * 2

    def execute(self, data):
        data.renderer.draw_line_3d(data.car.location.tuple(), (0, 0, 0), data.renderer.create_color(255, 255, 255, 255))
        return moves.go_towards_point(data, Vec3(), False, True)

    def __str__(self):
        return "KickOff"


class ShootAtGoal:
    def __init__(self, agent):
        goal_dir = - datalibs.get_goal_direction(agent, None)
        self.aim_corners = [
            Vec3(x=720, y=5100 * goal_dir),
            Vec3(x=-720, y=5100 * goal_dir),
            Vec3(y=5200 * goal_dir),
            Vec3(y=5700 * goal_dir)
        ]

    def utility(self, data):
        ball_soon = predict.move_ball(data.ball.copy(), 1)
        goal_dir = datalibs.get_goal_direction(data.car, None)

        own_half_01 = easing.fix(easing.remap(goal_dir * datalibs.ARENA_LENGTH2, (-1 * goal_dir) * datalibs.ARENA_LENGTH2, 0.0, 1.1, ball_soon.location.y))

        return own_half_01

    def execute(self, data):
        best_route = None
        for target in self.aim_corners:
            r = route.find_route_to_next_ball_landing(data, target)
            if best_route is None\
                    or (not best_route.good_route and (r.good_route or r.length < best_route.length))\
                    or (r.length < best_route.length and r.good_route):

                best_route = r

        return moves.follow_route(data, best_route)

    def __str__(self):
        return "ShootAtGoal"

class ClearBall:
    def __init__(self, agent):
        goal_dir = - datalibs.get_goal_direction(agent, None)
        self.aim_corners = [
            Vec3(x=4000, y=300*goal_dir),
            Vec3(x=-4000, y=300*goal_dir),
            Vec3(x=2000, y=2500*goal_dir),
            Vec3(x=-2000, y=2500*goal_dir),
            Vec3(y=5000*goal_dir)
        ]

    def utility(self, data):
        my_goal_dir = datalibs.get_goal_direction(data.car, None)
        goal_to_ball = data.ball.location - datalibs.get_goal_location(data.car, None)
        car_to_ball = data.ball.location - data.car.location

        ang = abs(car_to_ball.ang_to_flat(goal_to_ball))
        ang_01 = easing.fix(easing.lerp(math.pi * 0.6, 0, ang))
        ang_01 = easing.smooth_stop(2, ang_01)
        own_half_01 = easing.fix(easing.remap((-1*my_goal_dir) * datalibs.ARENA_LENGTH2, my_goal_dir * datalibs.ARENA_LENGTH2, -0.2, 1.2, data.ball.location.y))

        return own_half_01 * ang_01

    def execute(self, data):
        best_route = None
        for target in self.aim_corners:
            r = route.find_route_to_next_ball_landing(data, target)
            if best_route is None\
                    or (not best_route.good_route and (r.good_route or r.length < best_route.length))\
                    or (r.length < best_route.length and r.good_route):

                best_route = r

        return moves.follow_route(data, best_route)

    def __str__(self):
        return "ClearBall"


class SaveGoal:
    def __init__(self, agent):
        goal_dir = datalibs.get_goal_direction(agent, None)
        self.aim_corners = [
            Vec3(x=4000),
            Vec3(x=-4000),
            Vec3(x=4000, y=3000*goal_dir),
            Vec3(x=-4000, y=3000*goal_dir),
            Vec3(x=1900, y=4900*goal_dir),
            Vec3(x=-1900, y=4900*goal_dir),
            Vec3(x=4000, y=4900*goal_dir),
            Vec3(x=-4000, y=4900*goal_dir)
        ]

    def utility(self, data):
        ball_soon = predict.move_ball(data.ball.copy(), 1)
        ball_to_goal = datalibs.get_goal_location(data.car, None) - data.ball.location
        goal_dir = datalibs.get_goal_direction(data.car, None)

        ang = abs(ball_to_goal.ang_to_flat(data.ball.velocity))
        ang_01 = easing.fix(easing.lerp(math.pi*0.4, 0, ang))
        ang_01 = easing.smooth_stop(2, ang_01)
        own_half_01 = easing.fix(easing.remap((-1*goal_dir) * datalibs.ARENA_LENGTH2, goal_dir * datalibs.ARENA_LENGTH2, 0, 1.4, data.ball.location.y))

        return easing.fix(0.5*own_half_01 + 0.5*own_half_01 * ang_01)

    def execute(self, data):
        best_route = None
        for target in self.aim_corners:
            r = route.find_route_to_next_ball_landing(data, target)
            if best_route is None\
                    or (not best_route.good_route and (r.good_route or r.length < best_route.length))\
                    or (r.length < best_route.length and r.good_route):

                best_route = r

        return moves.follow_route(data, best_route)

    def __str__(self):
        return "SaveGoal"


class CollectBoost:
    def __init__(self, agent):
        self.collect_boost_system = None
        self.init_array(agent)

    def init_array(self, agent):
        boost_choices = []
        for i, pad in enumerate(agent.get_field_info().boost_pads):
            if i >= agent.get_field_info().num_boosts:
                break
            boost_choices.append(SpecificBoostPad(pad, i))

        self.collect_boost_system = rlu.UtilitySystem(boost_choices, 0)

    def utility(self, data):
        if data.car.boost == 0:
            return -0.5
        boost01 = float(data.car.boost / 100.0)
        boost01 = 1 - easing.smooth_stop(4, boost01)

        # best_boost = self.collect_boost_system.evaluate(data)

        return easing.fix(boost01)

    def execute(self, data):
        try:
            return self.collect_boost_system.evaluate(data).execute(data)
        except ValueError:
            self.init_array(data.agent)
            return SimpleControllerState()

    def reset(self):
        self.collect_boost_system.reset()

    def __str__(self):
        return "CollectBoost"


class SpecificBoostPad:
    def __init__(self, info, index):
        self.info = info
        self.index = index
        self.location = Vec3().set(info.location)

    def utility(self, data):
        car_to_pad = self.location - data.car.location_2d
        state = data.packet.game_boosts[self.index]

        dist = 1 - rlu.dist_01(data.car.location.dist(self.location))
        ang = rlu.face_ang_01(data.car.orientation.front.ang_to_flat(car_to_pad))
        active = state.is_active
        big = self.info.is_full_boost * 0.5

        return easing.fix(dist * ang + big) * active

    def execute(self, data):
        data.renderer.draw_line_3d(data.car.location.tuple(), self.location.tuple(), data.renderer.create_color(255, 0, 180, 0))
        return moves.go_towards_point(data, self.location, True, self.info.is_full_boost)

class FixAirOrientation:
    def utility(self, data):
        return not data.car.wheel_contact

    def execute(self, data):
        return moves.fix_orientation(data)

    def __str__(self):
        return "LandOnWheels"
