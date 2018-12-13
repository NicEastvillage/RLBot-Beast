from RLUtilities.Maneuvers import AirDodge
from rlbot.agents.base_agent import SimpleControllerState

import render
from plans import DodgePlan
from rlmath import *


class DriveController:
    def __init__(self):
        self.controls = SimpleControllerState()
        self.dodge = None

    def go_towards_point(self, bot, point: vec3, target_vel=1430, slide=False, boost=False, can_keep_speed=True, can_dodge=True, wall_offset_allowed=130) -> SimpleControllerState:
        REQUIRED_ANG_FOR_SLIDE = 1.65
        REQUIRED_VELF_FOR_DODGE = 800  # 910
        REQUIRED_ANG_FOR_DODGE = 0.3

        car = bot.info.my_car

        # Get down from wall by choosing a point close to ground
        if not is_near_wall(point, wall_offset_allowed) and angle_between(car.up(), vec3(0, 0, 1)) > math.pi * 0.31:
            point = lerp(xy(car.pos), xy(point), 0.5)

        car_to_point = point - car.pos

        # Dodge over
        if self.dodge is not None and self.dodge.finished:
            self.dodge = None

        # Continue dodge
        if self.dodge is not None:

            self.dodge.target = point
            self.dodge.step(0.01666)

            self.dodge.controls.boost = boost and angle_between(car_to_point, car.forward()) < 0.15\
                                        and norm(car.vel) < 2000 and dot(car.up(), car_to_point) >= 0

            return self.dodge.controls

        # The vector from the car to the point in local coordinates:
        # point_local[0]: how far in front of my car
        # point_local[1]: how far to the left of my car
        # point_local[2]: how far above my car
        point_local = dot(point - car.pos, car.theta)

        # Angle to point in local xy plane
        angle = math.atan2(point_local[1], point_local[0])
        dist = norm(point_local)
        vel_f = proj_onto_size(car.vel, car.forward())
        vel_towards_point = proj_onto_size(car.vel, car_to_point)

        # Start dodge
        if can_dodge and is_heading_towards_strict(angle, dist) and vel_towards_point > REQUIRED_VELF_FOR_DODGE and dist > vel_towards_point + 500 + 200:
            self.dodge = AirDodge(car, 0.1, point)

        # Is in turn radius deadzone?
        tr = turn_radius(abs(vel_f + 50))  # small bias
        tr_side = sign(angle)
        tr_center_local = vec3(0, tr * tr_side, 0)
        point_is_in_turn_radius_deadzone = norm(point - tr_center_local) < tr
        # Draw turn radius deadzone
        if car.on_ground:
            tr_center_world = car.pos + dot(car.theta, tr_center_local)
            tr_center_world_2 = car.pos + dot(car.theta, -1 * tr_center_local)
            render.draw_circle(bot, tr_center_world, car.up(), tr, 22)
            render.draw_circle(bot, tr_center_world_2, car.up(), tr, 22)

        if point_is_in_turn_radius_deadzone:
            # Hard turn
            self.controls.throttle = 0 if vel_f > 250 else 0.2
            self.controls.steer = sign(angle)

        else:
            # Should drop speed or just keep up the speed?
            if can_keep_speed and target_vel < vel_towards_point:
                target_vel = vel_towards_point

            # Turn and maybe slide
            self.controls.steer = clip(angle * 2.8, -1.0, 1.0)
            if slide and dist > 300 and abs(angle) > REQUIRED_ANG_FOR_SLIDE and abs(point_local[0]) < tr * 6:
                self.controls.handbrake = True
                self.controls.steer = sign(angle)
            else:
                self.controls.handbrake = False

            # Overshoot target vel for quick adjustment
            target_vel = lerp(vel_towards_point, target_vel, 1.2)

            # Find appropriate throttle/boost
            if vel_towards_point < target_vel:
                self.controls.throttle = 1
                if boost and vel_towards_point + 25 < target_vel \
                        and not self.controls.handbrake and is_heading_towards(angle, dist):
                    self.controls.boost = True
                else:
                    self.controls.boost = False

            else:
                vel_delta = target_vel - vel_towards_point
                self.controls.throttle = clip(vel_delta / 350, -1, 1)
                self.controls.boost = False

        return self.controls

# ----------------------------------------- Helper functions --------------------------------


def is_heading_towards(ang, dist):
    # The further away the car is the less accurate the angle is required
    required_ang = 0.05 + 0.0001 * dist
    return abs(ang) <= required_ang


def is_heading_towards_strict(ang, dist):
    # The further away the car is the less accurate the angle is required
    required_ang = 0.02 + 0.0001 * dist
    return abs(ang) <= required_ang


def turn_radius(vf):
    if vf == 0:
        return 0
    return 1.0 / turn_curvature(vf)


def turn_curvature(vf):
    if 0.0 <= vf < 500.0:
        return 0.006900 - 5.84e-6 * vf
    elif 500.0 <= vf < 1000.0:
        return 0.005610 - 3.26e-6 * vf
    elif 1000.0 <= vf < 1500.0:
        return 0.004300 - 1.95e-6 * vf
    elif 1500.0 <= vf < 1750.0:
        return 0.003025 - 1.10e-6 * vf
    elif 1750.0 <= vf < 2500.0:
        return 0.001800 - 0.40e-6 * vf
    else:
        return 0.0
