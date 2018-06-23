import math

def linear(t):
	return t

def flip(t):
	return 1-t

def smooth_start(n, t):
	return t**n

def smooth_stop(n, t):
	return 1-(1-t)**n

def mix(c, A, B, t):
	return c*A(t) + (1-c)*B(t)

def crossfade(A, B, t):
	return (1-t)*A(t) + t*B(t)

def smooth_step(n, t):
	return (1-t)*t**(n-1) + t*(1-(1-t)**(n-1))

def arch(n, t):
	return (t*(1-t))**n

def arch_tall(n, t):
	return arch(n, t)/arch(n, 0.5)

def simple_bezier(t):
	return -2*t*t*t + 3*t*t

def bezier4(t):
	u = 1-t
	return t*t*t + 3*t*t*u

def hesitate2(t):
	return 2*t*(1-t)*(1-t) + t*t
	
def hesitate3(t):
	return 3*t*(1-t)*(1-t) + t*t*t

def inv_lerp(low, high, t):
	if high-low == 0:
		return 0
	return (t-low)/(high-low)

def to_01(low, high, t):
	return inv_lerp(low, high, t)

def lerp(low, high, t):
	return low + t*(high-low)

def from_01(high, low, t):
	return lerp(low, high, t)

def remap(prev_low, prev_high, new_low, new_high, t):
	out = inv_lerp(prev_low, prev_high, t)
	out = lerp(new_low, new_high, out)
	return out

def fix(t):
	if t > 1:
		return 1
	if t < 0:
		return 0
	return t