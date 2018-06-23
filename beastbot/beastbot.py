import math
import rlmath
from vec import Vec3
import rlutility
import moves
import datafetch

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

class Beast(BaseAgent):

    def initialize_agent(self):
        pass

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        car = packet.game_cars[self.index]
        if car.team == 0:
            car_loc = Vec3().set(car.physics.location)
            car_direction = rlmath.get_car_facing_vector(car)
            self.renderer.begin_rendering()
            b_uts = []
            for pad in self.get_field_info().boost_pads:
                pad_loc = Vec3().set(pad.location)
                dist = car_loc.dist(pad_loc)
                ang = car_direction.angTo2d(pad_loc-car_loc)
                dist01 = rlutility.dist_01(dist)
                ang01 = rlutility.face_ang_01(ang)
                ut = (1-dist01)*ang01
                b_uts.append(ut)
                self.renderer.draw_line_3d(car_loc.tuple(), pad_loc.tuple(), self.renderer.create_color(255, 0, int(ut*255), 0))
                
            best_pad = b_uts.index(max(b_uts))
            best_pad = self.get_field_info().boost_pads[best_pad]
            best_pad_loc = Vec3().set(best_pad.location)
            
            self.renderer.draw_line_3d(car_loc.tuple(), best_pad_loc.tuple(), self.renderer.create_color(255, 255, 0, 0))
            self.renderer.end_rendering()
            return moves.go_towards_point(car, packet, best_pad_loc, boost=True)
        
        controller = SimpleControllerState()
        controller.throttle = 0.5
        return controller
