import math
import rlmath
from vec2 import Vec2

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

REQUIRED_SLIDE_ANG = 1.6

def go_to_point(car, packet: GameTickPacket, point: Vec2, slide=False) -> SimpleControllerState:
	controller_state = SimpleControllerState()
	
	car_location = Vec2(car.physics.location.x, car.physics.location.y)
	car_direction = rlmath.get_car_facing_vector(car)
	car_to_ball = point - car_location
	
	steer_correction_radians = car_direction.correction_to(car_to_ball)
	
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
	
	controller_state.steer = steer_correction
	controller_state.throttle = 1.0
	
	return controller_state