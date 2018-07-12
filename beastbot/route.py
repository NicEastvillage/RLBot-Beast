import math
import situation
import predict
from situation import Data
from vec import Vec3


class Route:
    def __init__(self, points, final_loc, time_offset, expected_vel, car_loc):
        self.points = points
        self.final_loc = final_loc
        self.time_offset = time_offset
        self.expected_vel = expected_vel
        self.length = self.__find_length(car_loc, points)
        self.car_loc = car_loc

    def __find_length(self, car_loc, points):
        if len(points) < 1:
            return 0
        sum_len = 0
        prev_loc = car_loc
        for loc in points:
            sum_len += prev_loc.dist(loc)
            prev_loc = loc
        return sum_len


def find_route_to_next_ball_landing(data: Data, look_towards=None):
    car_to_ball = data.ball.location - data.car.location
    dist = car_to_ball.length()
    # vel_f = data.car.velocity.proj_onto_size(car_to_ball)
    drive_time = dist / 1410

    ball = data.ball.copy()

    predict.move_ball(ball, drive_time)
    time_hit = predict.next_ball_ground_hit(ball).time
    time_total = drive_time + time_hit

    return get_route_to_ball(data, time_total, look_towards)


def draw_route(renderer, route: Route, r=255, g=255, b=0):
    if len(route.points) < 1:
        return

    prev_loc_t = route.points[0].tuple()
    for loc in route.points[1:]:
        loc_t = loc.tuple()
        renderer.draw_line_3d(prev_loc_t, loc_t, renderer.create_color(255, r, g, b))
        prev_loc_t = loc_t


def get_route_to_ball(data: Data, time_offset=0, look_towards=None):
    dist_step_size = 1410 * 0.5
    max_turn_ang = math.pi * 0.3

    if look_towards is None:
        look_towards = situation.get_goal_location(data.enemy, data)

    ball = predict.move_ball(data.ball.copy(), time_offset)

    ball_init_loc = ball.location.in2D()
    ball_to_goal = look_towards - ball_init_loc
    if ball_to_goal.in2D().length2() == 0:
        ball_to_goal = situation.get_goal_location(data.enemy, data) - ball_init_loc

    ball_init_dir = ball_to_goal.in2D().normalized()*-1
    car_init_loc = data.car.location.in2D()

    steps_taken = 0
    ball_visited = []

    while steps_taken < 13:
        ball_cur_loc = ball_init_loc
        ball_cur_dir = ball_init_dir

        ball_visited = [ball_cur_loc]

        ball_to_car = car_init_loc - ball_cur_loc

        for i in range(steps_taken):
            ball_to_car = car_init_loc - ball_cur_loc
            ang_diff = ball_cur_dir.angTo2d(ball_to_car)
            ball_turn_dir = 1 if ang_diff > 0 else -1

            if i > 0:
                ball_cur_dir = ball_cur_dir.rotate_2d(max_turn_ang * ball_turn_dir)
            ball_cur_loc += ball_cur_dir * dist_step_size

            ball_visited.append(ball_cur_loc)

        ang_diff = ball_cur_dir.angTo2d(ball_to_car)

        if abs(ang_diff) < max_turn_ang or ball_to_car.length() < dist_step_size:
            break

        steps_taken += 1

    ball_visited.reverse()
    return Route(ball_visited, ball_init_loc, time_offset, 1410, car_init_loc)


def get_route(data: Data, destination, look_target):
    dist_step_size = 1410 * 0.5
    max_turn_ang = math.pi * 0.3

    destination = destination.in2D()
    dest_to_target = look_target.in2D() - destination
    dest_init_dir = dest_to_target.normalized() * -1
    car_init_loc = data.car.location.in2D()

    steps_taken = 0
    locs_visited = []

    while steps_taken < 13:
        cur_loc = destination
        cur_dir = dest_init_dir

        locs_visited = [cur_loc]

        dest_to_car = car_init_loc - cur_loc

        for i in range(steps_taken):
            dest_to_car = car_init_loc - cur_loc
            ang_diff = cur_dir.angTo2d(dest_to_car)
            turn_sgn = 1 if ang_diff > 0 else -1

            if i > 0:
                cur_dir = cur_dir.rotate_2d(max_turn_ang * turn_sgn)
            cur_loc += cur_dir * dist_step_size

            locs_visited.append(cur_loc)

        ang_diff = cur_dir.angTo2d(dest_to_car)

        if abs(ang_diff) < max_turn_ang or dest_to_car.length() < dist_step_size:
            break

        steps_taken += 1

    locs_visited.reverse()
    return Route(locs_visited, destination, 0, 1410, car_init_loc)
