import math
import easing

MAX_DIST = 13_000

def dist_01(dist):
	return dist/MAX_DIST

def drive_ang_01(ang):
	return abs(math.cos(ang))

def face_ang_01(ang):
	return easing.fix(math.cos(ang))