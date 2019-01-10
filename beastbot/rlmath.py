import math

from RLUtilities.LinearAlgebra import *


FIELD_WIDTH = 8192
FIELD_LENGTH = 10240
FILED_HEIGHT = 2044
GOAL_WIDTH = 1900


X = 0
Y = 1
Z = 2


class Zone2d:
    def __init__(self, cornerA, cornerB):
        self.cornerMin = vec3(min(cornerA[X], cornerB[X]), min(cornerA[Y], cornerB[Y]), 0)
        self.cornerMax = vec3(max(cornerA[X], cornerB[X]), max(cornerA[Y], cornerB[Y]), 0)

    def contains(self, point):
        return self.cornerMin[X] <= point[X] <= self.cornerMax[X]\
               and self.cornerMin[Y] <= point[Y] <= self.cornerMax[Y]


class Zone3d:
    def __init__(self, cornerA, cornerB):
        self.cornerMin = vec3(min(cornerA[X], cornerB[X]), min(cornerA[Y], cornerB[Y]), min(cornerA[Z], cornerB[Z]))
        self.cornerMax = vec3(max(cornerA[X], cornerB[X]), max(cornerA[Y], cornerB[Y]), max(cornerA[Z], cornerB[Z]))

    def contains(self, point):
        return self.cornerMin[X] <= point[X] <= self.cornerMax[X]\
               and self.cornerMin[Y] <= point[Y] <= self.cornerMax[Y]\
               and self.cornerMin[Z] <= point[Z] <= self.cornerMax[Z]


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
    return vec3(c * vec[X] - s * vec[Y],
                s * vec[X] + c * vec[Y])


def is_near_wall(point: vec3, offset: float=130) -> bool:
    return abs(point[X]) > FIELD_WIDTH - offset or abs(point[Y]) > FIELD_LENGTH - offset  # TODO Add diagonal walls


def curve_from_arrival_dir(src, target, dir, w=1):
    bx = target[X]
    by = target[Y]
    cx = src[X]
    cy = src[Y]
    dx = dir[X]
    dy = dir[Y]

    t = - (bx * bx - 2 * bx * cx + by * by - 2 * by * cy + cx * cx + cy * cy) / (2 * (bx * dx + by * dy - cx * dx - cy * dy))
    t = clip(t, -1700, 1700)

    return target + w * t * dir


def bezier(t, points):
    n = len(points)
    if n == 1:
        return points[0]
    else:
        return (1 - t) * bezier(t, points[0:-1]) + t * bezier(t, points[1:n])
