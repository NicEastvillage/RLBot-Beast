import math
from vec import Vec3,Zone

from rlbot.utils.structures.game_data_struct import GameTickPacket

ARENA_LENGTH = 10280 # y
ARENA_WIDTH = 8240 # x
ARENA_HEIGHT = 4100 # z
ARENA_LENGTH2 = ARENA_LENGTH / 2
ARENA_WIDTH2 = ARENA_WIDTH / 2

GOAL_LENGTH = 650
GOAL_WIDTH = 1550
GOAL_HEIGHT = 615

CAR_LENGTH = 118
CAR_WIDTH = 84
CAR_HEIGHT = 36

BLUE_DIRECTION = -1
ORANGE_DIRECTION = 1

BLUE_HALF_ZONE = Zone(Vec3(-ARENA_WIDTH2, -ARENA_LENGTH2), Vec3(ARENA_WIDTH2, 0, ARENA_HEIGHT))
ORANGE_HALF_ZONE = Zone(Vec3(-ARENA_WIDTH2, ARENA_LENGTH2), Vec3(ARENA_WIDTH2, 0, ARENA_HEIGHT))

def enemy(car, packet:GameTickPacket):
	return packet.game_cars[1 - car.team]

def get_goal_direction(car, packet:GameTickPacket):
	if car.team == 0:
		return BLUE_DIRECTION
	else:
		return ORANGE_DIRECTION

def is_heading_towards(car, point):
	car_location = Vec3(car.physics.location.x, car.physics.location.y)
	car_direction = rlmath.get_car_facing_vector(car)
	car_to_point = point - car_location
	ang = car_direction.angTo2d(car_to_point)
	dist = car_to_point.length()
	return is_heading_towards2(ang, dist)

def is_heading_towards2(ang, dist):
	required_ang = (math.pi / 2) * (dist / ARENA_LENGTH)
	return ang <= required_ang