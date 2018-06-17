import math
from vec import Vec3
import situation
from rlbot.utils.structures.game_data_struct import GameTickPacket

# Vec3
def my_location(car, packet: GameTickPacket):
	return Vec3(car.physics.location.x, car.physics.location.y, car.physics.location.z)
	
# Vec3
def enemy_location(car, packet: GameTickPacket):
	enemy = packet.game_cars[1 - car.team]
	return Vec3(enemy.physics.location.x, enemy.physics.location.y, enemy.physics.location.z)

# Vec3
def ball_location(car, packet: GameTickPacket):
	return Vec3(packet.game_ball.physics.location.x, packet.game_ball.physics.location.y)
	
# Zone
def my_half_zone(car, packet: GameTickPacket):
	if car.team == 0:
		return situation.BLUE_HALF_ZONE
	else:
		return situation.ORANGE_HALF_ZONE

# Zone
def enemy_half_zone(car, packet: GameTickPacket):
	if car.team == 1:
		return situation.BLUE_HALF_ZONE
	else:
		return situation.ORANGE_HALF_ZONE

# Vec3
def my_goal_location(car, packet: GameTickPacket):
	goal_offset = situation.ARENA_LENGTH - 200
	if car.team == 0:
		goal_offset *= -1
	return Vec3(0, goal_offset)

# Vec3
def enemy_goal_location(car, packet: GameTickPacket):
	goal_offset = situation.ARENA_LENGTH - 200
	if car.team == 1:
		goal_offset *= -1
	return Vec3(0, goal_offset)