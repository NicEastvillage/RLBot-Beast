from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

import choices
import datalibs
import moves
import predict
from plans import KickOffPlan
from render import FakeRenderer
from utsystem import UtilitySystem
from vec import Vec3

RENDER = True


class Beast(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.tsgn = -1 if team == 0 else 1
        self.info = datalibs.EGameInfo(index, team)
        self.controls = SimpleControllerState()
        self.plan = None
        self.doing_kickoff = False

        self.ut = None
        self.last_task = None
        self.collect_boost = None
        self.point_of_interest = Vec3()

        self.pid_yaw = moves.PIDControl()
        self.pid_pitch = moves.PIDControl()
        self.pid_roll = moves.PIDControl()
        self.dodge_control = moves.DodgeControl()
        self.ignore_ori_till = 0

    def initialize_agent(self):
        self.ut = get_offense_system(self)
        self.collect_boost = choices.CollectBoost(self)

        if not RENDER:
            self.renderer = FakeRenderer()

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.info.read_packet(packet)

        self.renderer.begin_rendering()

        # Check kickoff
        if self.info.is_kickoff and not self.doing_kickoff:
            self.plan = KickOffPlan()
            self.doing_kickoff = True

        # Execute logic
        if self.plan is None or self.plan.finished:
            # There is no plan, use utility system to find a choice
            self.plan = None
            self.doing_kickoff = False
            choice = self.ut.evaluate(self)
            choice.execute(self)
            # The choice has started a plan, reset utility system
            if self.plan is not None:
                self.ut.reset()
        else:
            # We have a plan
            self.plan.execute(self)

        # Rendering
        predict.draw_ball_path(self, 4.5, 2)

        # Save for next frame
        self.info.my_car.last_input.roll = self.controls.roll
        self.info.my_car.last_input.pitch = self.controls.pitch
        self.info.my_car.last_input.yaw = self.controls.yaw
        self.info.my_car.last_input.boost = self.controls.boost

        self.renderer.end_rendering()
        return self.controls

    def draw_status(self, data):
        if self.last_task is not None:
            data.renderer.draw_string_3d(data.car.location.tuple(), 1, 1, str(self.last_task),
                                         self.last_task.color(data.renderer))


def get_offense_system(agent):
    off_choices = [
        #choices.FixAirOrientation(),
        #choices.DefendGoal(),
        #choices.SaveGoal(agent),
        #choices.ClearBall(agent),
        choices.ShootAtGoal(agent),
        #choices.Dribbling()
    ]
    return UtilitySystem(off_choices, 0.25)

