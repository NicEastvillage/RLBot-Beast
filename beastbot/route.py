import math
import situation
from situation import Data
from vec import Vec3


def draw_route(renderer, route):
	if len(route) < 2:
		return
	renderer.begin_rendering()
	prev_loc_t = route[0].tuple()
	for loc in route[1:]:
		loc_t = loc.tuple()
		renderer.draw_line_3d(prev_loc_t, loc_t, renderer.create_color(255, 255, 255, 0))
		prev_loc_t = loc_t
	renderer.end_rendering()


def get_route(data: Data):
	time_step_size = 0.1
	dist_step_size = 1350 * time_step_size
	max_turn_ang = math.pi * 0.1

	ball_init_loc = data.ball.location_2d
	ball_to_goal = (situation.get_goal_location(data.enemy, data) - ball_init_loc)
	ball_init_dir = ball_to_goal.in2D().normalized()*-1
	car_init_loc = data.car.location.in2D()
	car_init_dir = data.car.orientation.front.in2D().normalized()

	steps_taken = 0
	ball_visited = []
	car_visited = [car_init_loc]

	while steps_taken < 13:
		ball_cur_loc = ball_init_loc
		ball_cur_dir = ball_init_dir

		ball_visited = [ball_cur_loc]

		ball_to_car = car_init_loc - ball_cur_loc
		ang_diff = ball_cur_dir.angTo2d(ball_to_car)

		for i in range(steps_taken):
			ball_to_car = car_init_loc - ball_cur_loc
			ang_diff = ball_cur_dir.angTo2d(ball_to_car)
			ball_turn_dir = 1 if ang_diff > 0 else -1

			if i > 1:
				ball_cur_dir = ball_cur_dir.rotate_2d(min(max_turn_ang, abs(ang_diff)) * ball_turn_dir)
			ball_cur_loc += ball_cur_dir * dist_step_size

			ball_visited.append(ball_cur_loc)

		if math.pi - abs(ang_diff) < max_turn_ang or ball_to_car.length2() < dist_step_size*dist_step_size:
			break

		steps_taken += 1

	car_visited.extend(reversed(ball_visited))
	return car_visited