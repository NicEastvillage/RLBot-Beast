import rlutility
import choices
import situation
import predict
import route
import moves

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket


class Beast(BaseAgent):
    def initialize_agent(self):
        self.ut_system = get_offense_system(self)

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        data = situation.Data(self.index, packet)
        self.renderer.begin_rendering()

        predict.draw_ball_path(self.renderer, data, 4, 0.15)
        if data.car.team == 0:
            r = route.find_route_to_next_ball_landing(data)
            route.draw_route(self.renderer, r)
            self.renderer.end_rendering()
            return moves.follow_route(data, r)
        else:
            self.renderer.end_rendering()
            return self.ut_system.evaluate(data).execute(data)


def get_offense_system(agent):
    off_choices = [
        choices.CollectBoost(agent),
        choices.TouchBall()
    ]
    return rlutility.UtilitySystem(off_choices)
