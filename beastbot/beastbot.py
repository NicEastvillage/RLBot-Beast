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
        ch = []
        for i, pad in enumerate(self.get_field_info().boost_pads):
            ch.append(choices.SpecificBoostPad(pad, i))
        
        self.ut_system = rlutility.UtilitySystem(ch)

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        car = packet.game_cars[self.index]
        return self.ut_system.evaluate(car, packet).execute(car, packet)