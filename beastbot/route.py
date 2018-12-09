import math
import rlmath
import datalibs
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


def find_route_to_next_ball_landing(data, look_towards=None):
    car_to_ball = data.ball.location - data.car.location
    dist = car_to_ball.length()
    vel_f = data.car.velocity.proj_onto_size(car_to_ball)
    drive_time = dist / max(1410, vel_f)

    ball = data.ball

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


def get_route_to_ball(data, time_offset=0, look_towards=None):
    dist_step_size = 1410 * 0.5
    max_turn_ang = math.pi * 0.3

    if look_towards is None:
        look_towards = datalibs.get_goal_location(data.enemy, data)

    ball = predict.move_ball(data.ball.copy(), time_offset)

    ball_init_loc = ball.location.flat()
    ball_to_goal = look_towards - ball_init_loc
    if ball_to_goal.flat().length2() == 0:
        ball_to_goal = datalibs.get_goal_location(data.enemy, data) - ball_init_loc

    ball_init_dir = ball_to_goal.flat().normalized() * -1
    car_loc = data.car.location.flat()
    ball_to_car = car_loc - ball_init_loc

    ang = ball_init_dir.ang_to_flat(ball_to_car)

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


def get_route(data, destination, look_target):
    dist_step_size = 1410 * 0.5
    max_turn_ang = math.pi * 0.3

    destination = destination.flat()
    dest_to_target = look_target.flat() - destination
    dest_init_dir = dest_to_target.normalized() * -1
    car_init_loc = data.car.location.flat()

    steps_taken = 0
    locs_visited = []

    while steps_taken < 13:
        cur_loc = destination
        cur_dir = dest_init_dir

        locs_visited = [cur_loc]

        dest_to_car = car_init_loc - cur_loc

        for i in range(steps_taken):
            dest_to_car = car_init_loc - cur_loc
            ang_diff = cur_dir.ang_to_flat(dest_to_car)
            turn_sgn = 1 if ang_diff > 0 else -1

            if i > 0:
                cur_dir = cur_dir.rotate_2d(max_turn_ang * turn_sgn)
            cur_loc += cur_dir * dist_step_size

            locs_visited.append(cur_loc)

        ang_diff = cur_dir.ang_to_flat(dest_to_car)

        if abs(ang_diff) < max_turn_ang or dest_to_car.length() < dist_step_size:
            break

        steps_taken += 1

    good_route = True
    if steps_taken == 0:
        ang_diff = dest_init_dir.ang_to_flat(car_init_loc - destination)
        good_route = abs(ang_diff) < max_turn_ang / 4

    locs_visited.reverse()
    return Route(locs_visited, destination, 0, 1410, car_init_loc, good_route, True)


class AimCone:
    def __init__(self, right_most_ang, left_most_ang):
        self.right_ang = rlmath.fix_ang(right_most_ang)
        self.left_ang = rlmath.fix_ang(left_most_ang)
        self.right_dir = Vec3(math.cos(right_most_ang), math.sin(right_most_ang))
        self.left_dir = Vec3(math.cos(left_most_ang), math.sin(left_most_ang))

    def contains_direction(self, direction):
        # If you stand in blue goal and look at orange goal. positive y is forwards and positive x is left
        # This f up angles too, so all < or > are probably the opposite of what you would expect
        # Also, I don't know why both is not'ed
        ang = direction.ang()
        if self.right_ang < self.left_ang:
            return not (self.right_ang >= ang or ang >= self.left_ang)
        else:
            return not (self.right_ang >= ang >= self.left_ang)

    def span_size(self):
        if self.right_ang < self.left_ang:
            return math.tau + self.right_ang - self.left_ang
        else:
            return self.right_ang - self.left_ang

    def get_center_ang(self):
        return rlmath.fix_ang(self.right_ang - self.span_size() / 2)

    def get_center_dir(self):
        ang = self.get_center_ang()
        return Vec3(math.cos(ang), math.sin(ang))

    def get_goto_point(self, data, point):
        point = point.flat()
        desired_dir = self.get_center_dir()

        desired_dir_inv = -1 * desired_dir
        car_loc = data.car.location.flat()
        point_to_car = car_loc - point
        dist = point_to_car.length()

        ang_to_desired_dir = desired_dir_inv.ang_to_flat(point_to_car)

        ANG_ROUTE_ACCEPTED = math.pi / 5.0
        can_go_straight = abs(ang_to_desired_dir) < self.span_size() / 2.0
        can_with_route = abs(ang_to_desired_dir) < self.span_size() / 2.0 + ANG_ROUTE_ACCEPTED
        point = point + desired_dir_inv * 50
        if can_go_straight:
            return point, 1.0
        elif can_with_route:
            ang_to_right = abs(point_to_car.ang_to_flat(-1*self.right_dir))
            ang_to_left = abs(point_to_car.ang_to_flat(-1*self.left_dir))
            closest_dir = self.right_dir if ang_to_right < ang_to_left else self.left_dir

            bx = point.x
            by = point.y
            cx = car_loc.x
            cy = car_loc.y
            dx = closest_dir.x
            dy = closest_dir.y

            t = - (bx * bx - 2 * bx * cx + by * by - 2 * by * cy + cx * cx + cy * cy) / (
                        2 * (bx * dx + by * dy - cx * dx - cy * dy))
            t = min(max(-1700, t), 1700)

            goto = point + 0.8 * t * closest_dir

            goto.x = min(max(-4030, goto.x), 4030)
            goto.y = min(max(-5090, goto.y), 5090)

            data.renderer.draw_line_3d(data.car.location.tuple(), goto.tuple(), data.renderer.create_color(255, 150, 150, 150))
            data.renderer.draw_line_3d(point.tuple(), goto.tuple(), data.renderer.create_color(255, 150, 150, 150))
            return goto, 0.5
        else:
            return None, 1

    def draw(self, renderer, center, arm_len=500, arm_count=5, r=255, g=255, b=255):
        center = center.flat()
        c_tup = center.tuple()
        ang_step = self.span_size() / (arm_count - 1)

        for i in range(arm_count):
            ang = self.right_ang - ang_step * i
            arm_dir = Vec3(math.cos(ang), math.sin(ang))
            end = center + arm_dir * arm_len
            renderer.draw_line_3d(c_tup, end.tuple(),
                                  renderer.create_color(255 if i == 0 or i == arm_count - 1 else 110, r, g, b))


def debug_aim_cone(data):
    ball_loc = data.ball.location
    own_post_right, own_post_left = datalibs.get_goal_posts(data.car, data)
    enemy_post_right, enemy_post_left = datalibs.get_goal_posts(data.enemy, data)

    enemy_post_right_ang = (enemy_post_right - ball_loc).ang()
    enemy_post_left_ang = (enemy_post_left - ball_loc).ang()

    if data.car.team == 0:
        stress01 = rlmath.inv_lerp(datalibs.ARENA_LENGTH2, -datalibs.ARENA_LENGTH2, ball_loc.y - 500)
    else:
        stress01 = rlmath.inv_lerp(-datalibs.ARENA_LENGTH2, datalibs.ARENA_LENGTH2, ball_loc.y + 500)
    stress01 = min(max(0, stress01), 1)

    right_aim_ang = enemy_post_right_ang + 2 * stress01
    left_aim_ang = enemy_post_left_ang - 2 * stress01

    right_aim_ang = rlmath.fix_ang(right_aim_ang)
    left_aim_ang = rlmath.fix_ang(left_aim_ang)

    aim_cone_dyn = AimCone(right_aim_ang, left_aim_ang)
    aim_cone_dyn.draw(data.renderer, ball_loc, arm_count=7, b=0)

    car_to_ball = (ball_loc - data.car.location)
    good = aim_cone_dyn.contains_direction(car_to_ball)
    data.renderer.draw_line_3d(data.car.location.tuple(), ball_loc.tuple(),
                               data.renderer.create_color(255, 255 if good else 0, 140 if good else 255, 0))
