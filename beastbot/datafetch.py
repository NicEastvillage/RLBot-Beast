import math
from vec2 import Vec2
from rlbot.utils.structures.game_data_struct import GameTickPacket

# Vec2
def ball_location(car, packet: GameTickPacket):
	return Vec2(packet.game_ball.physics.location.x, packet.game_ball.physics.location.y)