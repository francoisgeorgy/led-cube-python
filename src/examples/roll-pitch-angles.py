import time
# import board
# from ledcube.imu import lis3dh_basic
from ledcube.core import Face
from ledcube.core.color import Color
from ledcube.core.cube import Cube
from ledcube.core.utils import normalize, rot_y, r2d, rot_x

# display roll and pitch angles

SHOW_AXES = True
SHOW_VECTOR = True
SHOW_ACCEL = True
SHOW_DOT = False
SHOW_DOT_SPEED = False

GRAVITY = 1
MAX_SPEED = 1   # absolute value
FILTER_ACC = False
INVERSE_X = False
ACC_VECTOR_FULL = True
ACCEL_ORIENTATION = [0, 1, 0]

# Must be initialized BEFORE the cube (rpi lib)
# i2c = board.I2C()  # uses board.SCL and board.SDA
# imu = lis3dh_basic.LIS3DH_I2C(i2c, address=0x18)
# imu.range = lis3dh_basic.RANGE_2_G
# imu.use_offset = False


class RollPitchAngles(Cube):

    def __init__(self):
        super().__init__()

    def run(self):

        while True:
            self.clear()

            x = 0
            y = 0
            z = 0
            try:
                gx, gy, gz = self.imu.acceleration
                if FILTER_ACC:
                    gx = round(gx*10) / 10
                    gy = round(gy*10) / 10
                    gz = round(gz*10) / 10
                x = gx
                y = gy
                z = gz
            except OSError:
                continue

            vn = normalize([x, y, z])

            pitch = rot_y(vn)
            roll = rot_x(vn)

            color = Color.GREEN()
            p = self.planes[Face.FRONT.value]
            p.text(2, 50, color, f'R {r2d(roll):>6.2f}')
            p.text(2, 40, color, f'P {r2d(pitch):>6.2f}')
            p.text(2, 2, color, f'X {x:>6.2f}')
            p.text(2, 12, color, f'Y {y:>6.2f}')
            p.text(2, 22, color, f'Z {z:>6.2f}')

            self.refresh()
            time.sleep(0.1)


if __name__ == "__main__":
    s = RollPitchAngles()
    s.setup()
    s.run()
