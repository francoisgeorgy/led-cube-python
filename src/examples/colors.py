from ledcube.core.cube import Cube


class Colors(Cube):

    def run(self):
        self.canvas.Clear()
        r, g, b = 0, 0, 0
        while True:
            for r in range(0, 255, 8):
                self.canvas.Fill(r, g, b)
                self.refresh()


if __name__ == "__main__":
    s = Colors()
    print("CTRL-C to quit", end="", flush=True)
    try:
        s.setup()
        s.run()
    except KeyboardInterrupt:
        print("\r\033[Kbye")  # \r : go to beginning of line; \033[K : clear from cursor to the end of the line
        s.clear()
