import time

from ledcube.core.color import Color
from ledcube.core.cube import Cube
from ledcube.core.utils import load_font


class CubeFaces(Cube):

    def run(self):
        f = load_font('10x20.bdf')
        for p in self.planes:
            p.text(26, 25, Color.YELLOW(), f'{p.get_label()}', f)
            p.border(Color.ORANGE())
        self.refresh()
        while True:
            time.sleep(0.1)
            pass


if __name__ == "__main__":
    s = CubeFaces()
    try:
        s.setup()
        s.run()
    except KeyboardInterrupt:
        print("bye\n")
        s.clear()
