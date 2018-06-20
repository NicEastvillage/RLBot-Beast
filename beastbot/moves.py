import math
import rlmath
import situation
from vec import Vec3

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

REQUIRED_SLIDE_ANG = 1.6

def go_towards_point(car, packet: GameTickPacket, point: Vec3, slide=False, boost=False) -> SimpleControllerState:
	controller_state = SimpleControllerState()
	
	car_location = Vec3(car.physics.location.x, car.physics.location.y)
	car_direction = rlmath.get_car_facing_vector(car)
	car_to_point = point - car_location
	
	steer_correction_radians = car_direction.angTo2d(car_to_point)
	
	do_smoothing = True
	if slide:
		if steer_correction_radians > REQUIRED_SLIDE_ANG or steer_correction_radians < -REQUIRED_SLIDE_ANG:
			controller_state.handbrake = True
			do_smoothing = False
			
	steer_correction = 0
	
	if do_smoothing:
		steer_correction = rlmath.steer_correction_smooth(steer_correction_radians)
	else:
		if steer_correction_radians > 0:
			steer_correction = 1
		elif steer_correction_radians < 0:
			steer_correction = -1
	
	if boost:
		if is_heading_towards(steer_correction_radians, car_to_point.length()):
			controller_state.boost = True
	
	controller_state.steer = steer_correction
	controller_state.throttle = 1.0
	
	return controller_state

def is_heading_towards(ang, dist):
	required_ang = (math.pi / 2) * (dist / situation.ARENA_LENGTH)
	return ang <= required_ang