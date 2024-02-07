import io

from PIL import Image, ImageDraw

from ledcube.emulator import Color
from ledcube.emulator.adapters.base import BaseAdapter
from ledcube.emulator.adapters.browser_adapter.server import Server
from ledcube.emulator.adapters.browser_adapter.web_socket import ImageWebSocket
from ledcube.emulator.adapters.mapper import pixel_mapper
from ledcube.emulator.logger import Logger


class CubeBrowserAdapter(BaseAdapter):

    SUPPORTS_ALTERNATE_PIXEL_STYLE = True

    def __init__(self, width, height, options):
        super().__init__(width, height, options)
        # super().__init__(4*64, 3*64, options)
        self.__server = None
        self.image = None

    def load_emulator_window(self):
        if self.loaded:
            return

        Logger.info(self.emulator_details_text())
        websocket = ImageWebSocket
        websocket.register_adapter(self)

        self.__server = Server(websocket, self.options)
        self.__server.run()

        self.loaded = True

    def draw_to_screen(self, pixels):
        image = Image.new("RGB", self.options.window_size())
        drawer = ImageDraw.Draw(image)
        pixel_size = self.options.pixel_size
        for row, pixel_row in enumerate(pixels):
            for col, pixel in enumerate(pixel_row):
                x, y = pixel_mapper(col, row)
                self.__draw_pixel(drawer, x * pixel_size, y * pixel_size, pixel)

        with io.BytesIO() as bytesIO:
            image.save(
                bytesIO, "JPEG", quality=self.options.browser.quality, optimize=True
            )
            self.image = bytesIO.getvalue()

    def __draw_pixel(self, image: ImageDraw, x, y, pixel):
        self.adjust_pixel_brightness(pixel)
        pixel_size = self.options.pixel_size
        if self.options.pixel_style == "circle":
            image.ellipse(
                (x, y, x + pixel_size - 1, y + pixel_size - 1),
                fill=pixel.to_tuple(),
                outline=pixel.to_tuple(),
            )
        else:
            image.rectangle(
                (x, y, x + pixel_size, y + pixel_size),
                fill=pixel.to_tuple(),
                outline=pixel.to_tuple(),
            )
