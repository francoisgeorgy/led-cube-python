import time

from examples.rubik.rubik import Rubik

# automatic Rubik cube. Run by itself, doing scramble, solve, scramble, solve, etc... until the program is killed.


if __name__ == "__main__":

    cube = None
    try:
        cube = Rubik()
        cube.setup()
        cube.reset_cube()
        while True:
            cube.shuffle_cube()
            time.sleep(1)
            cube.auto_solve(cube)
            time.sleep(8)
    except KeyboardInterrupt:
        if cube:
            cube.clear()
        print("bye\n")

