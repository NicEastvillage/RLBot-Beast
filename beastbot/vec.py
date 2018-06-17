import math

class Vec3:
    def __init__(self, x=0, y=0, z=0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def in2D(self):
        return Vec3(self.x, self.y, 0)

    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def dist(self, other):
        return math.sqrt(self.dist2(other))

    def dist2(self, other):
        return (self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2
    
    def angTo2d(self, ideal):
        current_in_radians = math.atan2(self.y, self.x)
        ideal_in_radians = math.atan2(ideal.y, ideal.x)

        diff = ideal_in_radians - current_in_radians

        # Make sure we go the 'short way'
        if abs(diff) > math.pi:
            if diff < 0:
                diff += 2 * math.pi
            else:
                diff -= 2 * math.pi

        return diff

class Zone:
    def __init__(self, a, b):
        self.low = Vec3(min(a.x, b.x), min(a.y, b.y), min(a.z, b.z))
        self.high = Vec3(max(a.x, b.x), max(a.y, b.y), max(a.z, b.z))
    
    def contains(self, point):
        if self.low.x <= point.x and point.x <= self.high.x:
            if self.low.y <= point.y and point.y <= self.high.y:
                if self.low.z <= point.z and point.z <= self.high.z:
                    return True
        return False