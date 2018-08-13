import math
from vec import Vec3


# returns sign of x, and 0 if x=0
def sign(x):
	return x and (1, -1)[x < 0]


def lerp(a, b, t):
	return (1 - t) * a + t * b


def inv_lerp(a, b, t):
	return a if b - a == 0 else (t - a) / (b - a)


def get_car_facing_vector(car):
	pitch = float(car.physics.rotation.pitch)
	yaw = float(car.physics.rotation.yaw)

	facing_x = math.cos(pitch) * math.cos(yaw)
	facing_y = math.cos(pitch) * math.sin(yaw)

	return Vec3(facing_x, facing_y)


def steer_correction_smooth(rad, last_rad, d_scale=5):
	derivative = rad - last_rad
	val = rad - d_scale * derivative + rad ** 3
	return min(max(-1, val), 1)


def fix_ang(ang):
	while abs(ang) > math.pi:
		if ang < 0:
			ang += 2 * math.pi
		else:
			ang -= 2 * math.pi
	return ang


def estimate_time_to_arrival(car, point, boost=False):
	car_to_point = point.flat() - car.location

	if boost:
		time = car_to_point.length() / 2300
	else:
		time = car_to_point.length() / 1400

	time += car.location.z / 400  # gravity is 650, but our velocity could be upwards. TODO: Make better!
	return time
