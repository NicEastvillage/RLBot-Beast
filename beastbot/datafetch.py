import math
from vec import Vec3
from rlbot.utils.structures.game_data_struct import GameTickPacket

# Vec3
def ball_location(car, packet: GameTickPacket):
	return Vec3(packet.game_ball.physics.location.x, packet.game_ball.physics.location.y)