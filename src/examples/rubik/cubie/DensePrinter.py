from __future__ import print_function
from .Printer import Printer


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


# class DensePrinter(object):
#     def __init__(self, cube):
#         self._cube = cube
#
#     @property
#     def cube(self):
#         '''
#         Initial implementation worked with NaiveCube, this hack the whole class accesses to self.cube
#         to work the same way as before
#         '''
#         return self._cube.to_naive_cube()
#
#     def pprint(self):
#         pass


class DensePrinter(Printer):
    def __init__(self, cube, colours=False):
        self.colours = colours
        super(DensePrinter, self).__init__(cube)

    def pprint(self, cube=None):
        if cube:
            self._cube = cube
        self.print_upper()
        self.print_center()
        self.print_down()

    def print_upper(self):
        for i in range(self.cube.size):
            print('  ' * self.cube.size, end='')
            for j in range(self.cube.size):
                self.print_square(self.cube.faces['U'].get_colour(int(i), int(j)))
            print()

    def print_center(self):
        for i in range(self.cube.size):
            for face in ['L', 'F', 'R', 'B']:
                for j in range(self.cube.size):
                    self.print_square(self.cube.faces[face].get_colour(int(i), int(j)))
            print()

    def print_down(self):
        for i in range(self.cube.size):
            print('  ' * self.cube.size, end='')
            for j in range(self.cube.size):
                self.print_square(self.cube.faces['D'].get_colour(int(i), int(j)))
            print()

    def print_square(self, c):
        if self.colours:
            if c == 'w':
                print(bcolors.WHITE, end='')
            elif c == 'b':
                print(bcolors.BLUE, end='')
            elif c == 'g':
                print(bcolors.GREEN, end='')
            elif c == 'r':
                print(bcolors.RED, end='')
            elif c == 'y':
                print(bcolors.YELLOW, end='')
            elif c == 'o':
                print(bcolors.ORANGE, end='')
            print(' ', bcolors.ENDC, end='')    # second half of the square
        else:
            print(c.upper(), end='')

