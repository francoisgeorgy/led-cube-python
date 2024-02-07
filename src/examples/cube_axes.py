from ledcube.core.color import Color
from ledcube.core.cube import Cube
from ledcube.core.utils import load_font

BORDER_COLOR = Color.BLUE()
AXES_COLOR = Color.ORANGE()


class CubeAxes(Cube):

    def __init__(self):
        super().__init__()

    def run(self):
        f = load_font('6x9.bdf')
        while True:
            for p in self.planes:
                p.border(BORDER_COLOR)
                p.draw_x_axis(AXES_COLOR, font=f)
                p.draw_y_axis(AXES_COLOR, font=f)
                p.draw_z_axis(AXES_COLOR, font=f)
                p.text(50, 50, Color.WHITE(), f'{p.get_label()}')
            self.refresh()


if __name__ == "__main__":
    s = CubeAxes()
    try:
        s.setup()
        s.run()
    except KeyboardInterrupt:
        print("bye\n")
        s.clear()
