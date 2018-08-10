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
    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.ut_system = None
        self.last_task = None
        self.pid = moves.PIDControl()

    def initialize_agent(self):
        self.ut_system = get_offense_system(self)

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        data = datalibs.Data(self, packet)

        self.renderer.begin_rendering()

        predict.draw_ball_path(self.renderer, data, 4.5, 0.11)
        task = self.ut_system.evaluate(data)
        action = task.execute(data)

        self.renderer.end_rendering()

        if self.last_task != task:
            print("Beast", self.index, "status:", str(task))
        self.last_task = task

        return action


def get_offense_system(agent):
    off_choices = [
        choices.KickOff(),
        choices.FixAirOrientation(),
        choices.SaveGoal(agent),
        choices.ClearBall(agent),
        choices.ShootAtGoal(agent),
        choices.CollectBoost(agent),
        choices.Dribbling()
    ]
    return rlutility.UtilitySystem(off_choices, 0.1)
