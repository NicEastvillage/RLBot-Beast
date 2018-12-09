
# This renderer replaces the framework renderer, and allows me to disable any rendering,
# and thus saving some CPU power. Not all methods are included
class FakeRenderer:
    def __init__(self):
        pass

    def begin_rendering(self):
        pass

    def end_rendering(self):
        pass

    def create_color(self, a, r, g, b):
        pass

    def draw_string_2d(self, x, y, scale_x, scale_y, text, color):
        pass

    def draw_rect_3d(self, location, width, height, fill, color):
        pass

    def draw_string_3d(self, location, scale_x, scale_y, text, color):
        pass

    def draw_line_3d(self, start, end, color):
        pass

    def draw_polyline_3d(self, locs, color):
        pass
