import math
import rlmath
from vec import Vec3,Zone
import behaviourtree as bt
import moves
import datalibs

from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

# sig: None
class Wait(bt.BTNode):
	def __init__(self):
		super().__init__()
		
	def resolve(self, prev_status, car, packet: GameTickPacket):
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

# sig: None
class PushBall(bt.BTNode):
	def __init__(self):
		super().__init__()
	
	def resolve(self, prev_status, car, packet: GameTickPacket):
		car_location = Vec3(car.physics.location.x, car.physics.location.y)
		ball_location = Vec3(packet.game_ball.physics.location.x, packet.game_ball.physics.location.y, packet.game_ball.physics.location.z)
		ball_velocity = Vec3(packet.game_ball.physics.velocity.x, packet.game_ball.physics.velocity.y, packet.game_ball.physics.velocity.z)
		
		own_goal_direction = datalibs.get_goal_direction(car, packet)
		ball_predicted = ball_location + 0.08 * ball_velocity + Vec3(y=own_goal_direction * 50)
		
		dist = (car_location - ball_predicted.in2D()).length()
		shouldBoost = dist > 500
		
		controller = moves.go_towards_point(car, packet, ball_predicted, slide=True, boost=shouldBoost)
		return (bt.ACTION, self.parent, controller)

# sig: <point>
class FacePoint(bt.BTNode):
	def __init__(self, arguments):
		super().__init__()
		self.pointFunc = arguments[0]
	
	def resolve(self, prev_status, car, packet: GameTickPacket):
		point = self.pointFunc(car, packet)
		car_location = Vec3(car.physics.location.x, car.physics.location.y)
		car_direction = rlmath.get_car_facing_vector(car)
		yaw_velocity = car.physics.angular_velocity.x
		car_velocity = Vec3(car.physics.velocity.x, car.physics.velocity.y)
		car_to_point = point - car_location
		
		steer_correction_radians = rlmath.fix_ang(car_direction.angTo2d(car_to_point) + yaw_velocity * 0.2)
		velocity_correction_radians = car_velocity.angTo2d(car_to_point)
		
		controller = SimpleControllerState()
		
		if abs(steer_correction_radians) > 0.5:
			controller.handbrake = True
		else:
			return (bt.SUCCESS, self.parent, None)
		
		if steer_correction_radians > 0:
			controller.steer = 1
		elif steer_correction_radians < 0:
			controller.steer = -1
		
		controller.throttle = 0.3
		# In these cases we want to brake instead
		if car_velocity.length() > 500:
			controller.throttle = 0
		
		return (bt.ACTION, self, controller)