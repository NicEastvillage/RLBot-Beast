from behaviour.behaviourtree import BTNode, SUCCESS, FAILURE

from rlbot.utils.structures.game_data_struct import GameTickPacket


# sig: <dist:float!> <pointA:Vec3Func> <pointB:Vec3Func>	
class DistanceLessThan(BTNode):
	def __init__(self, arguments):
		super().__init__()
		self.dist = arguments[0]
		self.pointAFunc = arguments[1]
		self.pointBFunc = arguments[2]
	
	def resolve(self, prev_status, car, packet: GameTickPacket):
		pointA = self.pointAFunc(car, packet)
		pointB = self.pointBFunc(car, packet)
		
		if pointA.dist2(pointB) < (self.dist * self.dist):
			return (SUCCESS, self.parent, None)
		else:
			return (FAILURE, self.parent, None)


# sig: <point:Vec3> <zone:Zone>
class IsPointInZone(BTNode):
	def __init__(self, arguments):
		super().__init__()
		self.pointFunc = arguments[0]
		self.zoneFunc = arguments[1]
	
	def resolve(self, prev_status, car, packet: GameTickPacket):
		point = self.pointFunc(car, packet)
		zone = self.zoneFunc(car, packet)
		
		if zone.contains(point):
			return (SUCCESS, self.parent, None)
		else:
			return (FAILURE, self.parent, None)


# sig: <point:Vec3> <z:float!>
class IsPointBelowZ(BTNode):
	def __init__(self, arguments):
		super().__init__()
		self.pointFunc = arguments[0]
		self.z = arguments[1]
	
	def resolve(self, prev_status, car, packet: GameTickPacket):
		point = self.pointFunc(car, packet)
		
		if point.z <= self.z:
			return (SUCCESS, self.parent, None)
		else:
			return (FAILURE, self.parent, None)