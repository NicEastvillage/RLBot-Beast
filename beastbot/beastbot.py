import math
import rlmath
from vec2 import Vec2
import moves

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket


class Beast(BaseAgent):

    def initialize_agent(self):
        #This runs once before the bot starts up
        pass

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        car = packet.game_cars[self.index]
        ball_location = Vec2(packet.game_ball.physics.location.x, packet.game_ball.physics.location.y)
        return moves.go_to_point(car, packet, ball_location)
