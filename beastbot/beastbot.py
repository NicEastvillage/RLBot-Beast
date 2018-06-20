import math
import rlmath
from vec import Vec3
import moves
import tasks as task
import guards as guard
import behaviourtree as bt
import datafetch

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket


class Beast(BaseAgent):

    def initialize_agent(self):
        #This runs once before the bot starts up
        self.kickoff = bt.BehaviourTree(bt.RepeatUntilFailure(task.GoTowards([datafetch.ball_location, False, True])))
        self.behaviour = bt.BehaviourTree(
            bt.Sequencer([
                bt.RepeatUntilFailure(bt.Sequencer([
                    # while
                    bt.Selector([
                        guard.DistanceLessThan([200, datafetch.my_location, datafetch.ball_location]),
                        # or
                        guard.IsPointInZone([datafetch.ball_location, datafetch.my_half_zone])
                    ]),
                    # do
                    task.GoTowards([datafetch.ball_location, True, False])
                ])),
                bt.RepeatUntilFailure(bt.Sequencer([
                    # while
                    bt.Inverter(guard.DistanceLessThan([200, datafetch.my_location, datafetch.my_goal_location])),
                    # do
                    task.GoTowards([datafetch.my_goal_location, True, False])
                ])),
                bt.RepeatUntilFailure(bt.Sequencer([
                    # while
                    guard.IsPointInZone([datafetch.ball_location, datafetch.enemy_half_zone]),
                    # do
                    task.Wait()
                ])),
            ]))
            
        #task.GoTowards([datafetch.ball_location])

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        car = packet.game_cars[self.index]
        
        if not packet.game_info.is_kickoff_pause:
            # run kickoff behaviour
            self.behaviour.reset()
            return self.kickoff.resolve(car, packet)
        else:
            self.kickoff.reset()
            return self.behaviour.resolve(car, packet)
