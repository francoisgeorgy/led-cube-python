import importlib
import math
import os
import sys
import time

from ledcube.core.color import Color
from ledcube.core.cube import Cube
from ledcube.core.mapper_matrix_to_cube import canvas_to_3d


class Shader(Cube):

    def __init__(self):
        super().__init__()

        # Add additional command line options :
        self.parser.add_argument("shader", help="The shader script", type=str)

    def run(self):

        if not self.args.shader:
            print("ERROR: shader script missing")
            sys.exit(0)

        # mod = load_module_from_path(self.args.shader)

        # shader_script = os.path.splitext(self.args.shader)[0]   # remove extension if any
        # mod = __import__(shader_script, fromlist=["shader"])

        t = 0
        while True:
            self.canvas.Clear()

            # Optimization problem : the angle has to be computed for each coord
            # TODO: pre-compute all angles

            # angle = math.atan2(z, x)

            for v in range(64):
                for u in range(4 * 64):
                    # print(u, v)
                    r, g, b = mod.shader(*canvas_to_3d(u, v), t)
                    # r, g, b = shader_rgb_t(*canvas_to_3d(u, v), t)
                    self.pixel(u, v, Color(r * 255, g * 255, b * 255))
            for v in range(64, 128):
                for u in range(128):
                    # r, g, b = shader_rgb_t(*canvas_to_3d(u, v), t)
                    r, g, b = mod.shader(*canvas_to_3d(u, v), t)
                    self.pixel(u, v, Color(r * 255, g * 255, b * 255))
            # for v in range(self.matrix.height):
            #     for u in range(self.matrix.width):
            #         r, g, b = shader_rgb(*canvas_to_3d(u, v))
            #         self.pixel(u, v, Color(r * 255, g * 255, b * 255))
            #         return
            # self.pixel(u, v, Color(((r * 255) + i) % 256, ((g * 255) + i) % 256, ((b * 255) + i) % 256))
            # print(i, ((r * 255) + i) % 256)
            # i = (i+1) % 256
            t = t + 1
            self.refresh()


if __name__ == "__main__":
    s = Shader()
    try:
        s.setup()
        s.run()
    except KeyboardInterrupt:
        print("bye\n")
        s.clear()
