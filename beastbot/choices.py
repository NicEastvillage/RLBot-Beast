import moves
import rlmath
import rlutility as rlu
from vec import Vec3

class SpecificBoostPad:
	def __init__(self, info, index):
		self.info = info
		self.index = index
		self.location = Vec3().set(info.location)
	
	def utility(self, car, packet):
		car_loc = Vec3(car.physics.location.x, car.physics.location.y, car.physics.location.z)
		car_direction = rlmath.get_car_facing_vector(car)
		car_to_pad = self.location - car_loc
		state = packet.game_boosts[self.index]
		
		dist = 1-rlu.dist_01(car_loc.dist(self.location))
		ang = rlu.face_ang_01(car_direction.angTo2d(car_to_pad))
		active = state.is_active
		
		return dist*ang*active
	
	def execute(self, car, packet):
		return moves.go_towards_point(car, packet, self.location, True, self.info.is_full_boost)