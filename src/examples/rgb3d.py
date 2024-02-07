from ledcube.core.color import Color
from ledcube.core.cube import Cube
from ledcube.core.mapper_matrix_to_cube import canvas_to_3d

# https://stackoverflow.com/questions/46695726/generating-pure-colors-of-equal-brightness-for-display-on-leds
equal_brightness = True


class RGB3D(Cube):
    
    def __init__(self):
        super().__init__()

    def run(self):

        while True:
            self.canvas.Clear()
            for v in range(self.matrix.height):
                for u in range(self.matrix.width):
                    x, y, z = canvas_to_3d(u, v)
                    r = x+0.5
                    g = y+0.5
                    b = z+0.5
                    if equal_brightness:
                        gamma = .43
                        r, g, b = r**(1/gamma), g**(1/gamma), b**(1/gamma)
                        t = r + g + b
                        if t < 0.0000001:
                            r, g, b = 0, 0, 0
                        else:
                            r = r / t
                            g = g / t
                            b = b / t
                            r, g, b = r**gamma, g**gamma, b**gamma
                    self.pixel(u, v, Color(r * 255, g * 255, b * 255))
            self.refresh()


if __name__ == "__main__":
    s = RGB3D()
    print("CTRL-C to quit", end="", flush=True)
    try:
        s.setup()
        s.run()
    except KeyboardInterrupt:
        print("\r\033[Kbye")  # \r : go to beginning of line; \033[K : clear from cursor to the end of the line
        s.clear()
