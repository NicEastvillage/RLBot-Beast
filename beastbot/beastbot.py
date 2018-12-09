from RLUtilities.GameInfo import GameInfo
from RLUtilities.Maneuvers import Drive
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from moves import go_towards_point
from render import FakeRenderer, draw_ball_path
from utsystem import UtilitySystem

RENDER = True


class Beast(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.team_sign = -1 if team == 0 else 1
        self.info = GameInfo(index, team)
        self.controls = SimpleControllerState()
        self.plan = None
        self.doing_kickoff = False

        self.ut = None

    def initialize_agent(self):
        self.ut = UtilitySystem([AtbaChoice()])

        if not RENDER:
            self.renderer = FakeRenderer()

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.info.read_packet(packet)

        self.renderer.begin_rendering()

        # Check kickoff
        #if self.info.is_kickoff and not self.doing_kickoff:
        #    self.plan = KickOffPlan()
        #    self.doing_kickoff = True

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
        draw_ball_path(self, 4.5, 2)

        # Save for next frame
        self.info.my_car.last_input.roll = self.controls.roll
        self.info.my_car.last_input.pitch = self.controls.pitch
        self.info.my_car.last_input.yaw = self.controls.yaw
        self.info.my_car.last_input.boost = self.controls.boost

        self.renderer.end_rendering()
        return self.controls


class AtbaChoice:
    def __init__(self):
        pass

    def utility(self, bot):
        return 1

    def execute(self, bot):
        bot.controls = go_towards_point(bot, bot.info.ball.pos, 2000, True, True, True, True)
