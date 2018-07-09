import math
import situation
from vec import Vec3


GRAVITY = Vec3(z=-650)
BOUNCINESS = -0.6


def draw_ball_path(renderer, data, duration, time_step):
    time_passed = 0
    ball_clone = situation.Ball()
    locations = [data.ball.location]
    while time_passed < duration:
        time_passed += time_step
        ball_clone.set(data.ball)
        move_ball(ball_clone, time_passed)
        locations.append(ball_clone.location)

    renderer.begin_rendering()
    prev_loc_t = locations[0].tuple()
    for loc in locations[1:]:
        loc_t = loc.tuple()
        renderer.draw_line_3d(prev_loc_t, loc_t, renderer.create_color(255, 255, 0, 0))
        prev_loc_t = loc_t
    renderer.end_rendering()


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
    def __init__(self, happens, time, is_side_wall):
        super().__init__(happens, time)
        self.is_side_wall = is_side_wall


def move_body(body, time, gravity=True):
    acc = GRAVITY if gravity else Vec3()

    # (1/2 * a * t^2) + (v * t) + p
    new_loc = 0.5 * time * time * acc + time * body.velocity + body.location
    new_vel = time * acc + body.velocity
    body.location = new_loc
    body.velocity = new_vel

    return body


def next_wall_hit(body, offset=0.0):
    wall_hits = [
        max((situation.ARENA_WIDTH2-offset - body.location.x) / body.velocity.x, 0) if body.velocity.x != 0 else 1e307,
        max((situation.ARENA_WIDTH2-offset + body.location.x) / -body.velocity.x, 0) if body.velocity.x != 0 else 1e307,
        max((situation.ARENA_LENGTH2-offset - body.location.y) / body.velocity.y, 0) if body.velocity.y != 0 else 1e307,
        max((situation.ARENA_LENGTH2-offset + body.velocity.y) / -body.velocity.y, 0) if body.velocity.y != 0 else 1e307
    ]
    wall_index = -1
    earliest_hit = 1e306
    for i, hit_time in enumerate(wall_hits):
        if hit_time <= earliest_hit:
            earliest_hit = hit_time
            wall_index = i

    return WallHitPrediction(wall_index != -1, earliest_hit, wall_index == 0 or wall_index == 1)


def time_of_arrival_at_height(body, height, gravity=True):
    if height == body.location.z:
        return 0

    acc = GRAVITY if gravity else Vec3()
    if acc.z == 0:
        return time_of_arrival_at_height_linear(body, height)
    else:
        return time_of_arrival_at_height_quadratic(body, height, acc.z)


def time_of_arrival_at_height_linear(body, height):
    if body.velocity.z == 0:
        return Prediction(False, 1e307)

    time = (height - body.location.z) / body.velocity.z
    return Prediction(time < 0, time)


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

    # See technical documents for this equation : t = -(v + sqrt(2*a*h - 2*a*p + v^2) / a
    time = -(vel_z + math.sqrt(2 * acc_z * height - 2 * acc_z * loc_z + vel_z * vel_z)) / acc_z
    return Prediction(True, time)


def move_ball(ball, time):
    if time <= 0:
        return ball

    time_spent = 0

    while time_spent <= time:
        time_left = time - time_spent

        wall_hit = next_wall_hit(ball, 92.0)
        ground_hit = time_of_arrival_at_height(ball, 92.0)

        # Check if ball doesn't hits anything
        if ground_hit.happens_after(time_left) and wall_hit.happens_after(time_left):
            return move_body(ball, time_left)

        elif wall_hit.happens_before_other(ground_hit):
            # Simulate until ball it hits wall
            move_body(ball, wall_hit.time)
            time_spent += wall_hit.time
            if wall_hit.is_side_wall:
                ball.velocity.x *= BOUNCINESS
            else:
                ball.velocity.y *= BOUNCINESS

        elif ground_hit.time == 0:
            # Simulate ball rolling until it hits wall
            ball.velocity.z = 0

            if not wall_hit.happens:
                # The ball is laying still
                break

            move_body(ball, min(wall_hit.time, time_left), False)
            time_spent += wall_hit.time

            if wall_hit.is_side_wall:
                ball.velocity.x *= BOUNCINESS
            else:
                ball.velocity.y *= BOUNCINESS

        else:
            # Simulate until ball it hits ground
            move_body(ball, ground_hit.time)
            time_spent += ground_hit.time
            ball.velocity.z *= BOUNCINESS

    return ball
