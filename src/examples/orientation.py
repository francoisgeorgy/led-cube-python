import time

from ledcube.core import Face
from ledcube.core.color import Color
from ledcube.core.cube import Cube

"""
On peut mettre le cube dans n'importe position, il va essayer de se ré-orienter et de toujours afficher "Hello" sur la
face dirigée vers le haut.
"""


class Orientation(Cube):

    def __init__(self):
        super().__init__()

    def run(self):

        while True:
            try:
                gx, gy, gz = self.imu.acceleration
                ax, ay, az = abs(gx), abs(gy), abs(gz)

                if ax > ay and ax > az:
                    face_up = Face.RIGHT if gx >= 0 else Face.LEFT
                elif ay > ax and ay > az:
                    face_up = Face.BACK if gy >= 0 else Face.FRONT
                else:
                    face_up = Face.TOP if gz >= 0 else Face.BOTTOM

                self.clear()
                p = self.planes[face_up.value]
                p.fill(Color.RED())
                self.refresh()

            except OSError:
                continue

            time.sleep(0.1)


if __name__ == "__main__":
    s = Orientation()
    try:
        s.setup()
        s.run()
    except KeyboardInterrupt:
        s.clear()
