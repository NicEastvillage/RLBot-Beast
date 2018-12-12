from RLUtilities.Maneuvers import AirDodge
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from info import EGameInfo
from moves import DriveController
from render import FakeRenderer, draw_ball_path
from rlmath import *
from utsystem import UtilitySystem

RENDER = True


class Beast(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.info = EGameInfo(index, team)
        self.controls = SimpleControllerState()
        self.plan = None
        self.doing_kickoff = False

        self.ut = None
        self.drive = DriveController()

    def initialize_agent(self):
        self.ut = UtilitySystem([ShootAtGoal()])

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


class ShootAtGoal:
    def __init__(self):
        pass

    def utility(self, bot):
        return 1

    def execute(self, bot):

        car = bot.info.my_car
        ball = bot.info.ball

        car_to_ball = ball.pos - car.pos
        ball_to_goal = bot.info.enemy_goal - ball.pos
        dist = norm(car_to_ball)

        right_side_of_ball = dot(car_to_ball, ball_to_goal) > 0

        if right_side_of_ball:
            # Chase ball
            bot.controls = bot.drive.go_towards_point(bot, xy(ball.pos), 2000, True, True, can_dodge=dist > 2200)
        else:
            # Go home
            bot.controls = bot.drive.go_towards_point(bot, bot.info.own_goal_field, 2000, True, True)
