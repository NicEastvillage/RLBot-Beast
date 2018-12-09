import math

from RLUtilities.LinearAlgebra import *


# returns sign of x, and 0 if x=0
def sign(x):
    return x and (1, -1)[x < 0]


def lerp(a, b, t):
    return (1 - t) * a + t * b


def inv_lerp(a, b, t):
    return a if b - a == 0 else (t - a) / (b - a)


def fix_ang(ang):
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

def rotated_2d(vec, ang):
    c = math.cos(ang)
    s = math.sin(ang)
    return vec3(c * vec[0] - s * vec[1],
                s * vec[0] + c * vec[1])
