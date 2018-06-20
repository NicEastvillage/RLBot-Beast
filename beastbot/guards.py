import math
from vec import Vec3,Zone
import behaviourtree as bt
import moves

from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

# sig: <dist:float!> <pointA:Vec3Func> <pointB:Vec3Func>	
class DistanceLessThan(bt.BTNode):
	def __init__(self, arguments):
		super().__init__()
		self.dist = arguments[0]
		self.pointAFunc = arguments[1]
		self.pointBFunc = arguments[2]
	
	def resolve(self, prev_status, car, packet: GameTickPacket):
		pointA = self.pointAFunc(car, packet)
		pointB = self.pointBFunc(car, packet)
		
		if pointA.dist2(pointB) < (self.dist * self.dist):
			return (bt.SUCCESS, self.parent, None)
		else:
			return (bt.FAILURE, self.parent, None)

# sig: <point:Vec3> <zone:Zone>
class IsPointInZone(bt.BTNode):
	def __init__(self, arguments):
		super().__init__()
		self.pointFunc = arguments[0]
		self.zoneFunc = arguments[1]
	
	def resolve(self, prev_status, car, packet: GameTickPacket):
		point = self.pointFunc(car, packet)
		zone = self.zoneFunc(car, packet)
		
		if zone.contains(point):
			return (bt.SUCCESS, self.parent, None)
		else:
			return (bt.FAILURE, self.parent, None)

# sig: <point:Vec3> <z:float!>
class IsPointBelowZ(bt.BTNode):
	def __init__(self, arguments):
		super().__init__()
		self.pointFunc = arguments[0]
		self.z = arguments[1]
	
	def resolve(self, prev_status, car, packet: GameTickPacket):
		point = self.pointFunc(car, packet)
		
		if point.z <= self.z:
			return (bt.SUCCESS, self.parent, None)
		else:
			return (bt.FAILURE, self.parent, None)