import math

from RLUtilities.LinearAlgebra import *


FIELD_WIDTH = 8192
FIELD_LENGTH = 10240
FILED_HEIGHT = 2044


# returns sign of x, and 0 if x == 0
def sign0(x) -> float:
    return x and (1, -1)[x < 0]


def sign(x) -> float:
    return (1, -1)[x < 0]


def lerp(a, b, t: float):
    return (1 - t) * a + t * b


def inv_lerp(a, b, v) -> float:
    return a if b - a == 0 else (v - a) / (b - a)


def fix_ang(ang: float) -> float:
    while abs(ang) > math.pi:
        if ang < 0:
            ang += 2 * math.pi
        else:
            ang -= 2 * math.pi
    return ang


def proj_onto(src: vec3, dir: vec3) -> vec3:
    try:
        return (dot(src, dir) / dot(dir, dir)) * dir
    except ZeroDivisionError:
        return vec3()


def proj_onto_size(src: vec3, dir: vec3) -> float:
    try:
        dir_n = normalize(dir)
        return dot(src, dir_n) / dot(dir_n, dir_n)  # can be negative!
    except ZeroDivisionError:
        return norm(src)


def rotated_2d(vec: vec3, ang: float) -> vec3:
    c = math.cos(ang)
    s = math.sin(ang)
    return vec3(c * vec[0] - s * vec[1],
                s * vec[0] + c * vec[1])


def is_near_wall(point: vec3, offset: float=100) -> bool:
    return abs(point[0]) > FIELD_WIDTH - offset or abs(point[1]) > FIELD_LENGTH - offset  # TODO Add diagonal walls