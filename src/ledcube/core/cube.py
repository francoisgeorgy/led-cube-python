import argparse

from ledcube.core import Face, running_on_pi, rgb_matrix_lib, rgb_graphics, imu
from ledcube.core.enums import Coord3D
from ledcube.core.plane import Plane
from ledcube.core.utils import load_font

#
# Default values for the cube:
#
CUBE_PANEL_SIZE = 64    # panels are 64x64 pixels
CUBE_LED_CHAINS = 3     # we have 3 panels per chain
CUBE_LED_PARALLEL = 2   # and we have 2 chains in parallel
CUBE_DEFAULT_BRIGHTNESS = 70
CUBE_SLOWDOWN_GPIO = 5  # this value works best with RPi 4
CUBE_PIXEL_MAPPER = "Cube"  # The pixel mapping; see rpi_rgb_led_matrix/lib/pixel-mapper.cc

# the emulator uses a custom pixel mapper to display the cube in a "unfolded" configuration.
EMULATOR_LED_CHAINS = 4
EMULATOR_LED_PARALLEL = 3
EMULATOR_DEFAULT_BRIGHTNESS = 100   # with the emulator, a value less than 100 will lead to fading pixels


class Cube(object):

    def __init__(self, *args, **kwargs):

        self.planes = None
        self.canvas = None
        self.matrix = None
        self.parser = argparse.ArgumentParser()

        # arguments common to RPi and emulator :
        self.parser.add_argument("-r", "--led-rows", action="store", help=f"Display rows. 16 for 16x32, 32 for 32x32. Default: {CUBE_PANEL_SIZE}", default=CUBE_PANEL_SIZE, type=int)
        self.parser.add_argument("-l", "--led-cols", action="store", help=f"Panel columns. Typically 32 or 64. (Default: {CUBE_PANEL_SIZE})", default=CUBE_PANEL_SIZE, type=int)
        self.parser.add_argument("--led-show-refresh", action="store_true", help="Shows the current refresh rate of the LED panel")

        if running_on_pi:
            self.parser.add_argument("-c", "--led-chain", action="store",
                                     help=f"Daisy-chained boards. Default: {CUBE_LED_CHAINS}.", default=CUBE_LED_CHAINS,
                                     type=int)
            self.parser.add_argument("-P", "--led-parallel", action="store",
                                     help=f"For Plus-models or RPi2: parallel chains. 1..3. Default: {CUBE_LED_PARALLEL}",
                                     default=CUBE_LED_PARALLEL, type=int)
            self.parser.add_argument("-b", "--led-brightness", action="store",
                                     help=f"Sets brightness level. Default: {CUBE_DEFAULT_BRIGHTNESS}. Range: 1..100",
                                     default=CUBE_DEFAULT_BRIGHTNESS, type=int)
            self.parser.add_argument("-p", "--led-pwm-bits", action="store", help="Bits used for PWM. Something between 1..11. Default: 11", default=11, type=int)
            self.parser.add_argument("-m", "--led-gpio-mapping", help="Hardware Mapping: regular, adafruit-hat, adafruit-hat-pwm" , choices=['regular', 'regular-pi1', 'adafruit-hat', 'adafruit-hat-pwm'], type=str)
            self.parser.add_argument("--led-scan-mode", action="store", help="Progressive or interlaced scan. 0 Progressive, 1 Interlaced (default)", default=1, choices=range(2), type=int)
            self.parser.add_argument("--led-pwm-lsb-nanoseconds", action="store", help="Base time-unit for the on-time in the lowest significant bit in nanoseconds. Default: 130", default=130, type=int)
            self.parser.add_argument("--led-slowdown-gpio", action="store", help=f"Slow down writing to GPIO. Range: 0..5. Default: {CUBE_SLOWDOWN_GPIO}", default=CUBE_SLOWDOWN_GPIO, type=int)
            self.parser.add_argument("--led-no-hardware-pulse", action="store", help="Don't use hardware pin-pulse generation")
            self.parser.add_argument("--led-rgb-sequence", action="store", help="Switch if your matrix has led colors swapped. Default: RGB", default="RGB", type=str)
            self.parser.add_argument("--led-pixel-mapper", action="store", help=f"Apply pixel mappers. Default: \"{CUBE_PIXEL_MAPPER}\"", default=CUBE_PIXEL_MAPPER, type=str)
            self.parser.add_argument("--led-row-addr-type", action="store", help="0 = default; 1=AB-addressed panels; 2=row direct; 3=ABC-addressed panels; 4 = ABC Shift + DE direct", default=0, type=int, choices=[0,1,2,3,4])
            self.parser.add_argument("--led-multiplexing", action="store", help="Multiplexing type: 0=direct; 1=strip; 2=checker; 3=spiral; 4=ZStripe; 5=ZnMirrorZStripe; 6=coreman; 7=Kaler2Scan; 8=ZStripeUneven... (Default: 0)", default=0, type=int)
            self.parser.add_argument("--led-panel-type", action="store", help="Needed to initialize special panels. Supported: 'FM6126A'", default="", type=str)
            self.parser.add_argument("--led-no-drop-privs", dest="drop_privileges", help="Don't drop privileges from 'root' after initializing the hardware.", action='store_false')
            self.parser.set_defaults(drop_privileges=True)
        else:
            self.parser.add_argument("-c", "--led-chain", action="store",
                                     help=f"Daisy-chained boards. Default: {EMULATOR_LED_CHAINS}.",
                                     default=EMULATOR_LED_CHAINS, type=int)
            self.parser.add_argument("-P", "--led-parallel", action="store",
                                     help=f"For Plus-models or RPi2: parallel chains. 1..3. Default: {EMULATOR_LED_PARALLEL}",
                                     default=EMULATOR_LED_PARALLEL, type=int)
            self.parser.add_argument("-b", "--led-brightness", action="store",
                                     help=f"Sets brightness level. Default: {EMULATOR_DEFAULT_BRIGHTNESS}. Range: 1..100",
                                     default=EMULATOR_DEFAULT_BRIGHTNESS, type=int)

        self.args = None
        self.resolution = 1
        self.font = load_font("6x10.bdf")
        self.imu = imu

    def setup(self):

        # TODO: return false if an argument is invalid or a mandatory argument is missing.

        self.args = self.parser.parse_args()

        options = rgb_matrix_lib.RGBMatrixOptions()

        options.rows = self.args.led_rows
        options.cols = self.args.led_cols
        options.chain_length = self.args.led_chain
        options.parallel = self.args.led_parallel
        options.brightness = self.args.led_brightness
        options.show_refresh_rate = 1 if self.args.led_show_refresh else 0

        if running_on_pi:
            # options.hardware_mapping = self.args.led_gpio_mapping
            options.row_address_type = self.args.led_row_addr_type
            options.multiplexing = self.args.led_multiplexing
            options.pwm_bits = self.args.led_pwm_bits
            options.pwm_lsb_nanoseconds = self.args.led_pwm_lsb_nanoseconds
            options.led_rgb_sequence = "RGB"
            options.pixel_mapper_config = self.args.led_pixel_mapper
            if self.args.led_slowdown_gpio is not None:
                options.gpio_slowdown = self.args.led_slowdown_gpio
            if self.args.led_no_hardware_pulse:
                options.disable_hardware_pulsing = True
            if not self.args.drop_privileges:
                options.drop_privileges=False
        else:
            # options.pixel_mapper_config = ""
            options.panel_type = ""
            options.show_refresh_rate = 1

        self.matrix = rgb_matrix_lib.RGBMatrix(options=options)
        self.canvas = self.matrix.CreateFrameCanvas()

        self.planes = [
            # FRONT
            # (1) : the X-axis(IMU) is represented by the X-axis(front panel)
            # (2) : the Y-axis(IMU) is represented by the negative Z-axis(front panel)
            Plane(self, Face.FRONT, x_axis=Coord3D(1, 0, 0), y_axis=Coord3D(0, 0, -1)),
            # RIGHT
            # (1) : the X-axis(IMU) is represented by the Z-axis(front panel)
            # (2) : the Y-axis(IMU) is represented by the X-axis(front panel)
            Plane(self, Face.RIGHT, x_axis=Coord3D(0, 0, 1), y_axis=Coord3D(1, 0, 0)),
            # BACK
            # (1) : the X-axis(IMU) is represented by the negative X-axis(front panel)
            # (2) : the Y-axis(IMU) is represented by the Y-axis(front panel)
            Plane(self, Face.BACK, x_axis=Coord3D(-1, 0, 0), y_axis=Coord3D(0, 1, 0)),
            # LEFT
            # (1) : the X-axis(IMU) is represented by the negative Z-axis(front panel)
            # (2) : the Y-axis(IMU) is represented by the negative X-axis(front panel)
            Plane(self, Face.LEFT, x_axis=Coord3D(0, 0, -1), y_axis=Coord3D(-1, 0, 0)),
            # TOP
            # (1) : the X-axis(IMU) is represented by the X-axis(front panel)
            # (2) : the Y-axis(IMU) is represented by the Y-axis(front panel)
            Plane(self, Face.TOP, x_axis=Coord3D(1, 0, 0), y_axis=Coord3D(0, 1, 0)),
            # BOTTOM
            # (1) : the X-axis(IMU) is represented by the X-axis(front panel)
            # (2) : the Y-axis(IMU) is represented by the negative Y-axis(front panel)
            Plane(self, Face.BOTTOM, x_axis=Coord3D(1, 0, 0), y_axis=Coord3D(0, -1, 0))
        ]

        return True

    def clear(self):
        self.canvas.Clear()

    def refresh(self):
        self.canvas = self.matrix.SwapOnVSync(self.canvas)

    def pixel(self, x, y, color):
        self.canvas.SetPixel(x, y, color.red, color.green, color.blue)

    def line(self, x0, y0, x1, y1, color):
        rgb_graphics.DrawLine(self.canvas, x0, y0, x1, y1, color)

    def circle(self, x0, y0, r, color):
        rgb_graphics.DrawCircle(self.canvas, x0, y0, r, color)

    def dot(self, p, part):
        x, y, z = part.position()
        self.circle(x // self.resolution, y // self.resolution, 4, part.getcolor())

    def text(self, x, y, color, text, font=None):
        rgb_graphics.DrawText(self.canvas, font if font else self.font, x, y, color, text)
