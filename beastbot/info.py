from RLUtilities.GameInfo import GameInfo
from rlbot.messages.flat import GameTickPacket

from rlmath import *


class EGameInfo(GameInfo):
    def __init__(self, index, team):
        super().__init__(index, team)

        self.team_sign = -1 if team == 0 else 1
        self.is_kickoff = False

        self.own_goal = vec3(0, self.team_sign * FIELD_LENGTH / 2, 0)
        self.own_goal_field = vec3(0, self.team_sign * (FIELD_LENGTH / 2 - 560), 0)
        self.enemy_goal = vec3(0, -self.team_sign * FIELD_LENGTH / 2, 0)

    def read_packet(self, packet: GameTickPacket):
        super().read_packet(packet)

        self.is_kickoff = packet.game_info.is_kickoff_pause
