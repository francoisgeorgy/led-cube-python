from __future__ import print_function
import argparse
import time

# from .Solver import Solver
# from .Solver import Beginner
# from .Solver import CFOP
from .NaiveCube import NaiveCube
from .Cubie import Cube
from .Printer import TtyPrinter

__author__ = 'Victor Cabezas'

# from cubie.Cubie import Cube
# from cubie.NaiveCube import NaiveCube
# from cubie.Printer import TtyPrinter
# from cubie.Solver import Beginner, CFOP, Solver

# METHODS = {
#     'Beginner': Beginner.BeginnerSolver,
#     'CFOP': CFOP.CFOPSolver
# }

def check_valid_cube(cube):
    '''Checks if cube is one of str, NaiveCube or Cubie.Cube and returns
    an instance of Cubie.Cube'''

    if isinstance(cube, str):
        c = NaiveCube()
        c.set_cube(cube)
        cube = c

    if isinstance(cube, NaiveCube):
        c = Cube()
        c.from_naive_cube(cube)
        cube = c

    if not isinstance(cube, Cube):
        raise ValueError('Cube is not one of (str, NaiveCube or Cubie.Cube)')

    return cube

# def solve(cube, method = Beginner.BeginnerSolver, *args, **kwargs):
#     if isinstance(method, str):
#         if not method in METHODS:
#             raise ValueError('Invalid method name, must be one of (%s)' %
#                 ', '.join(METHODS.keys())
#             )
#         method = METHODS[method]
#
#     if not issubclass(method, Solver):
#         raise ValueError('Method %s is not a valid Solver subclass' %
#             method.__class__.__name__
#         )
#
#     cube = check_valid_cube(cube)
#
#     solver = method(cube)
#
#     return solver.solution(*args, **kwargs)


def pprint(cube, color = True):
    cube = check_valid_cube(cube)
    printer = TtyPrinter(cube, color)
    printer.pprint()


def string_representation(cube):
    c = cube.to_naive_cube()
    s = ''
    for face in ['U', 'L', 'F', 'R', 'B', 'D']:
        for i in range(c.size):
            for j in range(c.size):
                s += c.faces[face].get_colour(int(i), int(j))
    return s


def describe_movement(m):
    descriptions = {
        "U": "Rotate the upper face 90 degrees clockwise",
        "U'": "Rotate the upper face 90 degrees counterclockwise",
        "U2": "Rotate the upper face 180 degrees",
        "D": "Rotate the down face 90 degrees clockwise",
        "D'": "Rotate the down face 90 degrees counterclockwise",
        "D2": "Rotate the down face 180 degrees",
        "L": "Rotate the left face 90 degrees clockwise",
        "L'": "Rotate the left face 90 degrees counterclockwise",
        "L2": "Rotate the left face 180 degrees",
        "R": "Rotate the right face 90 degrees clockwise",
        "R'": "Rotate the right face 90 degrees counterclockwise",
        "R2": "Rotate the right face 180 degrees",
        "F": "Rotate the front face 90 degrees clockwise",
        "F'": "Rotate the front face 90 degrees counterclockwise",
        "F2": "Rotate the front face 180 degrees",
        "B": "Rotate the back face 90 degrees clockwise",
        "B'": "Rotate the back face 90 degrees counterclockwise",
        "B2": "Rotate the back face 180 degrees",
        "M": "Rotate the middle layer parallel to the left face 90 degrees clockwise",
        "M'": "Rotate the middle layer parallel to the left face 90 degrees counterclockwise",
        "M2": "Rotate the middle layer parallel to the left face 180 degrees",
        "E": "Rotate the equatorial layer 90 degrees clockwise",
        "E'": "Rotate the equatorial layer 90 degrees counterclockwise",
        "E2": "Rotate the equatorial layer 180 degrees",
        "S": "Rotate the standing layer parallel to the front face 90 degrees clockwise",
        "S'": "Rotate the standing layer parallel to the front face 90 degrees counterclockwise",
        "S2": "Rotate the standing layer parallel to the front face 180 degrees",
        "X": "Rotate the entire cube on the R axis 90 degrees clockwise",
        "X'": "Rotate the entire cube on the R axis 90 degrees counterclockwise",
        "X2": "Rotate the entire cube on the R axis 180 degrees",
        "Y": "Rotate the entire cube on the U axis 90 degrees clockwise",
        "Y'": "Rotate the entire cube on the U axis 90 degrees counterclockwise",
        "Y2": "Rotate the entire cube on the U axis 180 degrees",
        "Z": "Rotate the entire cube on the F axis 90 degrees clockwise",
        "Z'": "Rotate the entire cube on the F axis 90 degrees counterclockwise",
        "Z2": "Rotate the entire cube on the F axis 180 degrees"
    }
    return descriptions.get(m, "Invalid move")


# Example usage
# move_code = "U"
# print(describe_movement(move_code))



# def main(argv = None):
#     arg_parser = argparse.ArgumentParser(description = 'cubie command line tool')
#     arg_parser.add_argument('-i', '--cube', dest = 'cube', required = True, help = 'Cube definition string')
#     arg_parser.add_argument('-c', '--color', dest = 'color', default = True, action = 'store_false', help = 'Disable use of colors with TtyPrinter')
#     arg_parser.add_argument('-s', '--solver', dest = 'solver', default = 'Beginner', choices = METHODS.keys(), help = 'Solver method to use')
#     args = arg_parser.parse_args(argv)
#
#     cube = args.cube.lower()
#     print ("Read cube", cube)
#     pprint(cube, args.color)
#
#     start = time.time()
#     print ("Solution", ', '.join(map(str, solve(cube, METHODS[args.solver]))))
#     print ("Solved in", time.time() - start, "seconds")
