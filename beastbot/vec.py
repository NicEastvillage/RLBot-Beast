import math
import rlmath


class Vec3:
    def __init__(self, x: float=0, y: float=0, z: float=0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def flat(self):
        return Vec3(self.x, self.y, 0)

    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scale):
        return Vec3(self.x * scale, self.y * scale, self.z * scale)

    def __rmul__(self, scale):
        return self * scale

    def __truediv__(self, scale):
        scale = 1 / float(scale)
        return self * scale

    def __str__(self):
        return "Vec3(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")"

    def length(self):
        return math.sqrt(self.length2())

    def length2(self):
        return self.x**2 + self.y**2 + self.z**2

    def dist(self, other):
        return math.sqrt(self.dist2(other))

    def dist2(self, other):
        return (self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2

    def normalized(self):
        return self / self.length()

    def rescale(self, new_len):
        return new_len * self.normalized()

    def mul_components(self, other):
        return Vec3(self.x*other.x, self.y*other.y, self.z*other.z)

    def rotate_2d(self, ang):
        c = math.cos(ang)
        s = math.sin(ang)
        return Vec3(c * self.x - s * self.y,
                    s * self.x + c * self.y)

    def lerp(self, other, t):
        return self * (1 - t) + other * t

    def dot(self, other):
        return self.x*other.x + self.y*other.y + self.z*other.z

    def cross(self, other):
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def ang(self):
        return rlmath.fix_ang(math.atan2(self.y, self.x))

    def ang_to(self, ideal):
        cos_ang = self.dot(ideal) / (self.length() * ideal.length())
        return math.acos(cos_ang)

    def ang_to_flat(self, ideal):
        current_in_radians = math.atan2(self.y, self.x)
        ideal_in_radians = math.atan2(ideal.y, ideal.x)

        diff = ideal_in_radians - current_in_radians
        return rlmath.fix_ang(diff)

    def proj_onto(self, other):
        return (self.dot(other) / other.dot(other)) * other

    def proj_onto_size(self, other):
        other = other.normalized()
        return self.dot(other) / other.dot(other)   # can be negative!

    def set(self, some):
        self.x = some.x
        self.y = some.y
        self.z = some.z
        return self

    def tuple(self):
        return self.x, self.y, self.z

    def copy(self):
        return Vec3(self.x, self.y, self.z)


UP = Vec3(0, 0, 1)


class Zone:
    def __init__(self, a, b):
        self.low = Vec3(min(a.x, b.x), min(a.y, b.y), min(a.z, b.z))
        self.high = Vec3(max(a.x, b.x), max(a.y, b.y), max(a.z, b.z))

    def contains(self, point):
        if self.low.x <= point.x <= self.high.x:
            if self.low.y <= point.y <= self.high.y:
                if self.low.z <= point.z <= self.high.z:
                    return True
        return False


class Orientation:
    def __init__(self, rotation):
        self.yaw = float(rotation.yaw)
        self.roll = float(rotation.roll)
        self.pitch = float(rotation.pitch)

        cr = math.cos(self.roll)
        sr = math.sin(self.roll)
        cp = math.cos(self.pitch)
        sp = math.sin(self.pitch)
        cy = math.cos(self.yaw)
        sy = math.sin(self.yaw)

        self.front = Vec3(cp*cy, cp*sy, sp)
        self.left = Vec3(cy*sp*sr-cr*sy, sy*sp*sr+cr*cy, -cp*sr)
        self.up = Vec3(-cr*cy*sp-sr*sy, -cr*sy*sp+sr*cy, cp*cr)
