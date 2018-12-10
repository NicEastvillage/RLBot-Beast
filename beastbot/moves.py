from rlbot.agents.base_agent import SimpleControllerState

from plans import DodgePlan
from rlmath import *


def go_towards_point(bot, point: vec3, target_vel=1430, slide=False, boost=False, can_keep_speed=True, wall_offset_allowed=130) -> SimpleControllerState:
    REQUIRED_SLIDE_ANG = 1.65

    controls = SimpleControllerState()

    car = bot.info.my_car

    # Get down from wall by choosing a point close to ground
    if not is_near_wall(point, wall_offset_allowed) and angle_between(car.up(), vec3(0, 0, 1)) > math.pi * 0.31:
        point = lerp(xy(car.pos), xy(point), 0.5)

    car_to_point = point - car.pos

    # The vector from the car to the point in local coordinates:
    # point_local[0]: how far in front of my car
    # point_local[1]: how far to the left of my car
    # point_local[2]: how far above my car
    point_local = dot(point - car.pos, car.theta)

    # Angle to point in local xy plane
    angle = math.atan2(point_local[1], point_local[0])
    dist = norm(point_local)
    vel_towards_point = proj_onto_size(car.vel, car_to_point)

    # Is in turn radius deadzone?
    tr = turn_radius(abs(vel_towards_point + 50))  # small bias
    tr_side = -1 * sign(angle)
    tr_center_local = vec3(0, tr * tr_side, 0)
    point_is_in_turn_radius_deadzone = norm(point - tr_center_local) < tr

    if point_is_in_turn_radius_deadzone:
        # Hard turn
        controls.throttle = 0 if vel_towards_point > 250 else 0.2
        controls.steer = sign(angle)

    else:
        # Should drop speed or just keep up the speed?
        if can_keep_speed and target_vel < vel_towards_point:
            target_vel = vel_towards_point

        # Turn and maybe slide
        controls.steer = clip(angle * 2.8, -1.0, 1.0)
        if slide and dist > 300 and abs(angle) > REQUIRED_SLIDE_ANG:
            controls.handbrake = True
            controls.steer = sign(angle)

        # Overshoot target vel for quick adjustment
        target_vel = lerp(vel_towards_point, target_vel, 1.2)

        # Find appropriate throttle/boost
        if vel_towards_point < target_vel:
            controls.throttle = 1
            if boost and vel_towards_point + 25 < target_vel \
                    and not controls.handbrake and is_heading_towards(angle, dist):

                controls.boost = True

        else:
            vel_delta = target_vel - vel_towards_point
            controls.throttle = clip(vel_delta / 300, -1, 1)

    return controls

# ----------------------------------------- Helper functions --------------------------------


def is_heading_towards(ang, dist):
    # The further away the car is the less accurate the angle is required
    required_ang = 0.05 + 0.0001 * dist
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
