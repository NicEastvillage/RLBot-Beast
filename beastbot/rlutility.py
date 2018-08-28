import math
import easing

MAX_DIST = 13_000


def dist_01(dist, max_dist=MAX_DIST):
	return easing.fix(dist / float(max_dist))


def drive_ang_01(ang):
	return abs(math.cos(ang))


def face_ang_01(ang):
	return easing.fix(math.cos(ang))


class UtilitySystem:
	def __init__(self, choices, prev_bias=0.15):
		self.choices = choices
		self.scores = [0] * len(choices)
		self.best_index = -1
		self.prev_bias = prev_bias

	def evaluate(self, data):
		for i, ch in enumerate(self.choices):
			self.scores[i] = ch.utility(data)
			if i == self.best_index:
				self.scores[i] += self.prev_bias  # was previous best choice bias

		prev_best_index = self.best_index
		self.best_index = self.scores.index(max(self.scores))

		if prev_best_index != self.best_index:
			# Check if choice has a reset method, then call it
			reset_method = getattr(self.choices[prev_best_index], "reset", None)
			if callable(reset_method):
				reset_method()

		return self.choices[self.best_index], self.scores[self.best_index]

	def reset(self):
		self.best_index = -1
