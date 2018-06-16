from vec2 import Vec2

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

SUCCESS = 0
FAILURE = 1
EVALUATING = 2
ACTION = 3

class BTNode:
	def __init__(self, arguments):
		parent = None
		children = []
	
	def resolve(self, prev_status, car, packet: GameTickPacket):
		# Here the node will calculate and do stuff
		# Returns a tuple (int, BTNode, SimpleControllerState) with status,
		# the next node to be called (eg. parent, self, or child), and a controller state (when status == ACTION)
		# Remember to reset when nercessary
		pass
		
	def add_child(self, child):
		children.append(child)
		child.parent = self

class BehaviourTree:
	def __init__(self, node):
		self.root = node
		self.current = node
	
	def resolve(self, car, packet: GameTickPacket) -> SimpleControllerState:
		if self.current:
			# Evaluate until an action is found
			val = self.current.resolve(ACTION, car, packet)
			while val[0] != ACTION:
				self.current = val[1]
				if self.current == None:
					# We have reached the root, do nothing but start from root next time
					self.current == self.root
					return SimpleControllerState()
					
				val = self.current.resolve(val[0], car, packet)
			
			controller_state = val[2]
			return controller_state
			
		return SimpleControllerState()