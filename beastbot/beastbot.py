import random
import time

from RLUtilities.Maneuvers import AirDodge
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.game_state_util import CarState, Physics, Vector3, Rotator, GameState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from info import EGameInfo
from moves import DriveController, AimCone
from plans import KickoffPlan
from render import FakeRenderer, draw_ball_path
from rlmath import *
from utsystem import UtilitySystem

RENDER = True


class Beast(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.do_rendering = RENDER
        self.controls = SimpleControllerState()
        self.info = None
        self.plan = None
        self.doing_kickoff = False

        self.ut = None
        self.drive = DriveController()

        self.last_time = 0
        self.state_setting_timer_last = time.time()

    def initialize_agent(self):
        self.ut = UtilitySystem([ShootAtGoal()])
        self.info = EGameInfo(self.index, self.team, )

        if not RENDER:
            self.renderer = FakeRenderer()

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:

        # Read packet
        if not self.info.field_info_loaded:
            self.info.read_field_info(self.get_field_info())
            if not self.info.field_info_loaded:
                return SimpleControllerState()
        self.info.read_packet(packet)

        self.renderer.begin_rendering()

        # Check kickoff
        if self.info.is_kickoff and not self.doing_kickoff:
            self.plan = KickoffPlan()
            self.doing_kickoff = True
            print("Beast: Begins kickoff")

        # Execute logic
        if self.plan is None or self.plan.finished:
            # There is no plan, use utility system to find a choice
            self.plan = None
            self.doing_kickoff = False
            choice = self.ut.evaluate(self)
            choice.execute(self)
            # The choice has started a plan, reset utility system and execute plan instead
            if self.plan is not None:
                self.ut.reset()
                self.plan.execute(self)
        else:
            # We have a plan
            self.plan.execute(self)

        # Rendering
        if self.do_rendering:
            draw_ball_path(self, 4, 5)

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
        ball_to_enemy_goal = bot.info.enemy_goal - ball.pos
        own_goal_to_ball = ball.pos - bot.info.own_goal
        dist = norm(car_to_ball)

        offence = ball.pos[Y] * bot.info.team_sign < 0
        dot_enemy = dot(car_to_ball, ball_to_enemy_goal)
        dot_own = dot(car_to_ball, own_goal_to_ball)
        right_side_of_ball = dot_enemy > 0 if offence else dot_own > 0

        if right_side_of_ball:
            # Aim cone
            dir_to_post_1 = (bot.info.enemy_goal + vec3(3800, 0, 0)) - bot.info.ball.pos
            dir_to_post_2 = (bot.info.enemy_goal + vec3(-3800, 0, 0)) - bot.info.ball.pos
            cone = AimCone(dir_to_post_1, dir_to_post_2)
            cone.get_goto_point(bot, car.pos, bot.info.ball.pos)
            if bot.do_rendering:
                cone.draw(bot, bot.info.ball.pos)

            # Chase ball
            bot.controls = bot.drive.go_towards_point(bot, xy(ball.pos), 2000, True, True, can_dodge=dist > 2200)
        else:
            # Go home
            bot.controls = bot.drive.go_towards_point(bot, bot.info.own_goal_field, 2000, True, True)
