import math
import datalibs
import predict
from datalibs import Data
from vec import Vec3


class Route:
    def __init__(self, points, final_loc, time_offset, expected_vel, car_loc, good_route, high_end_vel):
        self.points = points
        self.final_loc = final_loc
        self.time_offset = time_offset
        self.expected_vel = expected_vel
        self.length = self.__find_length(car_loc, points)
        self.car_loc = car_loc
        self.good_route = good_route
        self.high_end_vel = high_end_vel

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
    vel_f = data.car.velocity.proj_onto_size(car_to_ball)
    drive_time = dist / max(1410, vel_f)

    ball = data.ball.copy()

    predict.move_ball(ball, drive_time)
    time_hit = predict.next_ball_ground_hit(ball).time
    time_total = drive_time + time_hit

    return get_route_to_ball(data, time_total, look_towards)


def draw_route(renderer, route: Route, r=255, g=255, b=0):
    if len(route.points) < 1:
        return

    prev_loc_t = route.car_loc.tuple()
    for loc in route.points:
        loc_t = loc.tuple()
        renderer.draw_line_3d(prev_loc_t, loc_t, renderer.create_color(255 if route.good_route else 50, r, g, b))
        prev_loc_t = loc_t


def get_route_to_ball(data: Data, time_offset=0, look_towards=None):
    dist_step_size = 1410 * 0.5
    max_turn_ang = math.pi * 0.3

    if look_towards is None:
        look_towards = datalibs.get_goal_location(data.enemy, data)

    ball = predict.move_ball(data.ball.copy(), time_offset)

    ball_init_loc = ball.location.in2D()
    ball_to_goal = look_towards - ball_init_loc
    if ball_to_goal.in2D().length2() == 0:
        ball_to_goal = datalibs.get_goal_location(data.enemy, data) - ball_init_loc

    ball_init_dir = ball_to_goal.in2D().normalized()*-1
    car_loc = data.car.location.in2D()
    ball_to_car = car_loc - ball_init_loc

    ang = ball_init_dir.angTo2d(ball_to_car)

    good_route = abs(ang) < math.pi/2
    if good_route:
        bx = ball_init_loc.x
        by = ball_init_loc.y
        cx = car_loc.x
        cy = car_loc.y
        dx = ball_init_dir.x
        dy = ball_init_dir.y

        t = - (bx*bx - 2*bx*cx + by*by - 2*by*cy + cx*cx + cy*cy) / (2*(bx*dx + by*dy - cx*dx - cy*dy))
        t = min(max(-1400, t), 1400)

        point = ball_init_loc + t * ball_init_dir

        point.x = min(max(-4030, point.x), 4030)
        point.y = min(max(-5090, point.y), 5090)

        return Route([point, ball_init_loc], ball_init_dir, 1, 1410, car_loc, good_route, False)

    else:
        point = car_loc + 700 * ball_init_dir
        return Route([point, ball_init_loc], ball_init_dir, 1, 1410, car_loc, good_route, False)


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

    good_route = True
    if steps_taken == 0:
        ang_diff = dest_init_dir.angTo2d(car_init_loc - destination)
        good_route = abs(ang_diff) < max_turn_ang / 4

    locs_visited.reverse()
    return Route(locs_visited, destination, 0, 1410, car_init_loc, good_route, True)
