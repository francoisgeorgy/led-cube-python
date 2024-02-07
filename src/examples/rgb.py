import time

from ledcube.core.cube import Cube


class RGB(Cube):
    
    def __init__(self):
        super().__init__()

    def run(self):

        self.canvas.Clear()

        for u in range(64):
            for v in range(64):
                self.canvas.SetPixel(u, v, u*4, v*4, 100)

        self.refresh()

        while True:
            time.sleep(1)


if __name__ == "__main__":
    s = RGB()
    print("CTRL-C to quit", end="", flush=True)
    try:
        s.setup()
        s.run()
    except KeyboardInterrupt:
        print("\r\033[Kbye")  # \r : go to beginning of line; \033[K : clear from cursor to the end of the line
        s.clear()
