import math
import rlmath
from vec2 import Vec2

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket


class PythonExample(BaseAgent):

    def initialize_agent(self):
        #This runs once before the bot starts up
        pass

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        controller_state = SimpleControllerState()

        ball_location = Vec2(packet.game_ball.physics.location.x, packet.game_ball.physics.location.y)

        my_car = packet.game_cars[self.index]
        car_location = Vec2(my_car.physics.location.x, my_car.physics.location.y)
        car_direction = rlmath.get_car_facing_vector(my_car)
        car_to_ball = ball_location - car_location

        steer_correction_radians = car_direction.correction_to(car_to_ball)
        steer_correction = rlmath.steer_correction_smooth(steer_correction_radians)

        controller_state.throttle = 1.0
        controller_state.steer = steer_correction

        return controller_state
