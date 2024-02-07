from collections import namedtuple
from enum import Enum

r"""
    2 parallel chains with 3 panels per chain :
    
    PHYSICAL coordinates :
    
    ┌───────┬───────┬───────┐
    │0,0    │64,0   │128,0  │ Chain 1
    │Left   │Front  │Right  │ <= = Adapter
    └───────┴───────┴───────┘
    ┌───────┬───────┬───────┐
    │0,64   │64,64  │128,64 │ Chain 2
    │Top    │Back   │Bottom │ <= = Adapter
    └───────┴───────┴───────┘
    
    LOGICAL COORDINATES :
    
    ┌──────┬──────┬──────┬──────┐
    │0,0   │64,0  │128,0 │192,0 │
    │Front │Right │Back  │Left  │
    ├──────┼──────┼──────┴──────┘
    │0,64  │64,64 │
    │Top   │Bottom│
    └──────┴──────┘
"""


class Face(Enum):
    FRONT = 0
    RIGHT = 1
    BACK = 2
    LEFT = 3
    TOP = 4
    BOTTOM = 5


# Offset = namedtuple('Offset', ['x', 'y'])
Coord2D = namedtuple('Pos2D', ['x', 'y'])
Coord3D = namedtuple('Pos3D', ['x', 'y', 'z'])

# Planes offsets in logical (mapped) coordinates :
face_offsets = {
    Face.FRONT: Coord2D(x=0, y=0),
    Face.RIGHT: Coord2D(x=64, y=0),
    Face.BACK: Coord2D(x=128, y=0),
    Face.LEFT: Coord2D(x=192, y=0),
    Face.TOP: Coord2D(x=0, y=64),
    Face.BOTTOM: Coord2D(x=64, y=64)
}
# face_offsets = {
#     Face.FRONT: Coord2D(x=0, y=0),
#     Face.RIGHT: Coord2D(x=64, y=0),
#     Face.BACK: Coord2D(x=128, y=0),
#     Face.LEFT: Coord2D(x=192, y=0),
#     Face.TOP: Coord2D(x=0, y=64),
#     Face.BOTTOM: Coord2D(x=64, y=64)
# }

# Accessing the X offset of the Front face
# x_offset_front = face_offsets[Face.FRONT].x

# Other constants
PANEL = 64
WIDTH = 64

#
# class Offset(Enum):
#     LEFT_X = 192
#     LEFT_Y = 0
#     FRONT_X = 0
#     FRONT_Y = 0
#     RIGHT_X = 64
#     RIGHT_Y = 0
#     BACK_X = 128
#     BACK_Y = 0
#     TOP_X = 0
#     TOP_Y = 64
#     BOTTOM_X = 64
#     BOTTOM_Y = 64

FACES_LABELS = {
    'en': {
        Face.FRONT: 'F',
        Face.RIGHT: 'R',
        Face.BACK: 'K',
        Face.LEFT: 'L',
        Face.TOP: 'T',
        Face.BOTTOM: 'B'
    },
    'fr': {
        Face.FRONT: 'V',
        Face.RIGHT: 'D',
        Face.BACK: 'A',
        Face.LEFT: 'G',
        Face.TOP: 'S',
        Face.BOTTOM: 'O'
    }
}
FACES_LABELS['default'] = FACES_LABELS['en']

FACES_NAMES = {
    'en': {
        Face.FRONT: 'Front',
        Face.RIGHT: 'Right',
        Face.BACK: 'Back',
        Face.LEFT: 'Left',
        Face.TOP: 'Top',
        Face.BOTTOM: 'Bottom'
    },
    'fr': {
        Face.FRONT: 'Devant',
        Face.RIGHT: 'Droite',
        Face.BACK: 'Arrière',
        Face.LEFT: 'Gauche',
        Face.TOP: 'Dessus',
        Face.BOTTOM: 'Dessous'
    }
}
FACES_NAMES['default'] = FACES_NAMES['en']

