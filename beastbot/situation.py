import math
from vec import Vec3

from rlbot.utils.structures.game_data_struct import GameTickPacket

ARENA_LENGTH = 10280
ARENA_WIDTH = 8240
ARENA_HEIGHT = 4100

GOAL_LENGTH = 650
GOAL_WIDTH = 1550
GOAL_HEIGHT = 615

CAR_LENGTH = 118
CAR_WIDTH = 84
CAR_HEIGHT = 36

def get_goal_direction(car, packet:GameTickPacket):
	if car.team == 0:
		return -1
	else:
		return 1