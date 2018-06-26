import math
import rlmath
from vec import Vec3
import rlutility
import moves
import datafetch
import choices

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

class Beast(BaseAgent):

    def initialize_agent(self):
        self.ut_system = get_offense_system(self)

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        car = packet.game_cars[self.index]
        return self.ut_system.evaluate(car, packet).execute(car, packet)

def get_offense_system(agent):
    off_choices = []
    off_choices.append(choices.CollectBoost(agent))
    off_choices.append(choices.TouchBall())
    return rlutility.UtilitySystem(off_choices)