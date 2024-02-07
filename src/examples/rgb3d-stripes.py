import math
import random

from ledcube.core.color import Color
from ledcube.core.cube import Cube
from ledcube.core.mapper_matrix_to_cube import canvas_to_3d


class RGB3DStripes(Cube):
    
    def __init__(self):
        super().__init__()

    def run(self):
        k = True
        i = 0
        m = 1
        while True:
            self.canvas.Clear()
            j = (math.sin(i/15) + 1) / 2 * 255
            for v in range(self.matrix.height):
                for u in range(self.matrix.width):
                    if v > 63 and u > 127:
                        continue
                    # if k:
                    x, y, z = canvas_to_3d(u, v)
                    # else:
                    #     x, y, z = canvas_to_3d(u, v)
                    # if i % 511 == 0:
                    #     k = not k
                    r = m*x+0.5
                    g = m*y+0.5
                    b = m*z+0.5
                    self.pixel(u, v, Color((r * 255 + j) % 255, (g * 255 + j) % 255, (b * 255 + j) % 255))
            i = i + 1
            if j < 0.1:
                m = (m + 1) % 5
            if m == 0:
                m = 1
            self.refresh()


if __name__ == "__main__":
    s = RGB3DStripes()
    try:
        s.setup()
        s.run()
    except KeyboardInterrupt:
        s.clear()
