
from ledcube.core.color import Color
from ledcube.core.utils import clamp


class Dot:
    def __init__(self, p=None, x=0, y=0, z=0, radius=4, color=Color.BLUE(), max_speed=1):
        self.plane = p
        self.x = x
        self.y = y
        self.z = z
        self.vx = 0
        self.vy = 0
        self.vz = 0
        self.radius = radius
        self.color = color
        self.max_speed = max_speed

    # ? if accel is 0 and v not 0, does the particule continue to move or do we
    # want to slow it done?
    def accelerate(self, ax, ay, az):
        f = 2
        # limit the speed:
        self.vx = clamp(self.vx + ax / f, -self.max_speed, self.max_speed)
        self.vy = clamp(self.vy + ay / f, -self.max_speed, self.max_speed)
        self.vz = clamp(self.vz + az / f, -self.max_speed, self.max_speed)
        # self.vx = ax    # no integration of the acceleration, for debug
        # self.vy = ay
        # self.vz = az
        self.x = clamp(self.x + self.vx, self.radius, 63-self.radius)
        self.y = clamp(self.y + self.vy, self.radius, 63-self.radius)
        self.z = clamp(self.z + self.vz, self.radius, 63-self.radius)
        # If the dot come to a wall, its speed must be canceled
        if self.x == self.radius or self.x == 63-self.radius:
            self.vx = 0
        if self.y == self.radius or self.z == 63-self.radius:
            self.vy = 0
        if self.z == self.radius or self.z == 63-self.radius:
            self.vz = 0

    def position(self):
        return self.x, self.y, self.z

    def getcolor(self):
        return self.color

    def draw(self):
        self.plane.circle(self.x, self.y, self.radius, self.color)
