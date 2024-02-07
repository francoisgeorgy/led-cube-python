from ledcube.core.color import Color
from ledcube.core.cube import Cube
from ledcube.core.utils import load_font


class CubeLayout(Cube):

    def run(self):
        self.clear()
        f1 = load_font('9x18.bdf')
        f2 = load_font('5x8.bdf')
        while True:
            for p in self.planes:
                p.text(2, 50, Color.YELLOW(), f'{p.offset.x} {p.offset.y}', f1)
                p.text(2, 38, Color.YELLOW(), f'{p.get_name()}', f1)
                p.text(21, 10, Color.BLUE(), 'panel', f2)
                p.text(3, 2, Color.BLUE(), '___bottom___', f2)
                p.border(Color.ORANGE())
            self.refresh()


if __name__ == "__main__":
    s = CubeLayout()
    print("CTRL-C to quit", end="", flush=True)
    try:
        s.setup()
        s.run()
    except KeyboardInterrupt:
        print("\r\033[Kbye")  # \r : go to beginning of line; \033[K : clear from cursor to the end of the line
        s.clear()
