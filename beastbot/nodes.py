import math
from vec2 import Vec2
import behaviourtree as bt
import moves

from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

# sig: <point:Vec2Func>
class TaskGoTo(bt.BTNode):
	def __init__(self, arguments):
		super().__init__()
		self.pointFunc = arguments[0]
	
	def resolve(self, prev_status, car, packet: GameTickPacket):
		point = self.pointFunc(car, packet)
		controller = moves.go_to_point(car, packet, point, slide=True)
		return (bt.ACTION, self.parent, controller)

# sig: <dist:float> <pointA:Vec2Func> <pointB:Vec2Func>	
class GuardDistanceLessThan(bt.BTNode):
	def __init(self, arguments):
		super().__init__()
		self.dist = arguments[0]
		self.pointAFunc = arguments[1]
		self.pointBFunc = arguments[2]
	
	def resolve(self, prev_status, car, packet: GameTickPacket):
		pointA = self.pointAFunc(car, packet)
		pointB = self.pointBFunc(car, packet)
		
		if pointA.dist2(pointB) < self.dist * self.dist:
			return (bt.SUCCESS, self.parent, None)
		else:
			return (bt.FAILURE, self.parent, None)