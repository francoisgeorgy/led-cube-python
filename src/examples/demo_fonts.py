import os
import time
import random

from ledcube.core import rgb_graphics, Face
from ledcube.core.color import Color
from ledcube.core.cube import Cube
from ledcube.core.utils import reverse

fonts_text = (
    # '8pt_15_H.bdf',
    # 'Espy_Sans_Bold_14.bdf',
    # 'Espy_Sans_Bold_16.bdf',
    # 'Modern_12pt_10_H.bdf',
    # 'Modern_12pt_H.bdf',
    'Athens_18.bdf',
    'Classic_18pt_H.bdf',
    'Cory_24.bdf',
    'Courier_15.bdf',
    'Dwinelle_18.bdf',
    'Espy_Sans_16.bdf',
    'Geneva_24.bdf',
    'Helv (2).bdf',
    'MS_Sans_Serif_24.bdf',
    'Modern_12pt_H.bdf',
    'Modern_24pt_C.bdf',
    'New_York_18.bdf',
    'San_Francisco_18.bdf',
    'figlet-banner.bdf',
    'shaston-16.bdf',
    'spleen-32x64.bdf',
    'superpet-ascii.bdf',
    'swiss-36-ega.bdf',
    'swiss-36-vga.bdf'
)

fonts_symbols = (
    'Cairo_18.bdf',
    'Mobile_18.bdf'
)


class DemoFonts(Cube):

    def run(self):
        self.clear()

        fonts_path = f'{os.path.dirname(__file__)}/../../fonts'
        fonts = {}

        # word = 'Bienvenue chez PYXIS'
        # word = 'PYXIS'
        word = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        i = 0
        k = 0
        while True:
            self.clear()
            self.canvas.Fill(0, 0, 0)
            for face in Face:
                filename = fonts_text[k]
                if filename not in fonts:
                    fonts[filename] = rgb_graphics.Font()
                    fonts[filename].LoadFont(f'{fonts_path}/{filename}')
                c = word[(i+k) % len(word)]
                x = (64 - fonts[filename].CharacterWidth(ord(c))) // 2
                y = (64 - fonts[filename].height) // 2 + fonts[filename].baseline
                self.planes[face.value].text(x, reverse(y), Color.WHITE(), c, fonts[filename])
                k = (k + 1) % len(fonts_text)
            self.refresh()
            i = (i+1) % len(word)
            # time.sleep(0.1)


if __name__ == "__main__":
    s = DemoFonts()
    print("CTRL-C to quit", end="", flush=True)
    try:
        s.setup()
        s.run()
    except KeyboardInterrupt:
        s.clear()
