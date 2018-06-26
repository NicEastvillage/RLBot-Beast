import moves
import rlmath
import rlutility as rlu
import easing
import datafetch
from vec import Vec3

class TouchBall:
	def utility(self, car, packet):
		return 0.26
		car_loc = datafetch.my_location(car, packet)
		ball_loc = datafetch.ball_location(car, packet)
		dist01 = rlu.dist_01((car_loc - ball_loc).length())
		dist01 = 1-easing.smooth_stop(4, dist01)
		
		possession = datafetch.my_possession_score(car, packet)
		
		return easing.lerp(0.15, 0.85, dist01 * possession)
	
	def execute(self, car, packet):
		return moves.go_towards_point(car, packet, datafetch.ball_location(car, packet), True, True)

class CollectBoost:
	def __init__(self, agent):
		boost_choices = []
		for i, pad in enumerate(agent.get_field_info().boost_pads):
			boost_choices.append(SpecificBoostPad(pad, i))
		
		self.collect_boost_system = rlu.UtilitySystem(boost_choices)
	
	def utility(self, car, packet):
		boost01 = float(car.boost / 100.0)
		boost01 = 1-easing.smooth_stop(2, boost01)
		
		best_boost = self.collect_boost_system.evaluate(car, packet)
		time_est = rlmath.estimate_time_to_arrival(car, best_boost.location)
		time01 = 8**(-time_est)
		
		big = 0.20 if best_boost.info.is_full_boost else 0
		
		return easing.fix(boost01 * time01 + big)
	
	def execute(self, car, packet):
		return self.collect_boost_system.evaluate(car, packet).execute(car, packet)
	
	def reset(self):
		self.collect_boost_system.reset()

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