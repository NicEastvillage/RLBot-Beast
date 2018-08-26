import math
import rlmath
import rlutility
import predict
from vec import *

from rlbot.utils.structures.game_data_struct import GameTickPacket

# If you stand in blue goal and look at orange goal. positive y is forwards and positive x is left

ARENA_LENGTH = 10280    # y
ARENA_WIDTH = 8240      # x
ARENA_HEIGHT = 2044     # z
ARENA_LENGTH2 = ARENA_LENGTH / 2
ARENA_WIDTH2 = ARENA_WIDTH / 2

GOAL_LENGTH = 650
GOAL_WIDTH = 1900
GOAL_WIDTH2 = GOAL_WIDTH / 2
GOAL_HEIGHT = 615

CAR_LENGTH = 118
CAR_WIDTH = 84
CAR_HEIGHT = 36

BALL_RADIUS = 91.21

BLUE_HALF_ZONE = Zone(Vec3(-ARENA_WIDTH2, -ARENA_LENGTH2), Vec3(ARENA_WIDTH2, 0, ARENA_HEIGHT))
ORANGE_HALF_ZONE = Zone(Vec3(-ARENA_WIDTH2, ARENA_LENGTH2), Vec3(ARENA_WIDTH2, 0, ARENA_HEIGHT))

BLUE_GOAL_LOCATION = Vec3(y=-ARENA_LENGTH2-100)
ORANGE_GOAL_LOCATION = Vec3(y=ARENA_LENGTH2+100)
BLUE_GOAL_POST_RIGHT = Vec3(893, -ARENA_LENGTH2)
BLUE_GOAL_POST_LEFT = Vec3(-893, -ARENA_LENGTH2)
ORANGE_GOAL_POST_RIGHT = Vec3(-893, ARENA_LENGTH2)
ORANGE_GOAL_POST_LEFT = Vec3(893, ARENA_LENGTH2)

wall_offset = 65
ARENA_EXCEPT_WALLS_ZONE = Zone(Vec3(-ARENA_WIDTH2+wall_offset, -ARENA_LENGTH2+wall_offset),
                               Vec3(ARENA_WIDTH2-wall_offset, ARENA_LENGTH2-wall_offset, ARENA_HEIGHT))


def get_goal_location(team):
    return (BLUE_GOAL_LOCATION, ORANGE_GOAL_LOCATION)[team]


def get_goal_posts(team):
    if team:
        return ORANGE_GOAL_POST_RIGHT, ORANGE_GOAL_POST_LEFT
    else:
        return BLUE_GOAL_POST_RIGHT, BLUE_GOAL_POST_LEFT


def get_half_zone(team):
    return (BLUE_HALF_ZONE, ORANGE_HALF_ZONE)[team]


def on_my_half(team, point):
    if team == 0:
        return point.y <= 0
    else:
        return point.y >= 0


# returns -1 for blue (team 0) and 1 for orange (team 1)
def team_sign(team):
    return (-1, 1)[team]


# returns true if point is closer to the goal belong to specified team than the other point
def is_point_closer_to_goal(point, other, team):
    return (point.y < other.y, point.y > other.y)[team]

class Ball:
    def __init__(self):
        self.location = Vec3()
        self.location_2d = Vec3()
        self.velocity = Vec3()
        self.angular_velocity = Vec3()

    def set_game_ball(self, game_ball):
        self.location = Vec3().set(game_ball.physics.location)
        self.location_2d = self.location.flat()
        self.velocity = Vec3().set(game_ball.physics.velocity)
        self.angular_velocity = Vec3().set(game_ball.physics.angular_velocity)
        return self

    def set(self, other):
        self.location.set(other.location)
        self.location_2d = self.location.flat()
        self.velocity.set(other.velocity)
        self.angular_velocity.set(other.angular_velocity)
        return self

    def copy(self):
        return Ball().set(self)


class Car:
    def __init__(self, game_car):
        self.team = int(game_car.team)
        self.location = Vec3().set(game_car.physics.location)
        self.location_2d = self.location.flat()
        self.velocity = Vec3().set(game_car.physics.velocity)
        self.angular_velocity = Vec3().set(game_car.physics.angular_velocity)
        self.orientation = Orientation(game_car.physics.rotation)
        self.boost = int(game_car.boost)
        self.is_on_wall = not ARENA_EXCEPT_WALLS_ZONE.contains(self.location)
        self.wheel_contact = game_car.has_wheel_contact

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
        self.ang_to_ball_2d = self.orientation.front.ang_to_flat(car_to_ball_2d)

    def relative_location(self, location):
        return relative_location(self.location, location, self.orientation)

class Data:
    def __init__(self, agent, packet: GameTickPacket):
        self.agent = agent
        self.renderer = agent.renderer
        self.packet = packet
        self.ball = Ball().set_game_ball(packet.game_ball)

        self.car = Car(packet.game_cars[agent.index])
        self.enemy = Car(packet.game_cars[1 - agent.index])

        self.car.set_ball_dependent_variables(self.ball)
        self.enemy.set_ball_dependent_variables(self.ball)

        self.__decide_possession()

        # predictions
        self.time_till_hit = predict.time_till_reach_ball(self.ball, self.car)
        self.ball_when_hit = predict.move_ball(self.ball.copy(), self.time_till_hit)

    def __decide_possession(self):
        self.car.possession_score = self.__get_possession_score(self.car)
        self.enemy.possession_score = self.__get_possession_score(self.enemy)
        self.car.has_possession = self.car.possession_score >= self.enemy.possession_score
        self.enemy.has_possession = not self.car.has_possession

    def __get_possession_score(self, car):
        try:
            car_to_ball = self.ball.location - car.location

            dist = car_to_ball.length()
            ang = car.orientation.front.ang_to(car_to_ball)

            return rlutility.dist_01(dist) * rlutility.face_ang_01(ang)
        except ZeroDivisionError:
            return 0
