import time

from RLUtilities.Maneuvers import AirDodge
from rlbot.agents.base_agent import SimpleControllerState

import render
from plans import DodgePlan
from rlmath import *


class DriveController:
    def __init__(self):
        self.controls = SimpleControllerState()
        self.dodge = None
        self.last_point = None
        self.car = None
        self.last_dodge_end_time = 0
        self.dodge_cooldown = 0.26

    def start_dodge(self):
        if self.dodge is None:
            self.dodge = DodgePlan(self.last_point)

    def go_towards_point(self, bot, point: vec3, target_vel=1430, slide=False, boost=False, can_keep_speed=True, can_dodge=True, wall_offset_allowed=130) -> SimpleControllerState:
        REQUIRED_ANG_FOR_SLIDE = 1.65
        REQUIRED_VELF_FOR_DODGE = 950

        car = bot.info.my_car

        # Get down from wall by choosing a point close to ground
        if not is_near_wall(point, wall_offset_allowed) and angle_between(car.up(), vec3(0, 0, 1)) > math.pi * 0.31:
            point = lerp(xy(car.pos), xy(point), 0.5)

        car_to_point = point - car.pos

        # Dodge over
        if self.dodge is not None and self.dodge.finished:
            self.dodge = None
            self.last_dodge_end_time = time.time()

        # Continue dodge
        if self.dodge is not None:

            self.dodge.target = point
            self.dodge.execute(bot)

            return self.dodge.controls

        # The vector from the car to the point in local coordinates:
        # point_local[X]: how far in front of my car
        # point_local[Y]: how far to the left of my car
        # point_local[Z]: how far above my car
        point_local = dot(point - car.pos, car.theta)

        # Angle to point in local xy plane and other stuff
        angle = math.atan2(point_local[Y], point_local[X])
        dist = norm(point_local)
        vel_f = proj_onto_size(car.vel, car.forward())
        vel_towards_point = proj_onto_size(car.vel, car_to_point)

        # Start dodge
        if can_dodge and abs(angle) <= 0.02 and vel_towards_point > REQUIRED_VELF_FOR_DODGE\
                and dist > vel_towards_point + 500 + 500 and time.time() > self.last_dodge_end_time + self.dodge_cooldown:
            self.dodge = DodgePlan(point)

        # Is in turn radius deadzone?
        tr = turn_radius(abs(vel_f + 50))  # small bias
        tr_side = sign(angle)
        tr_center_local = vec3(0, tr * tr_side, 0)
        point_is_in_turn_radius_deadzone = norm(point_local - tr_center_local) < tr
        # Draw turn radius deadzone
        if car.on_ground and bot.do_rendering:
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
            self.controls.steer = clip(angle + (2.5*angle) ** 3, -1.0, 1.0)
            if slide and dist > 300 and abs(angle) > REQUIRED_ANG_FOR_SLIDE and abs(point_local[Y]) < tr * 6:
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

        # Save for things for later
        self.car = car
        self.last_point = point

        return self.controls



class AimCone:
    def __init__(self, right_most, left_most):
        # Right angle and direction
        if isinstance(right_most, float):
            self.right_ang = fix_ang(right_most)
            self.right_dir = vec3(math.cos(right_most), math.sin(right_most))
        elif isinstance(right_most, vec3):
            self.right_ang = math.atan2(right_most[Y], right_most[X])
            self.right_dir = normalize(right_most)
        # Left angle and direction
        if isinstance(left_most, float):
            self.left_ang = fix_ang(left_most)
            self.left_dir = vec3(math.cos(left_most), math.sin(left_most))
        elif isinstance(left_most, vec3):
            self.left_ang = math.atan2(left_most[Y], left_most[X])
            self.left_dir = normalize(left_most)

    def contains_direction(self, direction):
        # Direction can be both a angle or a vec3. Determine angle
        if isinstance(direction, float):
            ang = direction
        elif isinstance(direction, vec3):
            ang = math.atan2(direction[Y], direction[X])
        else:
            print("Err: direction is not an angle or vec3")
            ang = 0

        # Check if direction is with cone
        if self.right_ang < self.left_ang:
            return not (self.right_ang >= ang or ang >= self.left_ang)
        else:
            return not (self.right_ang >= ang >= self.left_ang)

    def span_size(self):
        if self.right_ang < self.left_ang:
            return math.tau + self.right_ang - self.left_ang
        else:
            return self.right_ang - self.left_ang

    def get_center_ang(self):
        return fix_ang(self.right_ang - self.span_size() / 2)

    def get_center_dir(self):
        ang = self.get_center_ang()
        return vec3(math.cos(ang), math.sin(ang), 0)

    def get_goto_point(self, bot, point):
        point = xy(point)
        desired_dir = self.get_center_dir()

        desired_dir_inv = -1 * desired_dir
        car_loc = xy(bot.info.my_car.pos)
        point_to_car = car_loc - point

        ang_to_desired_dir = angle_between(desired_dir_inv, point_to_car)

        ANG_ROUTE_ACCEPTED = math.pi / 5.0
        can_go_straight = abs(ang_to_desired_dir) < self.span_size() / 2.0
        can_with_route = abs(ang_to_desired_dir) < self.span_size() / 2.0 + ANG_ROUTE_ACCEPTED
        point = point + desired_dir_inv * 50
        if can_go_straight:
            return point, 1.0
        elif can_with_route:
            ang_to_right = abs(angle_between(point_to_car, -1 * self.right_dir))
            ang_to_left = abs(angle_between(point_to_car, -1 * self.left_dir))
            closest_dir = self.right_dir if ang_to_right < ang_to_left else self.left_dir

            bx = point[X]
            by = point[Y]
            cx = car_loc[X]
            cy = car_loc[Y]
            dx = closest_dir[X]
            dy = closest_dir[Y]

            t = - (bx * bx - 2 * bx * cx + by * by - 2 * by * cy + cx * cx + cy * cy) / (
                        2 * (bx * dx + by * dy - cx * dx - cy * dy))
            t = clip(t, -1700, 1700)

            goto = point + 1.0 * t * closest_dir

            goto[X] = clip(goto[X], -FIELD_WIDTH / 2, FIELD_WIDTH / 2)
            goto[Y] = clip(goto[Y], -FIELD_LENGTH / 2, FIELD_LENGTH / 2)

            bot.renderer.draw_line_3d(car_loc, goto, bot.renderer.create_color(255, 150, 150, 150))
            bot.renderer.draw_line_3d(point, goto, bot.renderer.create_color(255, 150, 150, 150))
            return goto, 0.5
        else:
            return None, 1

    def draw(self, bot, center, arm_len=500, arm_count=5, r=255, g=255, b=255):
        renderer = bot.renderer
        ang_step = self.span_size() / (arm_count - 1)

        for i in range(arm_count):
            ang = self.right_ang - ang_step * i
            arm_dir = vec3(math.cos(ang), math.sin(ang), 0)
            end = center + arm_dir * arm_len
            alpha = 255 if i == 0 or i == arm_count - 1 else 110
            renderer.draw_line_3d(center, end, renderer.create_color(alpha, r, g, b))


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
