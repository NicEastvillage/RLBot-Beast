import rlutility
import choices
import datalibs
import predict
import route
import moves

from vec import Vec3
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket


class Beast(BaseAgent):
    def initialize_agent(self):
        self.ut_system = get_offense_system(self)

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        data = datalibs.Data(self, packet)

        self.renderer.begin_rendering()

        predict.draw_ball_path(self.renderer, data, 4, 0.15)
        action = self.ut_system.evaluate(data).execute(data)
        self.renderer.end_rendering()
        return action


def get_offense_system(agent):
    off_choices = [
        choices.KickOff(),
        choices.FixAirOrientation(),
        choices.SaveGoal(agent),
        choices.ClearBall(agent),
        choices.ShootAtGoal(agent),
        choices.CollectBoost(agent)
    ]
    return rlutility.UtilitySystem(off_choices, 0)
