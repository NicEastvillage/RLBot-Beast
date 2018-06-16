import math
import rlmath
from vec2 import Vec2
import moves
import behaviourtree as bt
import nodes
import datafetch

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket


class Beast(BaseAgent):

    def initialize_agent(self):
        #This runs once before the bot starts up
        self.behaviour = bt.BehaviourTree(nodes.TaskGoTo([datafetch.ball_location]))
        pass

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        car = packet.game_cars[self.index]
        return self.behaviour.resolve(car, packet)
