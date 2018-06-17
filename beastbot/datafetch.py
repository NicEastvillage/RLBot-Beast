import math
from vec import Vec3
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