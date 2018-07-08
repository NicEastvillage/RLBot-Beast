import math
import situation
from situation import Data
from vec import Vec3


def draw_route(renderer, data: Data):
	route = get_route(data)

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

	ball_init_loc = data.ball_location.in2D()
	ball_to_goal = (situation.get_goal_location(data.enemy, data) - ball_init_loc)
	ball_init_dir = ball_to_goal.in2D().normalized()*-1
	car_init_loc = data.car.location.in2D()
	car_init_dir = data.car.orientation.front.in2D().normalized()

	steps_taken = 0
	ball_visited = []
	car_visited = []

	while steps_taken < 20:
		ball_cur_loc = ball_init_loc
		ball_cur_dir = ball_init_dir
		car_cur_loc = car_init_loc
		car_cur_dir = car_init_dir

		ball_visited = [ball_cur_loc]
		car_visited = [car_cur_loc]

		ang_diff = ball_cur_dir.angTo2d(car_cur_dir)

		for i in range(steps_taken):
			car_to_ball = ball_cur_loc - car_cur_loc
			ball_miss_ang = ball_cur_dir.angTo2d(-1 * car_to_ball)
			car_miss_ang = car_cur_dir.angTo2d(car_to_ball)
			ball_turn_dir = 1 if ball_miss_ang > 0 else -1
			car_turn_dir = 1 if car_miss_ang > 0 else -1

			ball_cur_dir = ball_cur_dir.rotate_2d(min(max_turn_ang, abs(ball_miss_ang)) * ball_turn_dir)
			ball_cur_loc += ball_cur_dir * dist_step_size
			car_cur_dir = car_cur_dir.rotate_2d(min(max_turn_ang, abs(car_miss_ang)) * car_turn_dir)
			car_cur_loc += car_cur_dir * dist_step_size

			ball_visited.append(ball_cur_loc)
			car_visited.append(car_cur_loc)

			ang_diff = ball_cur_dir.angTo2d(car_cur_dir)

		if math.pi - abs(ang_diff) < max_turn_ang:
			break

		steps_taken += 1

	car_visited.extend(reversed(ball_visited))
	return car_visited
