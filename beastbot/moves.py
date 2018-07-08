import math
import rlmath
import situation
from vec import Vec3
from rlbot.agents.base_agent import SimpleControllerState

REQUIRED_SLIDE_ANG = 1.6


def go_towards_point(data, point: Vec3, slide=False, boost=False) -> SimpleControllerState:
	controller_state = SimpleControllerState()

	car_to_point = point - data.car.location

	steer_correction_radians = data.car.orientation.front.angTo2d(car_to_point)

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
		if situation.is_heading_towards2(steer_correction_radians, car_to_point.length()):
			controller_state.boost = True

	controller_state.steer = steer_correction
	controller_state.throttle = 1.0

	return controller_state
