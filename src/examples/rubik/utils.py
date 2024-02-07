from enum import Enum

from ledcube.core import Face
from ledcube.core.color import Color

rubik_faces = ('U', 'L', 'F', 'R', 'B', 'D')
rubik_slices = ('M', 'E', 'S')
rubik_axes = ('X', 'Y', 'Z')

slices = {
    # Middle layer turn - between R and L - in the same direction as an L turn
    'M': [
        # (face, row, col)
        ('U', 0, 1), ('U', 1, 1), ('U', 2, 1),
        ('F', 0, 1), ('F', 1, 1), ('F', 2, 1),
        ('B', 0, 1), ('B', 1, 1), ('B', 2, 1),
        ('D', 0, 1), ('D', 1, 1), ('D', 2, 1)
    ],
    # Equatorial layer - between U and D - direction as a U turn
    'E': [
        # (face, row, col)
        ('F', 1, 0), ('F', 1, 1), ('F', 1, 2),
        ('R', 1, 0), ('R', 1, 1), ('R', 1, 2),
        ('B', 1, 0), ('B', 1, 1), ('B', 1, 2),
        ('L', 1, 0), ('L', 1, 1), ('L', 1, 2)
    ],
    # Standing layer - between F and B - direction as an F turn
    'S': [
        # (face, row, col)
        ('U', 1, 0), ('U', 1, 1), ('U', 1, 2),
        ('R', 0, 1), ('R', 1, 1), ('R', 2, 1),
        ('D', 1, 0), ('D', 1, 1), ('D', 1, 2),
        ('L', 0, 1), ('L', 1, 1), ('L', 2, 1)
    ]
}

slice_number = {
    'M': 0,
    'E': 1,
    'S': 2
}

# selection_color = Color(150, 150, 150)
selection_color = Color.WHITE()


def number_to_slice(n):
    if n == 0:
        return 'M'
    elif n == 1:
        return 'E'
    elif n == 2:
        return 'S'


class Slice(Enum):
    TOP = 0
    MIDDLE = 1
    BOTTOM = 2
    LEFT = 3
    CENTER = 4
    RIGHT = 5
    ALL = 6


slice_xy_range = {
    Slice.TOP: (43, 63),
    Slice.MIDDLE: (22, 42),
    Slice.BOTTOM: (1, 21),
    Slice.LEFT: (1, 21),
    Slice.CENTER: (22, 42),
    Slice.RIGHT: (43, 63)
}

slice_width = 20  # MUST correspond to the delta of slice_xy_ranges


# The following table is the RGB values of the hues of the six colors used on the official Rubik’s Cube.
#
# RGB :
#
# - White 255 255 255
# - Red 137 18 20
# - Blue 13 72 172
# - Orange 255 85 37
# - Green 25 155 76
# - Yellow 254 213 4


def get_color(c):
    if c == 'w':
        return Color.WHITE()
    elif c == 'b':
        # return Color.BLUE()
        # return Color(13, 72, 172)
        return Color(13, 72, 200)
    elif c == 'g':
        # return Color.GREEN()
        return Color(25, 155, 76)
    elif c == 'r':
        # return Color.RED()
        # return Color(137, 18, 20)
        return Color(180, 18, 20)
    elif c == 'y':
        # return Color.YELLOW()
        return Color(254, 213, 4)
    elif c == 'o':
        # return Color.ORANGE()
        # return Color(255, 85, 37)
        return Color(255, 100, 50)


def face_to_plane(face):
    if face == 'U':
        return Face.TOP
    elif face == 'L':
        return Face.LEFT
    elif face == 'F':
        return Face.FRONT
    elif face == 'R':
        return Face.RIGHT
    elif face == 'B':
        return Face.BACK
    elif face == 'D':
        return Face.BOTTOM
    else:
        raise ValueError("Invalid Rubik cube face")


def plane_to_face(plane):
    if plane == Face.TOP.value:
        return 'U'
    elif plane == Face.LEFT.value:
        return 'L'
    elif plane == Face.FRONT.value:
        return 'F'
    elif plane == Face.RIGHT.value:
        return 'R'
    elif plane == Face.BACK.value:
        return 'B'
    elif plane == Face.BOTTOM.value:
        return 'D'
    else:
        raise ValueError("Invalid plane")


def is_in_slice(face, row, col, slice):
    return (face, row, col) in slices[slice]


# The cubie default state is :
#
# - U yellow
# - D white
# - L blue
# - B orange
# - R green
# - F red

# color_to_face_map = {'W': 'U', 'Y': 'D', 'B': 'B', 'G': 'F', 'R': 'R', 'O': 'L'}
# standard :
# face_to_color_map = {'U': 'W', 'D': 'Y', 'L': 'B', 'R': 'G', 'F': 'R', 'B': 'O'}
# color_to_face_map = {'W': 'U', 'Y': 'D', 'B': 'L', 'G': 'R', 'R': 'F', 'O': 'B'}


# Example usage
# face_string = "ULFRBD"
# color_string = face_to_color(face_string)
# print(f"Face to Color: {color_string}")
#
#
# color_string = "WGRYBO"
# face_string = color_to_face(color_string)
# print(f"Color to Face: {face_string}")


face_to_color_map = {'U': 'Y', 'D': 'W', 'L': 'B', 'R': 'G', 'F': 'R', 'B': 'O'}
color_to_face_map = {'W': 'D', 'Y': 'U', 'B': 'L', 'G': 'R', 'R': 'F', 'O': 'B'}


def face_to_color(face_string):
    """Kociemba :

        A cube is defined by its cube definition string. A solved cube has the string

            'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'.
             012345678901234567890123456789012345678901234567890123
             0         1         2         3         4         5

                          | U1  U2  U3 |
                          | U4  U5  U6 |
                          | U7  U8  U9 |
             | L1  L2  L3 | F1  F2  F3 | R1  R2  R3 | B1  B2  B3 |
             | L4  L5  L6 | F4  F5  F6 | R4  R5  R6 | B4  B5  B6 |
             | L7  L8  L9 | F7  F8  F9 | R7  R8  R9 | B7  B8  B9 |
                          | D1  D2  D3 |
                          | D4  D5  D6 |
                          | D7  D8  D9 |
    """

    # face_to_color_map = {'U': 'W', 'D': 'Y', 'L': 'B', 'R': 'G', 'F': 'R', 'B': 'O'}

    # inverse B :
    # UP       RIGHT    FRONT    DOWN     LEFT     BACK
    # from: bwgwwywowbrwrrrgbrrgrrggrgoyyyyywyyywggoowoogbbbbbbooo
    # to:   bwgwwywowbrwrrrgbrrgrrggrgoyyyyywyyywggoowoogooobbbbbb
    #       012345678901234567890123456789012345678901234567890123
    #       0         1         2         3         4         5
    #       BUFUUDULUBRURRRFBRRFRRFFRFLDDDDDUDDDUFFLLULLFLLLBBBBBB

    U = face_string[:9]
    R = face_string[9:18]
    F = face_string[18:27]
    D = face_string[27:36]
    L = face_string[36:45]
    B = face_string[45:]
    # B = face_string[48:] + face_string[45:48]  # inversed (bottom <--> top)

    # print(face_string)
    # print(face_string[51:], '+', face_string[45:51])

    # print(U)
    # print(R)
    # print(F)
    # print(D)
    # print(L)
    # print(B)

    # les faces du cube sont en l'ordre définit par
    # rubik_faces = ('U', 'L', 'F', 'R', 'B', 'D')
    reordered = U + L + F + R + B + D

    return ''.join(face_to_color_map[face] for face in reordered.upper()).lower()


def color_to_face(color_string):
    # color_to_face_map = {'W': 'U', 'Y': 'D', 'B': 'L', 'G': 'R', 'R': 'F', 'O': 'B'}

    # les faces du cube sont en l'ordre définit par
    # rubik_faces = ('U', 'L', 'F', 'R', 'B', 'D')
    U = color_string[:9]
    L = color_string[9:18]
    F = color_string[18:27]
    R = color_string[27:36]
    B = color_string[36:45]
    D = color_string[45:]

    # l'ordre pour Kociemba est :
    reordered = U + R + F + D + L + B
    return ''.join(color_to_face_map[color] for color in reordered.upper()).upper()
