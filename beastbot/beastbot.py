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
        self.collect_boost = None
        self.point_of_interest = Vec3()

        self.pid_yaw = moves.PIDControl()
        self.pid_pitch = moves.PIDControl()
        self.pid_roll = moves.PIDControl()
        self.dodge_control = moves.DodgeControl()
        self.ignore_ori_till = 0

    def initialize_agent(self):
        self.ut_system = get_offense_system(self)
        self.collect_boost = choices.CollectBoost(self)

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        data = datalibs.Data(self, packet)

        self.renderer.begin_rendering()

        # predict.draw_ball_path(data.renderer, data, 4.5, 0.11)

        if self.dodge_control.is_dodging:

            self.draw_status(data)
            self.renderer.end_rendering()

            return self.dodge_control.continue_dodge(data)
        else:
            task, score = self.ut_system.evaluate(data)
            if score < self.collect_boost.utility(data):
                # collect boost has higher utility, bot keep the other task in mind
                self.point_of_interest = task.get_point_of_interest(data)
                action = self.collect_boost.execute(data)
            else:
                action = task.execute(data)

            self.draw_status(data)
            self.renderer.end_rendering()

            if self.last_task != task:
                print("Beast", self.index, "status:", str(task))
            self.last_task = task

            return action

    def draw_status(self, data):
        if self.last_task is not None:
            data.renderer.draw_string_3d(data.car.location.tuple(), 1, 1, str(self.last_task), self.last_task.color(data.renderer))

def get_offense_system(agent):
    off_choices = [
        choices.KickOff(),
        choices.FixAirOrientation(),
        choices.DefendGoal(),
        choices.SaveGoal(agent),
        choices.ClearBall(agent),
        choices.ShootAtGoal(agent),
        choices.Dribbling()
    ]
    return rlutility.UtilitySystem(off_choices, 0.25)
