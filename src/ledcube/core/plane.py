from ledcube.core.enums import Coord3D, Coord2D, FACES_LABELS, face_offsets, FACES_NAMES
from ledcube.core.utils import cross_product, u, v, get_non_zero_axis_label


# TODO: what is resolution?


class Plane:
    def __init__(self, parent, face, offset=None, x_axis=Coord3D(0, 0, 0), y_axis=Coord3D(0, 0, 0), z_axis=None, resolution=1):
        self.parent = parent
        self.face = face
        # self.label = label if label else FACES_LABELS["default"][face]
        self.offset = offset if offset else face_offsets[face]
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.z_axis = Coord3D(*cross_product(x_axis, y_axis) if z_axis is None else z_axis)
        self.ax = 0
        self.ay = 0
        self.az = 0
        self.resolution = resolution
        # print(f'plane {self.label}: x={strvec(self.x_axis)} y={strvec(self.y_axis)} z={strvec(self.z_axis)}')

    def get_label(self, lang='default'):
        return FACES_LABELS[lang][self.face]

    def get_name(self, lang='default'):
        return FACES_NAMES[lang][self.face]

    def update_acceleration(self, gx, gy, gz):
        self.ax = gx * self.x_axis.x + gy * self.y_axis.x + gz * self.z_axis.x
        self.ay = gx * self.x_axis.y + gy * self.y_axis.y + gz * self.z_axis.y
        self.az = gx * self.x_axis.z + gy * self.y_axis.z + gz * self.z_axis.z

    def pixel(self, x, y, color):
        self.parent.pixel(self.offset.x + u(x), self.offset.y + v(y), color)

    def line(self, x0, y0, x1, y1, color, inverse_y=True):
        if inverse_y:
            self.parent.line(self.offset.x + u(x0), self.offset.y + v(y0), self.offset.x + u(x1), self.offset.y + v(y1), color)
        else:
            self.parent.line(self.offset.x + u(x0), self.offset.y + y0, self.offset.x + u(x1), self.offset.y + y1, color)

    def circle(self, x, y, r, color):
        self.parent.circle(self.offset.x + u(x), self.offset.y + v(y), r, color)

    def text(self, x, y, color, t, f=None):
        self.parent.text(self.offset.x + u(x), self.offset.y + v(y), color, t, f)

    def draw_x_axis(self, color, axis_len=28, with_label=True, font=None, value=None, label=None):
        self.line(9, 6, 9+axis_len, 6, color)
        if with_label:
            self.text(8+axis_len+3, 2, color, f"{label if label else get_non_zero_axis_label(self.x_axis)}", font)
            if value:
                self.text(8+axis_len+3, 10, color, f"{value}", font)

    def draw_y_axis(self, color, axis_len=28, with_label=True, font=None, value=None, label=None):
        self.line(6, 9, 6, 9+axis_len, color)
        if with_label:
            self.text(3, axis_len+11, color, f"{label if label else get_non_zero_axis_label(self.y_axis)}", font)
            if value:
                self.text(3, 8+axis_len+10, color, f"{value}", font)

    def draw_z_axis(self, color, axis_len=28, with_label=True, font=None, value=None, label=None):
        self.circle(6, 6, 3, color)
        self.pixel(6, 6, color)
        if with_label:
            self.text(9, 9, color, f"{label if label else get_non_zero_axis_label(self.z_axis)}", font)
            if value:
                self.text(9, 17, color, f"{value}", font)

    def border(self, color):
        self.line(0, 0, 63, 0, color)
        self.line(63, 0, 63, 63, color)
        self.line(0, 63, 63, 63, color)
        self.line(0, 0, 0, 63, color)

    def fill(self, color):
        for y in range(self.offset.y, self.offset.y + 64):
            for x in range(self.offset.x, self.offset.x + 64):
                self.parent.pixel(x, y, color)

    def fill_circle(self, x0, y0, r, color):
        """
        https://github.com/adafruit/Adafruit-GFX-Library/blob/master/Adafruit_GFX.cpp#L471
        https://adafruit.github.io/Adafruit-GFX-Library/html/class_adafruit___g_f_x.html
        :param face:
        :param x0:
        :param y0:
        :param r:
        :param corners:
        :param delta:
        :param color:
        :return:
        """

        if r <= 0:
            return

        if r == 1:
            self.pixel(x0, y0, color)
            return

        f = 1 - r
        dd_f_x = 1
        dd_f_y = -2 * r
        x = 0
        y = r
        px = x
        py = y

        while x < y:

            if f >= 0:
                y -= 1
                dd_f_y += 2
                f += dd_f_y

            x += 1
            dd_f_x += 2
            f += dd_f_x

            self.line(x0, y0 - y, x0, y0 - y + 2 * y, color)

            if x <= (y + 1):
                self.line(x0 + x, y0 - y, x0 + x, y0 - y + 2 * y, color)
                self.line(x0 - x, y0 - y, x0 - x, y0 - y + 2 * y, color)

            if y != py:
                self.line(x0 + py, y0 - px, x0 + py, y0 - px + 2 * px, color)
                self.line(x0 - py, y0 - px, x0 - py, y0 - px + 2 * px, color)
                py = y

            px = x
