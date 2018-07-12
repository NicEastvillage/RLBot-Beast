import math
import moves
import rlmath
import rlutility as rlu
import easing
import predict
import situation
import route
from vec import Vec3


class TouchBall:
    def utility(self, data):
        dist01 = rlu.dist_01(data.car.dist_to_ball)
        dist01 = 1 - easing.smooth_stop(4, dist01)

        possession = data.car.possession_score

        return easing.lerp(0.15, 0.85, dist01 * possession)

    def execute(self, data):
        ball_land_eta = max(predict.time_of_arrival_at_height(data.ball, 92.2).time, 0)
        ball_land_loc = predict.move_ball(data.ball.copy(), ball_land_eta).location
        drive_eta = ball_land_loc.dist(data.car.location) / 1410
        if drive_eta < ball_land_eta:
            bias = (ball_land_loc - situation.get_goal_location(data.enemy, data)).rescale(23)
            dest = ball_land_loc + bias
            data.renderer.draw_line_3d(data.car.location.tuple(), dest.tuple(),
                                       data.renderer.create_color(255, 255, 0, 255))
            return moves.go_towards_point_with_timing(data, dest, ball_land_eta, True)
        else:
            ball_loc2 = predict.move_ball(data.ball.copy(), drive_eta).location
            drive_eta = ball_loc2.dist(data.car.location) / 1410
            data.renderer.draw_line_3d(data.car.location.tuple(), ball_loc2.tuple(),
                                       data.renderer.create_color(255, 255, 0, 255))
            return moves.go_towards_point_with_timing(data, ball_loc2, drive_eta, True)


class KickOff:
    def utility(self, data):
        return data.packet.game_info.is_kickoff_pause

    def execute(self, data):
        data.renderer.draw_line_3d(data.car.location.tuple(), (0,0,0), data.renderer.create_color(255, 255, 255, 255))
        return moves.go_towards_point(data, Vec3(), False, True)


class SaveGoal:
    def __init__(self, agent):
        goal_dir = situation.get_goal_direction(agent, None)
        self.aim_corners = [
            Vec3(x=4000),
            Vec3(x=-4000),
            Vec3(x=4000, y=4900*goal_dir),
            Vec3(x=-4000, y=4900*goal_dir)
        ]

    def utility(self, data):
        ball_soon = predict.move_ball(data.ball.copy(), 1)
        ball_to_goal = situation.get_goal_location(data.car, None) - data.ball.location
        goal_dir = situation.get_goal_direction(data.car, None)

        ang = abs(ball_to_goal.angTo2d(data.ball.velocity))
        ang_01 = easing.fix(easing.lerp(math.pi*0.4, 0, ang))
        ang_01 = easing.smooth_stop(2, ang_01)
        own_half_01 = easing.fix(easing.remap((1-goal_dir)*situation.ARENA_LENGTH2, goal_dir*situation.ARENA_LENGTH2, 0.2, 1.4, ball_soon.location.y))

        return own_half_01 * ang_01

    def execute(self, data):
        best_route = None
        for target in self.aim_corners:
            r = route.find_route_to_next_ball_landing(data, target)
            route.draw_route(data.renderer, r)
            if r.good_route and (best_route is None or r.length < best_route.length):
                best_route = r

        if best_route is None:
            return moves.go_towards_point(data, data.ball.location, True, True)
        else:
            return moves.follow_route(data, best_route)


class CollectBoost:
    def __init__(self, agent):
        boost_choices = []
        for i, pad in enumerate(agent.get_field_info().boost_pads):
            boost_choices.append(SpecificBoostPad(pad, i))

        self.collect_boost_system = rlu.UtilitySystem(boost_choices, 0)

    def utility(self, data):
        boost01 = float(data.car.boost / 100.0)
        boost01 = 1 - easing.smooth_stop(4, boost01)

        best_boost = self.collect_boost_system.evaluate(data)
        time_est = rlmath.estimate_time_to_arrival(data.car, best_boost.location)
        time01 = 4 ** (-time_est)

        return easing.fix(boost01 * time01)

    def execute(self, data):
        return self.collect_boost_system.evaluate(data).execute(data)

    def reset(self):
        self.collect_boost_system.reset()


class SpecificBoostPad:
    def __init__(self, info, index):
        self.info = info
        self.index = index
        self.location = Vec3().set(info.location)

    def utility(self, data):
        car_to_pad = self.location - data.car.location_2d
        state = data.packet.game_boosts[self.index]

        dist = 1 - rlu.dist_01(data.car.location.dist(self.location))
        ang = rlu.face_ang_01(data.car.orientation.front.angTo2d(car_to_pad))
        active = state.is_active
        big = self.info.is_full_boost * 0.5

        return easing.fix(dist * ang + big) * active

    def execute(self, data):
        data.renderer.draw_line_3d(data.car.location.tuple(), self.location.tuple(), data.renderer.create_color(255, 0, 255, 0))
        return moves.go_towards_point(data, self.location, True, self.info.is_full_boost)
