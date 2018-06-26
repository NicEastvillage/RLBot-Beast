import math
import easing

MAX_DIST = 13_000

def dist_01(dist):
	return dist/MAX_DIST

def drive_ang_01(ang):
	return abs(math.cos(ang))

def face_ang_01(ang):
	return easing.fix(math.cos(ang))

class UtilitySystem:
	def __init__(self, choices):
		self.choices = choices
		self.scores = [0]*len(choices)
		self.best_index = -1
	
	def evaluate(self, car, packet):
		for i, ch in enumerate(self.choices):
			self.scores[i] = ch.utility(car, packet)
			if i == self.best_index:
				self.scores[i] += 0.15 # was previous best choice bias
		
		prev_best_index = self.best_index
		self.best_index = self.scores.index(max(self.scores))
		
		if prev_best_index != self.best_index:
			# Check if choice has a reset method, then call it
			reset_method = getattr(self.choices[prev_best_index], "reset", None)
			if callable(reset_method):
				reset_method()
		
		return self.choices[self.best_index]
	
	def reset(self):
		self.best_index = -1