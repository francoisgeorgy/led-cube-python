import importlib

from .enums import Face
import io


# https://raspberrypi.stackexchange.com/questions/5100/detect-that-a-python-program-is-running-on-the-pi
def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower():
                return True
    except Exception:
        pass
    return False


running_on_pi = is_raspberrypi()

# Dynamically import the appropriate module
if running_on_pi:
    rgb_matrix_lib = importlib.import_module('rgbmatrix')
    rgb_graphics = importlib.import_module('rgbmatrix.graphics')

    import board
    from ..imu import lis3dh_basic

    i2c = board.I2C()  # uses board.SCL and board.SDA
    imu = lis3dh_basic.LIS3DH_I2C(i2c, address=0x18)
    imu.range = lis3dh_basic.RANGE_2_G
    imu.use_offset = True

else:
    # rgb_matrix_lib = importlib.import_module('RGBMatrixEmulator')
    rgb_matrix_lib = importlib.import_module('ledcube.emulator')
    # rgb_graphics = importlib.import_module('RGBMatrixEmulator.graphics')
    rgb_graphics = importlib.import_module('ledcube.emulator.graphics')
    # from RGBMatrixEmulator import RGBMatrixOptions, RGBMatrix, graphics

    from ..imu.imu_emulator import ImuEmulator
    imu = ImuEmulator()

