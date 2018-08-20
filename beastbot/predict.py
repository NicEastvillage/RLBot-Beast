import math
import rlmath
import datalibs
from vec import Vec3


GRAVITY = Vec3(z=-650)
BOUNCINESS = -0.6


def draw_ball_path(renderer, data, duration, time_step):
    time_passed = 0
    ball_clone = datalibs.Ball()
    locations = [data.ball.location]
    while time_passed < duration:
        time_passed += time_step
        ball_clone.set(data.ball)
        move_ball(ball_clone, time_passed)
        locations.append(ball_clone.location.copy())

    prev_loc_t = locations[0].tuple()
    for loc in locations[1:]:
        loc_t = loc.tuple()
        renderer.draw_line_3d(prev_loc_t, loc_t, renderer.create_color(255, 255, 0, 0))
        prev_loc_t = loc_t


class Prediction:
    def __init__(self, happens, time):
        self.happens = happens
        self.time = time

    def happens_before(self, time: float):
        return self.happens and self.time < time

    def happens_after(self, time: float):
        return self.happens and self.time > time

    def happens_before_other(self, other_prediction):
        return (self.happens and not other_prediction.happens)\
               or (other_prediction.happens and self.happens_before(other_prediction.time))


class WallHitPrediction(Prediction):
    def __init__(self, happens, time, wall):
        super().__init__(happens, time)
        self.wall = wall


class SideWall:
    def __init__(self, x):
        self.wall_x = x
        self.normal = Vec3(x=rlmath.sign(x))

    def get_next_ball_hit(self, ball):
        if ball.velocity.x == 0:
            return Prediction(False, 1e307)
        dist = rlmath.sign(self.wall_x) * (abs(self.wall_x - ball.location.x) - datalibs.BALL_RADIUS)
        t = dist / ball.velocity.x
        return Prediction(t >= 0, t)

    def bounce_ball(self, ball):
        bounce(ball, self.normal)


class BackWall:
    def __init__(self, y):
        self.wall_y = y
        self.normal = Vec3(y=rlmath.sign(y))

    def get_next_ball_hit(self, ball):
        if ball.velocity.y == 0:
            return Prediction(False, 1e307)
        dist = rlmath.sign(self.wall_y) * (abs(self.wall_y - ball.location.y) - datalibs.BALL_RADIUS)
        t = dist / ball.velocity.y
        return Prediction(t >= 0, t)

    def bounce_ball(self, ball):
        bounce(ball, self.normal)


class CornerWall:
    def __init__(self, anchor, normal):
        self.anchor = anchor
        self.normal = normal.normalized()

    def get_next_ball_hit(self, ball):
        dot = ball.velocity.dot(self.normal)
        if dot == 0:
            return Prediction(False, 1e307)
        # t = (self.normal.x * ball.location.x - self.normal.x * self.anchor.x + self.normal.y ) / -dot
        scaled = self.normal.mul_components(ball.location - self.anchor)
        t = (scaled.x + scaled.y) / -dot
        return Prediction(t >= 0, t)

    def bounce_ball(self, ball):
        bounce(ball, self.normal)


class Ceiling:
    def __init__(self, z):
        self.height = z
        self.normal = Vec3(z=-1)

    def get_next_ball_hit(self, ball):
        return time_of_arrival_at_height(ball, self.height - datalibs.BALL_RADIUS)

    def bounce_ball(self, ball):
        bounce(ball, self.normal)


SIDE_WALL_POS = SideWall(4120)
SIDE_WALL_NEG = SideWall(-4120)
BACK_WALL_POS = BackWall(5140)
BACK_WALL_NEG = BackWall(-5140)
CORNER_WALL_PP = CornerWall(Vec3(3318, 4570), Vec3(1, 1))
CORNER_WALL_NP = CornerWall(Vec3(-3318, 4570), Vec3(-1, 1))
CORNER_WALL_PN = CornerWall(Vec3(3318, -4570), Vec3(1, -1))
CORNER_WALL_NN = CornerWall(Vec3(-3318, -4570), Vec3(-1, -1))
CEILING = Ceiling(2044)


def move_body(body, time, gravity=True):
    acc = GRAVITY if gravity else Vec3()

    # (1/2 * a * t^2) + (v * t) + p
    new_loc = 0.5 * time * time * acc + time * body.velocity + body.location
    new_vel = time * acc + body.velocity
    body.location = new_loc
    body.velocity = new_vel

    return body


def will_ball_hit_goal(ball):
    if ball.velocity.y == 0:
        return Prediction(False, 1e306)

    time = abs(ball.location.y) / abs(ball.velocity.y)
    hit_loc = move_ball(ball.copy(), time).location
    hits_goal = abs(hit_loc.x) < 1900
    return Prediction(hits_goal, time)


def next_ball_wall_hit(ball):
    walls = [
        SIDE_WALL_POS, SIDE_WALL_NEG, BACK_WALL_POS, BACK_WALL_NEG,
        CORNER_WALL_PP, CORNER_WALL_PN, CORNER_WALL_NP, CORNER_WALL_NN,
        CEILING
    ]
    wall_index = -1
    earliest_hit_time = 1e300
    for i, w in enumerate(walls):
        hit = w.get_next_ball_hit(ball)
        if hit.happens and hit.time <= earliest_hit_time:
            wall_index = i
            earliest_hit_time = hit.time

    return WallHitPrediction(wall_index != -1, earliest_hit_time, walls[wall_index])


def next_ball_ground_hit(ball):
    return time_of_arrival_at_height(ball, datalibs.BALL_RADIUS)


def time_of_arrival_at_height(body, height, gravity=True):
    if height == body.location.z:
        return Prediction(True, 0)

    acc = GRAVITY if gravity else Vec3()
    if acc.z == 0:
        return time_of_arrival_at_height_linear(body, height)
    else:
        return time_of_arrival_at_height_quadratic(body, height, acc.z)


def time_of_arrival_at_height_linear(body, height):
    if body.velocity.z == 0:
        return Prediction(False, 1e307)

    time = (height - body.location.z) / body.velocity.z
    return Prediction(time >= 0, time)


def time_of_arrival_at_height_quadratic(body, height, acc_z):

    loc_z = body.location.z
    vel_z = body.velocity.z

    # Check if height is above current z, because then the body may never get there
    if height > loc_z:
        # Elapsed time when arriving at the turning point
        turn_time = -vel_z / acc_z
        turn_point_height = 0.5 * acc_z * turn_time * turn_time + vel_z * turn_time + loc_z

        # Return null if height is never reached, or was in the past
        if turn_point_height < height or turn_time < 0:
            return Prediction(False, 1e307)

        # The height is reached on the way up
        if loc_z < height:
            time = (-vel_z + math.sqrt(2 * acc_z * height - 2 * acc_z * loc_z + vel_z * vel_z)) / acc_z
            return Prediction(True, time)

    # See technical documents for this equation : t = -(v + sqrt(2*a*h - 2*a*p + v^2) / a
    time = -(vel_z + math.sqrt(2 * acc_z * height - 2 * acc_z * loc_z + vel_z * vel_z)) / acc_z
    return Prediction(True, time)


def bounce(ball, normal):
    # See https://samuelpmish.github.io/notes/RocketLeague/ball_bouncing/
    MU = 0.285
    A = 0.0003

    v_perp = ball.velocity.dot(normal) * normal
    v_para = ball.velocity - v_perp
    v_spin = datalibs.BALL_RADIUS * normal.cross(ball.angular_velocity)
    s = v_para + v_spin

    if s.length() == 0:
        delta_v_para = Vec3()
    else:
        ratio = v_perp.length() / s.length()
        delta_v_para = - min(1.0, 2.0 * ratio) * MU * s

    delta_v_perp = - 1.60 * v_perp

    ball.velocity += delta_v_perp + delta_v_para
    ball.angular_velocity += A * datalibs.BALL_RADIUS * delta_v_para.cross(normal)


def move_ball(ball, time):
    if time <= 0:
        return ball

    time_spent = 0
    limit = 30

    while time - time_spent > 0.001 and limit != 0:
        time_left = time - time_spent
        limit -= 1

        wall_hit = next_ball_wall_hit(ball)
        ground_hit = next_ball_ground_hit(ball)

        # Check if ball doesn't hits anything
        if ground_hit.happens_after(time_left) and wall_hit.happens_after(time_left):
            return move_body(ball, time_left)

        elif wall_hit.happens_before_other(ground_hit):
            # Simulate until ball it hits wall
            move_body(ball, wall_hit.time)
            time_spent += wall_hit.time
            wall_hit.wall.bounce_ball(ball)

        elif ground_hit.time == 0.0 and abs(ball.velocity.z * BOUNCINESS) < 2.0:
            # Simulate ball rolling until it hits wall or time's up
            ball.velocity.z = 0

            if not wall_hit.happens:
                # The ball is laying still
                return ball

            if time_left < wall_hit.time:
                # Time's up
                move_body(ball, time_left, False)
                return ball

            # Roll
            move_body(ball, wall_hit.time, False)
            time_spent += wall_hit.time
            wall_hit.wall.bounce_ball(ball)

        else:
            # Simulate until ball it hits ground
            move_body(ball, ground_hit.time)
            time_spent += ground_hit.time
            bounce(ball, Vec3(0, 0, 1))

    return ball


def time_till_reach_ball(ball, car):
    car_to_ball = (ball.location - car.location).flat()
    dist = car_to_ball.length() - datalibs.BALL_RADIUS - 25
    vel_c_f = car.velocity.proj_onto_size(car_to_ball)
    vel_b_f = ball.velocity.proj_onto_size(car_to_ball)
    vel_c_amp = rlmath.lerp(vel_c_f, car.velocity.length(), 0.6)
    vel_f = vel_c_amp - vel_b_f
    time = dist / max(300, vel_f)

    return time
