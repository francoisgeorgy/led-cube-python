from ledcube.imu.utils import AccelerationTuple


class ImuEmulator:

    def __init__(self):
        pass

    def get_accel(self):
        gx, gy, gz = 0.1, 0.2, 0.3
        return gx, gy, gz

    @property
    def acceleration(self) -> AccelerationTuple:
        gx, gy, gz = 0.1, 0.2, 0.3
        return gx, gy, gz

    def shake(self) -> bool:
        return False
