import math
from vec2 import Vec2
import behaviourtree as bt
import moves

from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

# Sequencer, aborts on failure by returning failure
class Sequencer(bt.BTNode):
	def __init__(self, children = []):
		super().__init__(children)
		self.next = 0
	
	def resolve(self, prev_status, car, packet: GameTickPacket):
		child_count = len(self.children)
		if child_count <= 0
			print("ERROR: Sequencer has no children!")
		
		# abort
		if prev_status == bt.FAILURE:
			return (bt.FAILURE, self.parent, None)
		
		# resolve next
		if self.next < child_count:
			self.next += 1
			return (bt.EVALUATING, self.children[self.next - 1], None)
		else:
			# out of children, all succeeded!
			return (bt.SUCCESS, self.parent, None)

# Selector, aborts on success by returning success
class Sequencer(bt.BTNode):
	def __init__(self, children = []):
		super().__init__(children)
		self.next = 0
	
	def resolve(self, prev_status, car, packet: GameTickPacket):
		child_count = len(self.children)
		if child_count <= 0
			print("ERROR: Selector has no children!")
		
		# abort
		if prev_status == bt.SUCCESS:
			return (bt.SUCCESS, self.parent, None)
		
		# resolve next
		if self.next < child_count:
			self.next += 1
			return (bt.EVALUATING, self.children[self.next - 1], None)
		else:
			# out of children, all failed!
			return (bt.FAILURE, self.parent, None)

# sig: <point:Vec2Func>
class TaskGoTo(bt.BTNode):
	def __init__(self, arguments):
		super().__init__()
		self.pointFunc = arguments[0]
	
	def resolve(self, prev_status, car, packet: GameTickPacket):
		point = self.pointFunc(car, packet)
		controller = moves.go_to_point(car, packet, point, slide=True)
		return (bt.ACTION, self, controller)
	
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