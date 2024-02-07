import datetime
import random

from ledcube.core import Face
from ledcube.core.color import Color
from ledcube.core.cube import Cube


class CubeInfos(Cube):

    def __init__(self):
        super().__init__()

    def run(self):
        t = datetime.datetime(2000, 1, 1)    # any date in the past, to force the force refresh
        elapsed = 0
        while True:
            if (datetime.datetime.now() - t).seconds >= 1:
                t = datetime.datetime.now()
                self.clear()
                elapsed = elapsed + 1
                self.planes[Face.TOP.value].text(
                    random.randint(0, 55), random.randint(0, 55), Color.GREY(), f'{elapsed}')
                self.refresh()


if __name__ == "__main__":
    s = CubeInfos()
    try:
        s.setup()
        # s.animation()
        s.run()
    except KeyboardInterrupt:
        print("bye\n")
        s.clear()
