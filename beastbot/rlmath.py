import math


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
