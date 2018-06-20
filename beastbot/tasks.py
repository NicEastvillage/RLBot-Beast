import math
from vec import Vec3,Zone
import behaviourtree as bt
import moves

from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

# sig: None
class Wait(bt.BTNode):
	def __init__(self):
		super().__init__()
		
	def resolve(self, prev_status, car, packet: GameTickPacket):
		print("Waiting")
		return (bt.ACTION, self.parent, SimpleControllerState())

# sig: <point:Vec3Func> <slide:bool> <boost:bool>
class GoTowards(bt.BTNode):
	def __init__(self, arguments):
		super().__init__()
		self.pointFunc = arguments[0]
		self.slide = arguments[1]
		self.boost = arguments[2]
	
	def resolve(self, prev_status, car, packet: GameTickPacket):
		point = self.pointFunc(car, packet)
		controller = moves.go_towards_point(car, packet, point, slide=self.slide, boost=self.boost)
		return (bt.ACTION, self.parent, controller)