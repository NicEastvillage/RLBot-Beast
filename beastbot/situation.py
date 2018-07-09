import math
import rlmath
import rlutility
from vec import Vec3, Zone, Orientation

from rlbot.utils.structures.game_data_struct import GameTickPacket

ARENA_LENGTH = 10280    # y
ARENA_WIDTH = 8240      # x
ARENA_HEIGHT = 4100     # z
ARENA_LENGTH2 = ARENA_LENGTH / 2
ARENA_WIDTH2 = ARENA_WIDTH / 2

GOAL_LENGTH = 650
GOAL_WIDTH = 1550
GOAL_HEIGHT = 615

CAR_LENGTH = 118
CAR_WIDTH = 84
CAR_HEIGHT = 36

BLUE_DIRECTION = -1
ORANGE_DIRECTION = 1

BLUE_HALF_ZONE = Zone(Vec3(-ARENA_WIDTH2, -ARENA_LENGTH2), Vec3(ARENA_WIDTH2, 0, ARENA_HEIGHT))
ORANGE_HALF_ZONE = Zone(Vec3(-ARENA_WIDTH2, ARENA_LENGTH2), Vec3(ARENA_WIDTH2, 0, ARENA_HEIGHT))

BLUE_GOAL_LOCATION = Vec3(y=-ARENA_LENGTH2-100)
ORANGE_GOAL_LOCATION = Vec3(y=ARENA_LENGTH2+100)

wall_offset = 65
ARENA_EXCEPT_WALLS_ZONE = Zone(Vec3(-ARENA_WIDTH2+wall_offset, -ARENA_LENGTH2+wall_offset),
                               Vec3(ARENA_WIDTH2-wall_offset, ARENA_LENGTH2-wall_offset, ARENA_HEIGHT))

def get_goal_direction(car, packet:GameTickPacket):
	if car.team == 0:
		return BLUE_DIRECTION
	else:
		return ORANGE_DIRECTION


def get_goal_location(car, data):
	if car.team == 0:
		return BLUE_GOAL_LOCATION
	else:
		return ORANGE_GOAL_LOCATION


def is_heading_towards(car, point):
	car_location = Vec3(car.physics.location.x, car.physics.location.y)
	car_direction = rlmath.get_car_facing_vector(car)
	car_to_point = point - car_location
	ang = car_direction.angTo2d(car_to_point)
	dist = car_to_point.length()
	return is_heading_towards2(ang, dist)


def is_heading_towards2(ang, dist):
	required_ang = (math.pi / 3) * (dist / ARENA_LENGTH)
	return ang <= required_ang


def get_half_zone(team):
	if team == 0:
		return BLUE_HALF_ZONE
	else:
		return ORANGE_HALF_ZONE


class Ball:
	def __init__(self):
		self.location = Vec3()
		self.location_2d = Vec3()
		self.velocity = Vec3()
		self.angular_velocity = Vec3()

	def set_game_ball(self, game_ball):
		self.location = Vec3().set(game_ball.phyhics.location)
		self.location_2d = self.location.in2D()
		self.velocity = Vec3().set(game_ball.phyhics.velocity)
		self.angular_velocity = Vec3().set(game_ball.phyhics.angular_velocity)
		return self

	def set(self, other):
		self.location.set(other.location)
		self.location_2d = self.location.in2D()
		self.velocity.set(other.velocity)
		self.angular_velocity.set(other.angular_velocity)
		return self

	def copy(self):
		return Ball().set(self)


class Car:
	def __init__(self, game_car):
		self.team = int(game_car.team)
		self.location = Vec3().set(game_car.physics.location)
		self.location_2d = self.location.in2D()
		self.velocity = Vec3().set(game_car.physics.velocity)
		self.angular_velocity = Vec3().set(game_car.physics.angular_velocity)
		self.orientation = Orientation(game_car.physics.rotation)
		self.boost = int(game_car.boost)
		self.is_on_wall = not ARENA_EXCEPT_WALLS_ZONE.contains(self.location)

		# Default values for variables, set by Data
		self.has_possession = False
		self.possession_score = 0
		self.dist_to_ball = 1000
		self.dist_to_ball_2d = 1000
		self.ang_to_ball_2d = 0

	def set_ball_dependent_variables(self, ball):
		car_to_ball_2d = ball.location_2d - self.location_2d

		self.dist_to_ball = self.location.dist(ball.location)
		self.dist_to_ball_2d = car_to_ball_2d.length()
		self.ang_to_ball_2d = self.orientation.front.angTo2d(car_to_ball_2d)


class Data:
	def __init__(self, index, packet: GameTickPacket):
		self.packet = packet
		self.ball = Ball().set_game_ball(packet.game_ball)

		self.car = Car(packet.game_cars[index])
		self.enemy = Car(packet.game_cars[1 - index])

		self.car.set_ball_dependent_variables(self.ball)
		self.enemy.set_ball_dependent_variables(self.ball)

		self.__decide_possession()

	def __decide_possession(self):
		self.car.possession_score = self.__get_possession_score(self.car)
		self.enemy.possession_score = self.__get_possession_score(self.enemy)
		self.car.has_possession = self.car.possession_score >= self.enemy.possession_score
		self.enemy.has_possession = not self.car.has_possession

	def __get_possession_score(self, car):
		car_to_ball = self.ball.location - car.location

		dist = car_to_ball.length()
		ang = car.orientation.front.angTo(car_to_ball)

		return rlutility.dist_01(dist) * rlutility.face_ang_01(ang)
