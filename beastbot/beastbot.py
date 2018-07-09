import rlutility
import choices
import situation
import predict
import route

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket


class Beast(BaseAgent):
	def initialize_agent(self):
		self.ut_system = get_offense_system(self)

	def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
		data = situation.Data(self.index, packet)
		if data.car.team == 0:
			r = route.get_route(data)
			route.draw_route(self.renderer, r)
		return self.ut_system.evaluate(data).execute(data)


def get_offense_system(agent):
	off_choices = [
		choices.CollectBoost(agent),
		choices.TouchBall()
	]
	return rlutility.UtilitySystem(off_choices)
