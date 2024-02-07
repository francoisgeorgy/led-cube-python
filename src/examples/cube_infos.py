import datetime
import platform
import time

from ledcube.core.color import Color
from ledcube.core.cube import Cube
from ledcube.core.remote import get_cube_ip
from ledcube.core import Face
from ledcube.core.utils import load_font


class CubeInfos(Cube):

    def __init__(self):
        super().__init__()
        # self.font = self.load_font('9x18.bdf')

    #
    #   0 63    width = 64      (64 - 64) / 2
    #   1 62
    #  31 32    width = 2       (64 - 2) / 2
    #
    def centered_square(self, plane, width, color):
        d = (64 - width) // 2
        self.planes[plane].line(d, d, d+width-1, d, color)
        self.planes[plane].line(d+width-1, d, d+width-1, d+width-1, color)
        self.planes[plane].line(d+width-1, d+width-1, d, d+width-1, color)
        self.planes[plane].line(d, d+width-1, d, d, color)

    def animation(self):
        w = 0
        period = 90 * 1000 * 1000      # 0.1 s in [ns]

        while True:
            start_t = time.time_ns()
            self.clear()
            self.centered_square(Face.FRONT.value, w, Color.GREEN())
            self.centered_square(Face.RIGHT.value, w, Color.RED())
            self.centered_square(Face.BACK.value, w, Color.BLUE())
            self.centered_square(Face.LEFT.value, w, Color.RED())
            self.centered_square(Face.TOP.value, w, Color.WHITE())
            self.centered_square(Face.BOTTOM.value, w, Color.YELLOW())
            self.refresh()

            if w >= 64:
                break
            w = w + 2

            delta_t = time.time_ns() - start_t
            wait_t = period - delta_t
            if wait_t > 0:
                time.sleep(wait_t / 1000000000)

    def run(self):
        hostname = platform.node().split('.')[0]
        ip = get_cube_ip()

        large = load_font('9x18.bdf')

        start_time = datetime.datetime(2000, 1, 1)    # any date in the past, to force the force refresh
        t = 0
        while True:
            if (datetime.datetime.now() - start_time).seconds >= 1:
                start_time = datetime.datetime.now()
                self.clear()
                self.planes[Face.FRONT.value].border(Color.GREEN())
                self.planes[Face.RIGHT.value].border(Color.RED())
                self.planes[Face.BACK.value].border(Color.BLUE())
                self.planes[Face.LEFT.value].border(Color.GREEN())
                self.planes[Face.TOP.value].border(Color.WHITE())
                self.planes[Face.BOTTOM.value].border(Color.YELLOW())

                self.planes[Face.FRONT.value].text(28, 28, Color.GREEN(), 'F', large)
                self.planes[Face.RIGHT.value].text(28, 28, Color.RED(), 'R', large)
                self.planes[Face.BACK.value].text(28, 28, Color.BLUE(), 'K', large)
                self.planes[Face.LEFT.value].text(28, 28, Color.GREEN(), 'L', large)
                self.planes[Face.BOTTOM.value].text(28, 28, Color.YELLOW(), 'B', large)

                self.planes[Face.TOP.value].text(3, 52, Color.GREY(), hostname)
                a = ip.split('.')
                self.planes[Face.TOP.value].text(3, 42, Color.GREY(), f'{a[0]}.{a[1]}')
                self.planes[Face.TOP.value].text(3, 32, Color.GREY(), f' .{a[2]}.{a[3]}')

                t = t + 1
                self.planes[Face.TOP.value].text(32, 2, Color.GREY(), f'{t:>5}')
                self.refresh()


if __name__ == "__main__":
    s = CubeInfos()
    try:
        s.setup()
        s.animation()
        s.run()
    except KeyboardInterrupt:
        print("bye\n")
        s.clear()
