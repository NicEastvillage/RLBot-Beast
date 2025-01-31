import math
from typing import List

from utility.curves import bezier
from utility.vec import Vec3, cross, normalize, axis_to_rotation, dot


def draw_ball_path(bot, duration: float, step_size: int):
    pred = bot.ball_prediction
    if pred is not None and duration > 0 and step_size > 0:
        max_slice = int(math.ceil(duration * 120))
        locations = [s.physics.location for s in pred.slices[0:max_slice:step_size]]
        if len(locations) > 0:
            bot.renderer.draw_polyline_3d(locations, bot.renderer.create_color(255, 255, 0, 0))


def draw_circle(bot, center: Vec3, normal: Vec3, radius: float, pieces: int):
    # Construct the arm that will be rotated
    arm = normalize(cross(normal, center)) * radius
    angle = 2 * math.pi / pieces
    rotation_mat = axis_to_rotation(angle * normalize(normal))
    points = [center + arm]

    for i in range(pieces):
        arm = dot(rotation_mat, arm)
        points.append(center + arm)

    bot.renderer.draw_polyline_3d(points, bot.renderer.orange)


def draw_bezier(bot, points: List[Vec3], time_step: float=0.05):
    time = 0
    last_point = points[0]
    while time < 1:
        time += time_step
        current_point = bezier(time, points)
        bot.renderer.draw_line_3d(last_point, current_point, bot.renderer.create_color(255, 180, 255, 210))
        last_point = current_point
