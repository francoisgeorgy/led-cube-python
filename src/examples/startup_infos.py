import time

import segno

from ledcube.core.color import Color
from ledcube.core.cube import Cube
from ledcube.core.remote import get_cube_ip
from ledcube.core import Face
from ledcube.core.utils import reverse


class StartupInfos(Cube):

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
        ip = get_cube_ip()
        a = ip.split('.')

        qr = segno.make_qr(f"http://{ip}:5040/", version=2)

        # Convert QR code to a binary matrix
        qr_matrix = []
        for row in qr.matrix_iter(scale=2):
            qr_matrix.append([col == 0x1 for col in row])

        c = Color.WHITE()
        while True:
            self.clear()
            p = self.planes[Face.FRONT.value]
            y = 0
            for row in qr_matrix:
                x = 0
                for col in row:
                    if col:
                        p.pixel(x, reverse(y), c)
                    x = x + 1
                y = y + 1

            uptime_h = int(time.monotonic() // 3600)
            uptime_m = (int(time.monotonic()) % 3600) // 60
            uptime_s = int(time.monotonic()) % 60

            # self.planes[Face.TOP.value].text(3, 52, Color.GREY(), hostname)
            self.planes[Face.TOP.value].text(3, 52, Color.GREY(), f'{a[0]}.{a[1]}.')
            self.planes[Face.TOP.value].text(3, 42, Color.GREY(), f'{a[2]}.{a[3]}')
            self.planes[Face.TOP.value].text(3, 32, Color.GREY(), f':5040')
            self.planes[Face.TOP.value].text(2, 2, Color.GREY(), f'{uptime_h:02}:{uptime_m:02}:{uptime_s:02}')
            self.refresh()
            time.sleep(0.1)


if __name__ == "__main__":
    s = StartupInfos()
    try:
        s.setup()
        s.animation()
        s.run()
    except KeyboardInterrupt:
        s.clear()
