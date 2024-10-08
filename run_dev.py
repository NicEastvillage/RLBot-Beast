from pathlib import Path
from time import sleep

from rlbot import flat
from rlbot.managers import MatchManager

MATCH_CONFIG_FILE = 'rlbot.toml'

if __name__ == '__main__':
    root_dir = Path(__file__).parent

    # Start RLBotServer and the match
    match_manager = MatchManager(root_dir)
    match_manager.ensure_server_started()
    match_manager.start_match(root_dir / MATCH_CONFIG_FILE)

    sleep(5)

    # wait for the match to end
    # or press ctrl+c to kill the match
    while match_manager.packet is None or match_manager.packet.game_info.game_state_type != flat.GameStateType.Ended:
        sleep(0.1)

    # ensure RLBotServer shuts down
    match_manager.shut_down()