from __future__ import print_function

import time
import math

from .Printer import Printer

#                    | --- | --- | --- |
#                    |     |     |     |
#                    | --- | --- | --- |
#                    |     |     |     |
#                    | --- | --- | --- |
#                    |     |     |     |
#                    | --- | --- | --- |
# | --- | --- | --- | | --- | --- | --- | | --- | --- | --- | | --- | --- | --- |
# |     |     |     | |     |     |     | |     |     |     | |     |     |     |
# | --- | --- | --- | | --- | --- | --- | | --- | --- | --- | | --- | --- | --- |
# |     |     |     | |     |     |     | |     |     |     | |     |     |     |
# | --- | --- | --- | | --- | --- | --- | | --- | --- | --- | | --- | --- | --- |
# |     |     |     | |     |     |     | |     |     |     | |     |     |     |
# | --- | --- | --- | | --- | --- | --- | | --- | --- | --- | | --- | --- | --- |
#                    | --- | --- | --- |
#                    |     |     |     |
#                    | --- | --- | --- |
#                    |     |     |     |
#                    | --- | --- | --- |
#                    |     |     |     |
#                    | --- | --- | --- |

class bcolors:
    BLUE = '\033[44m'
    GREEN = '\033[102m'
    YELLOW = '\033[103m'
    RED = '\033[101m'
    WHITE = '\033[107m'
    ORANGE = '\033[48;5;214m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class LEDPrinter(Printer):
    def __init__(self, cube, canvas):
        self.colours = True
        self.canvas = canvas
        super(LEDPrinter, self).__init__(cube)

    def pprint(self):
        for face in ['U', 'L', 'F', 'R', 'B', 'D']:
            self.print_face()

    def print_face(self, face):
        for i in range(self.cube.size):
            for j in range(self.cube.size):
                self.print_square(self.cube.faces[face].get_colour(int(i), int(j)))
            print()

    def print_square(self, c):
        if self.colours:
            if c == 'w':
                print(bcolors.WHITE, end = ' ')
            elif c == 'b':
                print(bcolors.BLUE, end = ' ')
            elif c == 'g':
                print(bcolors.GREEN, end = ' ')
            elif c == 'r':
                print(bcolors.RED, end = ' ')
            elif c == 'y':
                print(bcolors.YELLOW, end = ' ')
            elif c == 'o':
                print(bcolors.ORANGE, end = ' ')
            print(' ', bcolors.ENDC, end = ' ')
        else:
            print(c.upper(), end = ' ')

