import math

class Vec2:
    def __init__(self, x=0, y=0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, val):
        return Vec2(self.x + val.x, self.y + val.y)

    def __sub__(self, val):
        return Vec2(self.x - val.x, self.y - val.y)

    def dist(self, other):
        return math.sqrt(self.dist2(other))

    def dist2(self, other):
        return (self.x - other.x)**2 + (self.y - other.y)**2

    def correction_to(self, ideal):
        current_in_radians = math.atan2(self.y, self.x)
        ideal_in_radians = math.atan2(ideal.y, ideal.x)

        correction = ideal_in_radians - current_in_radians

        # Make sure we go the 'short way'
        if abs(correction) > math.pi:
            if correction < 0:
                correction += 2 * math.pi
            else:
                correction -= 2 * math.pi

        return correction