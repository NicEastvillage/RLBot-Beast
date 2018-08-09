import math
import rlmath
import rlutility
from vec import Vec3
import datalibs
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
		return datalibs.BLUE_HALF_ZONE
	else:
		return datalibs.ORANGE_HALF_ZONE

# float
def get_possession_score(car, packet):
	car_loc = Vec3(car.physics.location.x, car.physics.location.y, car.physics.location.z)
	car_dir = rlmath.get_car_facing_vector(car)
	ball_loc = Vec3(packet.game_ball.physics.location.x, packet.game_ball.physics.location.y)
	car_to_ball = ball_loc - car_loc
	
	dist = car_to_ball.length()
	ang = car_dir.ang_to(car_to_ball)
	
	return rlutility.dist_01(dist)*rlutility.face_ang_01(ang)

# float
def my_possession_score(car, packet):
	return get_possession_score(car, packet)

# float
def enemy_possession_score(car, packet):
	enemy = packet.game_cars[1 - car.team]
	return get_possession_score(enemy, packet)

# boolean
def has_possession(car, packet):
	return my_possession_score(car, packet) > enemy_possession_score(car, packet)

def has_not_possession(car, packet):
	return not has_possession(car, packet)

# Zone
def enemy_half_zone(car, packet: GameTickPacket):
	if car.team == 1:
		return datalibs.BLUE_HALF_ZONE
	else:
		return datalibs.ORANGE_HALF_ZONE

# Vec3
def my_goal_location(car, packet: GameTickPacket):
	goal_offset = datalibs.ARENA_LENGTH2 - 300
	if car.team == 0:
		goal_offset *= -1
	return Vec3(0, goal_offset)

# Vec3
def enemy_goal_location(car, packet: GameTickPacket):
	goal_offset = datalibs.ARENA_LENGTH2 - 300
	if car.team == 1:
		goal_offset *= -1
	return Vec3(0, goal_offset)