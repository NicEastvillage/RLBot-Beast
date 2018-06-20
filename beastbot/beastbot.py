import math
import rlmath
from vec import Vec3
import moves
import behaviourtree as bt
import nodes
import datafetch

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket


class Beast(BaseAgent):

    def initialize_agent(self):
        #This runs once before the bot starts up
        self.kickoff = bt.BehaviourTree(bt.RepeatUntilFailure(nodes.TaskGoTo([datafetch.ball_location])))
        self.behaviour = bt.BehaviourTree(
            bt.Sequencer([
                bt.RepeatUntilFailure(bt.Sequencer([
                    # while
                    bt.Selector([
                        nodes.GuardDistanceLessThan([500, datafetch.my_location, datafetch.ball_location]),
                        # or
                        nodes.GuardIsPointInZone([datafetch.ball_location, datafetch.my_half_zone])
                    ]),
                    # do
                    nodes.TaskGoTo([datafetch.ball_location])
                ])),
                bt.RepeatUntilFailure(bt.Sequencer([
                    # while
                    bt.Inverter(nodes.GuardDistanceLessThan([200, datafetch.my_location, datafetch.my_goal_location])),
                    # do
                    nodes.TaskGoTo([datafetch.my_goal_location])
                ])),
                bt.RepeatUntilFailure(bt.Sequencer([
                    # while
                    nodes.GuardIsPointInZone([datafetch.ball_location, datafetch.enemy_half_zone]),
                    # do
                    nodes.TaskWait()
                ])),
            ]))
            
        #nodes.TaskGoTo([datafetch.ball_location])

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        car = packet.game_cars[self.index]
        
        if not packet.game_info.is_kickoff_pause:
            # run kickoff behaviour
            self.behaviour.reset()
            return self.kickoff.resolve(car, packet)
        else:
            self.kickoff.reset()
            return self.behaviour.resolve(car, packet)
