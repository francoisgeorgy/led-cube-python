# adapted from from RGBMatrixEmulator.graphics.color.py
from ledcube.core import rgb_graphics


class Color(rgb_graphics.Color):
    def __init__(self, r=0, g=0, b=0):
        self.red = r
        self.green = g
        self.blue = b

    def adjust_brightness(self, alpha, to_int=False):
        self.red *= alpha
        self.green *= alpha
        self.blue *= alpha
        if to_int:
            self.red = int(self.red)
            self.green = int(self.green)
            self.blue = int(self.blue)

    def gamma(self, gamma=0.43):
        r, g, b = (self.red/255.0)**(1/gamma), (self.green/255.0)**(1/gamma), (self.blue/255.0)**(1/gamma)
        t = r + g + b
        if t < 0.000001:
            self.red, self.green, self.blue = 0, 0, 0
        else:
            r = r / t
            g = g / t
            b = b / t
            self.red, self.green, self.blue = 255*(r**gamma), 255*(g**gamma), 255*(b**gamma)

    def to_tuple(self):
        return int(self.red), int(self.green), int(self.blue)

    def to_hex(self):
        return "#%02x%02x%02x" % self.to_tuple()

    @classmethod
    def BLACK(cls):
        return Color(0, 0, 0)

    @classmethod
    def RED(cls):
        return Color(255, 0, 0)

    @classmethod
    def ORANGE(cls):
        return Color(255, 165, 0)

    @classmethod
    def YELLOW(cls):
        return Color(255, 255, 0)

    @classmethod
    def GREEN(cls):
        return Color(0, 255, 0)

    @classmethod
    def BLUE(cls):
        return Color(0, 0, 255)

    @classmethod
    def WHITE(cls):
        return Color(255, 255, 255)

    @classmethod
    def GREY(cls):
        return Color(177, 177, 190)
