import math
import rlmath
import situation
from situation import Data
from vec import Vec3,UP
from rlbot.agents.base_agent import SimpleControllerState

REQUIRED_SLIDE_ANG = 1.6


def go_towards_point(data, point: Vec3, slide=False, boost=False) -> SimpleControllerState:
	controller_state = SimpleControllerState()

	car_to_point = point - data.car.location

	steer_correction_radians = data.car.orientation.front.angTo2d(car_to_point)

	do_smoothing = True
	if slide:
		if car_to_point.length() > 300:
			if steer_correction_radians > REQUIRED_SLIDE_ANG or steer_correction_radians < -REQUIRED_SLIDE_ANG:
				controller_state.handbrake = True
				do_smoothing = False

	if do_smoothing:
		controller_state.steer = rlmath.steer_correction_smooth(steer_correction_radians, data.car.angular_velocity.y)
	else:
		if steer_correction_radians > 0:
			controller_state.steer = 1
		elif steer_correction_radians < 0:
			controller_state.steer = -1

	if boost:
		if not data.car.is_on_wall and not do_smoothing and data.car.velocity.length() < 2000:
			if situation.is_heading_towards2(steer_correction_radians, car_to_point.length()):
				if data.car.orientation.up.angTo(UP) < math.pi*0.3:
					controller_state.boost = True

	controller_state.throttle = 1.0

	return controller_state


def go_towards_point_with_timing(data: Data, point: Vec3, eta: float, slide=False):
	controller_state = SimpleControllerState()

	car_to_point = point - data.car.location
	dist = car_to_point.length()

	steer_correction_radians = data.car.orientation.front.angTo2d(car_to_point)

	do_smoothing = True
	if slide:
		if dist > 300:
			if steer_correction_radians > REQUIRED_SLIDE_ANG or steer_correction_radians < -REQUIRED_SLIDE_ANG:
				controller_state.handbrake = True
				do_smoothing = False

	if do_smoothing:
		controller_state.steer = rlmath.steer_correction_smooth(steer_correction_radians, data.car.angular_velocity.y)
	else:
		if steer_correction_radians > 0:
			controller_state.steer = 1
		elif steer_correction_radians < 0:
			controller_state.steer = -1

	vel_f = data.car.velocity.proj_onto(car_to_point).length()
	alpha = 1.3  # interpolation parameter
	avg_vel_f = dist / eta
	target_vel_f = (1.0 - alpha) * vel_f + alpha * avg_vel_f

	if vel_f < target_vel_f:
		controller_state.throttle = 1.0
		# boost?
		if target_vel_f > 1410:
			if not data.car.is_on_wall and not do_smoothing and data.car.velocity.length() < 2000:
				if situation.is_heading_towards2(steer_correction_radians, dist):
					if data.car.orientation.up.angTo(UP) < math.pi * 0.3:
						controller_state.boost = True
	else:
		if (vel_f - target_vel_f) > 75:
			controller_state.throttle = -1.0

	return controller_state
