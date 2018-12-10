from RLUtilities.GameInfo import GameInfo
from rlmath import *


class EGameInfo(GameInfo):
    def __init__(self, index, team):
        super().__init__(index, team)

        self.team_sign = -1 if team == 0 else 1

        self.own_goal = vec3(0, self.team_sign * FIELD_LENGTH / 2, 0)
        self.own_goal_field = vec3(0, self.team_sign * (FIELD_LENGTH / 2 - 560), 0)
        self.enemy_goal = vec3(0, -self.team_sign * FIELD_LENGTH / 2, 0)

