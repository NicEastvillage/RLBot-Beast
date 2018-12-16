from RLUtilities.GameInfo import GameInfo, BoostPad
from rlbot.messages.flat import GameTickPacket, FieldInfo

from rlmath import *


class EBoostPad(BoostPad):
    def __init__(self, index, pos, is_big, is_active, timer):
        super().__init__(index, pos, is_active, timer)
        self.is_big = is_big


class EGameInfo(GameInfo):
    def __init__(self, index, team, field_info: FieldInfo):
        super().__init__(index, team, field_info)

        self.team_sign = -1 if team == 0 else 1
        self.is_kickoff = False

        self.own_goal = vec3(0, self.team_sign * FIELD_LENGTH / 2, 0)
        self.own_goal_field = vec3(0, self.team_sign * (FIELD_LENGTH / 2 - 560), 0)
        self.enemy_goal = vec3(0, -self.team_sign * FIELD_LENGTH / 2, 0)

        self.boost_pads = []
        for i in range(field_info.num_boosts):
            pad = field_info.boost_pads[i]
            pos = vec3(pad.location.x, pad.location.y, pad.location.z)
            self.boost_pads.append(EBoostPad(i, pos, pad.is_full_boost, True, 0.0))

    def read_packet(self, packet: GameTickPacket):
        super().read_packet(packet)

        # Game state
        self.is_kickoff = packet.game_info.is_kickoff_pause

        # Boost pads
        for pad in self.boost_pads:
            pad_state = packet.game_boosts[pad.index]
            pad.is_active = pad_state.is_active
            pad.timer = pad_state.timer
