import math


# returns sign of x, and 0 if x=0
def sign(x):
    return x and (1, -1)[x < 0]


def lerp(a, b, t):
    return (1 - t) * a + t * b


def inv_lerp(a, b, t):
    return a if b - a == 0 else (t - a) / (b - a)


def steer_correction_smooth(rad, last_rad, d_strength=5):
    derivative = rad - last_rad
    val = rad - d_strength * derivative + rad ** 3
    return min(max(-1, val), 1)


def fix_ang(ang):
    while abs(ang) > math.pi:
        if ang < 0:
            ang += 2 * math.pi
        else:
            ang -= 2 * math.pi
    return ang


def is_heading_towards(car, point):
    car_direction = car.orientation.front
    car_to_point = point - car.location
    ang = car_direction.ang_to_flat(car_to_point)
    dist = car_to_point.length()
    return is_heading_towards2(ang, dist)


def is_heading_towards2(ang, dist):
    required_ang = (math.pi / 3) * (dist / 10420 + 0.05)
    return abs(ang) <= required_ang
