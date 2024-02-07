import logging
import math
import time
from queue import Queue

import twophase.solver as sv

from ledcube.core import Face
from ledcube.core.color import Color
from ledcube.core.cube import Cube
from ledcube.core.utils import v, reverse, load_font
from ledcube.core.mem_cube import MemCube
from examples.rubik.cubie import Cubie
from examples.rubik.cubie.DebugPrinter import DebugPrinter
from examples.rubik.cubie.Move import Move
from examples.rubik.cubie.utils import string_representation, check_valid_cube
from examples.rubik.utils import face_to_plane, get_color, Slice, rubik_faces, is_in_slice, selection_color, \
    slice_xy_range, \
    slice_width, face_to_color, color_to_face

r"""
Run with : 

    python src/examples/rubik/rubik.py -c 4 -P 2

The configuration string of the cube corresponds to the color of the stickers according to the following figure

               ----------------
               | 0  | 1  | 2  |
               ----------------
               | 3  | 4  | 5  |
               ----------------
               | 6  | 7  | 8  |
               ----------------
-------------------------------------------------------------
| 9  | 10 | 11 | 18 | 19 | 20 | 27 | 28 | 29 | 36 | 37 | 38 |
-------------------------------------------------------------
| 12 | 13 | 14 | 21 | 22 | 23 | 30 | 31 | 32 | 39 | 40 | 41 |
-------------------------------------------------------------
| 15 | 16 | 17 | 24 | 25 | 26 | 33 | 34 | 35 | 42 | 43 | 44 |
-------------------------------------------------------------
               ----------------
               | 45 | 46 | 47 |
               ----------------
               | 48 | 49 | 50 |
               ----------------
               | 51 | 52 | 53 |
               ----------------
So, the color at position 0, corresponds to the color of the sticker BLU, the color at 1 is BU and so on ...

        Up
   Left Front Right Back
        Down

Colors used in the implementation are:

[O]range
[B]lue
[R]ed
[W]hite
[Y]ellow
[G]reen
"""


PRINT_CUBE = False
TRACE = False
STEP_BY_STEP = False
SHOW_FACE_COLOR = False

# RANGE_90 = (0, 91, 2)
# RANGE_180 = (0, 181, 2)
# speed up during dev :
RANGE_90 = (0, 91, 10)      # step of 10 for debug
RANGE_180 = (0, 181, 10)    # debug


class Rubik(Cube):

    def __init__(self, message_callback=None):
        super().__init__()
        self.selected_face = None
        self.selected_slice = None
        self.display_face_name = False
        self.large_font = load_font('10x20.bdf')
        self.cube = Cubie.Cube()
        self.mem_cube = MemCube(64)

        self.message_callback = message_callback
        self.task_commands = Queue()
        # self.debug_print_cube()

    def send_message(self, message):
        if self.message_callback is not None:
            self.message_callback(message)

    def debug_print_cube(self):
        if PRINT_CUBE:
            printer = DebugPrinter(self.cube, True)
            printer.pprint()

    def get_representation(self):
        return string_representation(self.cube)

    def init_from_colors(self, s):
        self.set_cube_from_string(s)

    def init_from_faces(self, s):
        self.set_cube_from_string(face_to_color(s))

    def toggle_face(self, face):
        """
        If 'face' is the currently selected face, then toggle the selection.
        If 'face' is another face, select it. If another face was already selected,
        unselected this face before selecting the new face.
        :param face:
        :return:
        """
        if face is None:
            self.selected_face = None
        else:
            if self.selected_face == face:
                self.selected_face = None
            else:
                self.selected_face = face

    def move_selection(self, m):
        if m not in ('cw', 'ccw', '180'):
            # TODO: raise exception
            return
        if self.selected_face is None:
            # ignore
            return
        s = self.selected_face
        if m == '180':
            s = s + '2'
        elif m == 'ccw':
            s = s + "'"
        m = Move(s)
        self.selected_slice = None
        self.selected_face = None
        self.move_cube(m)

    # 0                           63
    # | 2...19 | 23...40 | 44...61 |
    #
    # STYLE 2
    def draw_square(self, plane, i, j, color):
        x0 = j * 21 + 2
        y0 = i * 21 + 2
        for y in range(18):
            for x in range(18):
                if (y == 0 and x == 0) or (y == 0 and x == 17) or (y == 17 and x == 0) or (y == 17 and x == 17):
                    continue
                #
                # Attention: we must use v(y) here because the LED-cube Y axis is from bottom to up but
                #            the Rubik cube Y axis is top to bottom.
                #
                self.planes[plane.value].pixel(x0 + x, v(y0 + y), color)
                self.mem_cube.set_pixel(plane.value, x0 + x, v(y0 + y), color)
        if SHOW_FACE_COLOR:
            self.planes[plane.value].text(x0 + 2, v(y0 + 9), Color.BLACK())

    def draw_square_with_background(self, plane, i, j, color, background=None):
        # TODO: optimize
        # background :
        x0 = j * 21
        y0 = i * 21
        for y in range(22):
            for x in range(22):
                self.planes[plane.value].pixel(x0 + x, v(y0 + y), background)
        # cell :
        x0 = j * 21 + 2
        y0 = i * 21 + 2
        for y in range(18):
            for x in range(18):
                if (y == 0 and x == 0) or (y == 0 and x == 17) or (y == 17 and x == 0) or (y == 17 and x == 17):
                    # if True:
                    self.planes[plane.value].pixel(x0 + x, v(y0 + y), background)
                    # else:
                    #     continue
                self.planes[plane.value].pixel(x0 + x, v(y0 + y), color)
                self.mem_cube.set_pixel(plane.value, x0 + x, v(y0 + y), color)
        # cell border :
        x0 = j * 21 + 2
        y0 = i * 21 + 2
        p = self.planes[plane.value]
        p.line(x0, v(y0), x0+17, v(y0), Color.BLACK())
        p.line(x0+17, v(y0), x0+17, v(y0+17), Color.BLACK())
        p.line(x0+17, v(y0+17), x0, v(y0+17), Color.BLACK())
        p.line(x0, v(y0+17), x0, v(y0), Color.BLACK())
        p.pixel(x0+1, v(y0+1), Color.BLACK())
        p.pixel(x0+16, v(y0+1), Color.BLACK())
        p.pixel(x0+16, v(y0+16), Color.BLACK())
        p.pixel(x0+1, v(y0+16), Color.BLACK())
        p.pixel(x0, v(y0), background)
        p.pixel(x0+17, v(y0), background)
        p.pixel(x0+17, v(y0+17), background)
        p.pixel(x0, v(y0+17), background)

    def draw_cube(self):
        c = self.cube.to_naive_cube()
        for face in rubik_faces:
            p = self.planes[face_to_plane(face).value]
            for i in range(c.size):
                for j in range(c.size):
                    self.draw_square(face_to_plane(face), i, j, get_color(c.faces[face].get_colour(int(i), int(j))))
                    if self.selected_slice and is_in_slice(face, i, j, self.selected_slice):
                        # style 1 :
                        # self.draw_square_with_background(face_to_plane(face), i, j, get_color(c.faces[face].get_colour(int(i), int(j))), selection_color)
                        # style 2 :
                        # self.draw_square(face_to_plane(face), i, j, get_color(c.faces[face].get_colour(int(i), int(j))))
                        x0 = j * 21
                        y0 = i * 21
                        w = 21
                        p.line(x0, v(y0), x0+w, v(y0), selection_color)
                        p.line(x0+w, v(y0), x0+w, v(y0+w), selection_color)
                        p.line(x0+w, v(y0+w), x0, v(y0+w), selection_color)
                        p.line(x0, v(y0+w), x0, v(y0), selection_color)
                    # else:
                    #     self.draw_square(face_to_plane(face), i, j, get_color(c.faces[face].get_colour(int(i), int(j))))
            if self.selected_face == face:
                p.border(selection_color)
            if self.display_face_name:
                p.text(27, 24, Color.BLACK(), face, self.large_font)

    # used, e.g., when drawing a slice
    def redraw_cube(self):
        self.clear()
        # self.selected_face = None
        # self.selected_slice = None
        self.draw_cube()
        self.refresh()
        self.draw_cube()    # Initialize the new cancas with the cube to avoid flicker

    def reset_cube(self):
        self.cube.reset()
        self.selected_face = None
        self.selected_slice = None
        self.clear()
        self.draw_cube()
        self.refresh()
        self.draw_cube()    # Initialize the new cancas with the cube to avoid flicker
        # self.send_message("cube reset")

    def shuffle_cube(self):
        self.cube.shuffle()
        self.clear()
        self.draw_cube()
        self.refresh()
        self.draw_cube()    # Initialize the new cancas with the cube to avoid flicker
        # self.send_message("cube shuffled")

    def set_cube_from_string(self, cube_str):
        self.cube = check_valid_cube(cube_str)
        # self.send_message("cube initialized")

    def names(self):
        """Display (toggle) the face name"""
        self.display_face_name = not self.display_face_name
        self.redraw_cube()

    def hint(self):
        """Show the next face or slice to move"""
        # TODO
        cube_str = string_representation(self.cube)
        # logging.debug("current cube:", cube_str)
        # moves = solve(cube_str, 'CFOP')
        # logging.debug("movements to solve:", moves)

    def shift_x_slice(self, face, distance, cw):
        """
        top, back, bottom, front are oriented the same
        shift is vertical
        cw :  top --> back --> bottom --> front --> top ...
        ccw : top --> front --> bottom --> back --> top ...

        BACK has x reversed relative to front, so we have to call u(x) on BACK.

        :param face:
        :param distance:
        :param cw:
        :return:
        """

        if distance == 0:
            return

        if face == Face.RIGHT:
            front_offset = slice_xy_range[Slice.RIGHT][0]
            top_offset = slice_xy_range[Slice.RIGHT][0]
            back_offset = slice_xy_range[Slice.LEFT][0]
            down_offset = slice_xy_range[Slice.RIGHT][0]
        else:
            front_offset = slice_xy_range[Slice.LEFT][0]
            top_offset = slice_xy_range[Slice.LEFT][0]
            back_offset = slice_xy_range[Slice.RIGHT][0]
            down_offset = slice_xy_range[Slice.LEFT][0]

        # i, j = slice_xy_range[slice]
        for y in range(64 - 1):
            if cw:
                # R is rotated cw or L is rotated ccw
                # shift must be from bottom to top : y(0) replace y(1)
                y_from = y - distance
            else:
                # R is rotated ccw or L is rotated cw
                # shift must be from top to bottom
                y_from = y + distance
            for x in range(slice_width):
                if cw:
                    # FRONT --> TOP :
                    if y_from < 0:
                        r, g, b = self.mem_cube.get_pixel(Face.FRONT.value, x+front_offset, y_from + 64)
                    else:
                        r, g, b = self.mem_cube.get_pixel(Face.TOP.value, x+top_offset, y_from)
                    self.planes[Face.TOP.value].pixel(x+top_offset, y, Color(r, g, b))

                    # TOP --> BACK :
                    if y_from < 0:
                        r, g, b = self.mem_cube.get_pixel(Face.TOP.value, x+top_offset, y_from + 64)
                    else:
                        r, g, b = self.mem_cube.get_pixel(Face.BACK.value, x+back_offset, reverse(y_from))
                    # reverse BACK Y movement direction
                    self.planes[Face.BACK.value].pixel(x+back_offset, reverse(y), Color(r, g, b))

                    # BACK --> BOTTOM :
                    if y_from < 0:
                        r, g, b = self.mem_cube.get_pixel(Face.BACK.value, x+back_offset, y_from + 64)
                    else:
                        r, g, b = self.mem_cube.get_pixel(Face.BOTTOM.value, x+down_offset, y_from)
                    self.planes[Face.BOTTOM.value].pixel(x+down_offset, y, Color(r, g, b))

                    # BOTTOM --> FRONT :
                    if y_from < 0:
                        r, g, b = self.mem_cube.get_pixel(Face.BOTTOM.value, x+down_offset, y_from + 64)
                    else:
                        r, g, b = self.mem_cube.get_pixel(Face.FRONT.value, x+front_offset, y_from)
                    self.planes[Face.FRONT.value].pixel(x+front_offset, y, Color(r, g, b))

                else:
                    # BACK --> TOP :
                    if y_from < 64:
                        r, g, b = self.mem_cube.get_pixel(Face.TOP.value, x+top_offset, y_from)
                    else:
                        r, g, b = self.mem_cube.get_pixel(Face.BACK.value, x+back_offset, reverse(y_from - 64))
                    self.planes[Face.TOP.value].pixel(x+top_offset, y, Color(r, g, b))

                    # BOTTOM --> BACK :
                    if y_from < 64:
                        r, g, b = self.mem_cube.get_pixel(Face.BACK.value, x+back_offset, reverse(y_from))
                    else:
                        r, g, b = self.mem_cube.get_pixel(Face.BOTTOM.value, x+down_offset, y_from - 64)
                    # reverse BACK Y movement direction
                    self.planes[Face.BACK.value].pixel(x+back_offset, reverse(y), Color(r, g, b))

                    # FRONT --> BOTTOM :
                    if y_from < 64:
                        r, g, b = self.mem_cube.get_pixel(Face.BOTTOM.value, x+down_offset, y_from)
                    else:
                        r, g, b = self.mem_cube.get_pixel(Face.FRONT.value, x+front_offset, y_from - 64)
                    # reverse BACK Y movement direction
                    self.planes[Face.BOTTOM.value].pixel(x+down_offset, y, Color(r, g, b))

                    # TOP --> FRONT :
                    if y_from < 64:
                        r, g, b = self.mem_cube.get_pixel(Face.FRONT.value, x+front_offset, y_from)
                    else:
                        r, g, b = self.mem_cube.get_pixel(Face.TOP.value, x+top_offset, y_from - 64)
                    self.planes[Face.FRONT.value].pixel(x+front_offset, y, Color(r, g, b))

    def shift_y_slice(self, slice, distance, cw):
        """
        front, right, back, left front are vertically oriented the same; back as X reversed
        shift is horizontal
        cw :  front --> right --> back --> left --> front ...
        ccw : front --> left --> back --> right --> front ...

        BACK has x reversed relative to front, so we have to call u(x) on BACK.

        :param slice:
        :param distance:
        :param cw:
        :return:
        """

        if distance == 0:
            # logging.debug("distance is 0")
            return

        i, j = slice_xy_range[slice]
        for x in range(64 - 1):
            if cw:
                # R is rotated cw or L is rotated ccw
                # shift must be from bottom to top : y(0) replace y(1)
                x_from = x + distance
            else:
                # R is rotated ccw or L is rotated cw
                # shift must be from top to bottom
                x_from = x - distance
            for y in range(i, j):
                if cw:
                    # ccw : front --> left --> back --> right --> front ...
                    if x_from < 64:
                        r, g, b = self.mem_cube.get_pixel(Face.FRONT.value, x_from, y)
                    else:
                        r, g, b = self.mem_cube.get_pixel(Face.RIGHT.value, x_from - 64, y)
                    self.planes[Face.FRONT.value].pixel(x, y, Color(r, g, b))

                    if x_from < 64:
                        r, g, b = self.mem_cube.get_pixel(Face.RIGHT.value, x_from, y)
                    else:
                        r, g, b = self.mem_cube.get_pixel(Face.BACK.value, x_from - 64, y)
                    self.planes[Face.RIGHT.value].pixel(x, y, Color(r, g, b))

                    if x_from < 64:
                        r, g, b = self.mem_cube.get_pixel(Face.BACK.value, x_from, y)
                    else:
                        r, g, b = self.mem_cube.get_pixel(Face.LEFT.value, x_from - 64, y)
                    self.planes[Face.BACK.value].pixel(x, y, Color(r, g, b))

                    if x_from < 64:
                        r, g, b = self.mem_cube.get_pixel(Face.LEFT.value, x_from, y)
                    else:
                        r, g, b = self.mem_cube.get_pixel(Face.FRONT.value, x_from - 64, y)
                    self.planes[Face.LEFT.value].pixel(x, y, Color(r, g, b))

                else:
                    # cw :  front --> right --> back --> left --> front ...
                    if x_from < 0:
                        r, g, b = self.mem_cube.get_pixel(Face.LEFT.value, x_from + 64, y)
                    else:
                        r, g, b = self.mem_cube.get_pixel(Face.FRONT.value, x_from, y)
                    self.planes[Face.FRONT.value].pixel(x, y, Color(r, g, b))

                    if x_from < 0:
                        r, g, b = self.mem_cube.get_pixel(Face.FRONT.value, x_from + 64, y)
                    else:
                        r, g, b = self.mem_cube.get_pixel(Face.RIGHT.value, x_from, y)
                    self.planes[Face.RIGHT.value].pixel(x, y, Color(r, g, b))

                    if x_from < 0:
                        r, g, b = self.mem_cube.get_pixel(Face.RIGHT.value, x_from + 64, y)
                    else:
                        r, g, b = self.mem_cube.get_pixel(Face.BACK.value, x_from, y)
                    self.planes[Face.BACK.value].pixel(x, y, Color(r, g, b))

                    if x_from < 0:
                        r, g, b = self.mem_cube.get_pixel(Face.BACK.value, x_from + 64, y)
                    else:
                        r, g, b = self.mem_cube.get_pixel(Face.LEFT.value, x_from, y)
                    self.planes[Face.LEFT.value].pixel(x, y, Color(r, g, b))

    def shift_z_slice(self, face, distance, cw):
        """
        top, right, bottom, left are NOT oriented the same

        :param face:
        :param distance:
        :param cw:
        :return:
        """

        if distance == 0:
            return

        # if face == Face.FRONT:
        # i_bottom, j_bottom = slice_xy_range[Slice.BOTTOM]
        # elif face == Face.FRONT:
        # i_front, j_front = slice_xy_range[Slice.TOP]
        # else:
        #     raise ValueError("Unsupported face for Z axis rotation")

        if face == Face.FRONT:
            top_offset = slice_xy_range[Slice.BOTTOM][0]
            right_offset = slice_xy_range[Slice.LEFT][0]
            down_offset = slice_xy_range[Slice.TOP][0]
            left_offset = slice_xy_range[Slice.RIGHT][0]
            # else:
            #     top_offset = slice_xy_range[Slice.BOTTOM][0]
            #     right_offset = slice_xy_range[Slice.LEFT][0]
            #     down_offset = slice_xy_range[Slice.TOP][0]
            #     left_offset = slice_xy_range[Slice.RIGHT][0]
        else:
            top_offset = slice_xy_range[Slice.TOP][0]
            right_offset = slice_xy_range[Slice.RIGHT][0]
            down_offset = slice_xy_range[Slice.BOTTOM][0]
            left_offset = slice_xy_range[Slice.LEFT][0]

        for s in range(64 - 1):
            if cw:
                _from = s - distance
            else:
                _from = s + distance
            for w in range(slice_width):
                if cw:
                    # TOP --> RIGHT
                    #
                    # CW(U) means CCW(R) --> we use reverse() on R
                    if _from < 0:
                        # TOP is horizontal
                        r, g, b = self.mem_cube.get_pixel(Face.TOP.value, _from + 64, w+top_offset)
                    else:
                        # RIGHT is vertical
                        r, g, b = self.mem_cube.get_pixel(Face.RIGHT.value, w+right_offset, reverse(_from))
                    # reverse RIGHT Y axis :
                    self.planes[Face.RIGHT.value].pixel(w+right_offset, reverse(s), Color(r, g, b))

                    # RIGHT --> DOWN
                    if _from < 0:
                        # RIGHT is vertical
                        r, g, b = self.mem_cube.get_pixel(Face.RIGHT.value, w + right_offset, reverse(_from + 64))
                    else:
                        # BOTTOM is horizontal
                        r, g, b = self.mem_cube.get_pixel(Face.BOTTOM.value, reverse(_from), w + down_offset)
                    self.planes[Face.BOTTOM.value].pixel(reverse(s), w+down_offset, Color(r, g, b))

                    # DOWN --> LEFT : similar to a rotation on X axis
                    # OK
                    if _from < 0:
                        # DOWN is horizontal
                        r, g, b = self.mem_cube.get_pixel(Face.BOTTOM.value, reverse(_from + 64), w + down_offset)
                    else:
                        # LEFT is vertical
                        r, g, b = self.mem_cube.get_pixel(Face.LEFT.value, w+left_offset, _from)
                    self.planes[Face.LEFT.value].pixel(w+left_offset, s, Color(r, g, b))

                    # LEFT --> TOP
                    # OK
                    if _from < 0:
                        # LEFT is vertical
                        r, g, b = self.mem_cube.get_pixel(Face.LEFT.value, w+left_offset, _from + 64)
                    else:
                        # TOP is horizontal
                        r, g, b = self.mem_cube.get_pixel(Face.TOP.value, _from, w+top_offset)
                    self.planes[Face.TOP.value].pixel(s, w+top_offset, Color(r, g, b))

                else:
                    # TOP --> LEFT
                    if _from < 64:
                        # LEFT is vertical
                        r, g, b = self.mem_cube.get_pixel(Face.LEFT.value, w+left_offset, _from)
                    else:
                        # TOP is horizontal
                        r, g, b = self.mem_cube.get_pixel(Face.TOP.value, _from - 64, w+top_offset)
                    self.planes[Face.LEFT.value].pixel(w+left_offset, s, Color(r, g, b))

                    # LEFT --> DOWN
                    if _from < 64:
                        # DOWN is horizontal
                        r, g, b = self.mem_cube.get_pixel(Face.BOTTOM.value, reverse(_from), w + down_offset)
                    else:
                        # LEFT is vertical
                        r, g, b = self.mem_cube.get_pixel(Face.LEFT.value, w+left_offset, _from - 64)
                    self.planes[Face.BOTTOM.value].pixel(reverse(s), w+down_offset, Color(r, g, b))

                    # DOWN --> RIGHT
                    # CW(U) means CCW(R) --> we use reverse() on R
                    if _from < 64:
                        # RIGHT is vertical
                        r, g, b = self.mem_cube.get_pixel(Face.RIGHT.value, w+right_offset, reverse(_from))
                    else:
                        # DOWN is horizontal
                        r, g, b = self.mem_cube.get_pixel(Face.BOTTOM.value, reverse(_from - 64), w+down_offset)
                    self.planes[Face.RIGHT.value].pixel(w+right_offset, reverse(s), Color(r, g, b))

                    # RIGHT --> TOP
                    if _from < 64:
                        # TOP is horizontal
                        r, g, b = self.mem_cube.get_pixel(Face.TOP.value, _from, w+top_offset)
                    else:
                        # RIGHT is vertical
                        r, g, b = self.mem_cube.get_pixel(Face.RIGHT.value, w + right_offset, reverse(_from - 64))
                    self.planes[Face.TOP.value].pixel(s, w+top_offset, Color(r, g, b))

    def mem_pixel(self, p, x, y, orient=0):
        """
        Example: when rotating F, R vertical slices are shifted into F horizontal slices

            y bottom = y==0

            F bottom slice : R[x max, y 0] <-- F[x 0, y max]
                             R[x max, y N] <-- F[x N, y max]
            FFF
            FFF
            FFF  RRR   --> R must be rotated 90 ccw
                 RRR       to align its left slice with F bottom slice
                 RRR

        :param p:
        :param orient: 0 = horizontal, 1=90 cw, -1=90 ccw, 2=180
        :param x:
        :param y:
        :return:
        """
        if orient == 0:
            return self.mem_cube.get_pixel(p, x, v(y))
        elif orient == -1:
            return self.mem_cube.get_pixel(p, v(y), x)
        elif orient == 1:
            return self.mem_cube.get_pixel(p, x, v(y))
        elif orient == 2:
            return self.mem_cube.get_pixel(p, x, v(63-y))

    def rotate_face_angle(self, plane, angle, whole_cube=False):
        # logging.debug("rotate", plane)

        # If the whole the cube has to be rotated, the face needs to be U, F or R.
        # FIXME: review and test when called with whole_cube=True

        plane2 = None
        if whole_cube:
            if plane == Face.TOP.value:
                plane2 = Face.BOTTOM.value
            elif plane == Face.LEFT.value:
                plane2 = Face.RIGHT.value
            elif plane == Face.FRONT.value:
                plane2 = Face.BACK.value

        width, height = 64, 64
        center = (width / 2 - 0.5, height / 2 - 0.5)
        angle_rad = math.radians(angle)
        sin_angle = math.sin(angle_rad)
        cos_angle = math.cos(angle_rad)

        # fill face in black to avoid rotation artefacts
        for x in range(width):
            for y in range(height):
                self.planes[plane].pixel(x, y, Color.BLACK())

        for x in range(width):
            for y in range(height):

                # Translate coordinates
                xt = x - center[0]
                yt = y - center[1]

                # Apply rotation
                xr = xt * cos_angle - yt * sin_angle
                yr = xt * sin_angle + yt * cos_angle

                # Translate back and round to nearest integer
                new_x = round(xr + center[0] + 0.0)
                new_y = round(yr + center[1] + 0.0)

                # Check if the new coordinates are within the canvas bounds
                if 0 <= new_x < width and 0 <= new_y < height:
                    r, g, b = self.mem_cube.get_pixel(plane, x, y)
                    # self.planes[plane].pixel(new_x, v(new_y), Color(r, g, b))
                    self.planes[plane].pixel(new_x, new_y, Color(r, g, b))
                    if plane2:
                        r, g, b = self.mem_cube.get_pixel(plane2, x, y)
                        # self.planes[plane2].pixel(new_x, v(new_y), Color(r, g, b))
                        self.planes[plane2].pixel(new_x, new_y, Color(r, g, b))

        shift_amount = abs(int(64 * sin_angle))
        # cw = angle >= 0
        cw = angle < 0

        # TODO: if shift_amount hasn't changed since last call, to not call shift_adjacent_edges.
        #       Only if this doesn't have a visual impact on the performances.

        if plane == Face.RIGHT.value:
            self.shift_x_slice(Face.RIGHT, shift_amount, cw)

        elif plane == Face.LEFT.value:
            self.shift_x_slice(Face.LEFT, shift_amount, not cw)

        elif plane == Face.TOP.value:
            self.shift_y_slice(Slice.TOP, shift_amount, cw)

        elif plane == Face.BOTTOM.value:
            self.shift_y_slice(Slice.BOTTOM, shift_amount, not cw)

        elif plane == Face.FRONT.value:
            self.shift_z_slice(Face.FRONT, shift_amount, cw)

        elif plane == Face.BACK.value:
            self.shift_z_slice(Face.BACK, shift_amount, not cw)

    def rotate_layer_angle(self, plane, angle):
        # TODO
        pass
        # shift_amount = int(64 * math.sin(math.radians(angle)))
        # if plane == 'M':
        #     # Rotate the middle layer parallel to the left face 90 degrees clockwise
        #     self.shift_adjacent_edges(
        #         Face.FRONT.value,
        #         Face.RIGHT.value,
        #         Face.BACK.value,
        #         Face.LEFT.value, shift_amount,
        #         Slice.MIDDLE, horizontal=False, cw=True)
        # elif plane == 'E':
        #     # Rotate the equatorial layer 90 degrees clockwise
        #     self.shift_adjacent_edges(
        #         Face.FRONT.value,
        #         Face.RIGHT.value,
        #         Face.BACK.value,
        #         Face.LEFT.value, shift_amount,
        #         Slice.MIDDLE, horizontal=True, cw=True)
        # elif plane == 'S':
        #     # Rotate the standing layer parallel to the front face 90 degrees clockwise
        #     self.shift_adjacent_edges(
        #         Face.TOP.value,
        #         Face.RIGHT.value,
        #         Face.BOTTOM.value,
        #         Face.LEFT.value, shift_amount,
        #         Slice.MIDDLE, horizontal=False, cw=True)
        # # elif plane == Face.BOTTOM.value:
        # #     self.shift_adjacent_edges(Face.FRONT.value, Face.RIGHT.value, Face.BACK.value, Face.LEFT.value, shift_amount, Slice.BOTTOM, horizontal=True, cw=True)
        # # elif plane == Face.FRONT.value:
        # #     self.shift_adjacent_edges(Face.TOP.value, Face.RIGHT.value, Face.BOTTOM.value, Face.LEFT.value, shift_amount, Slice.TOP, horizontal=False, cw=True)
        # # elif plane == Face.BACK.value:
        # #     self.shift_adjacent_edges(Face.TOP.value, Face.RIGHT.value, Face.BOTTOM.value, Face.LEFT.value, shift_amount, Slice.BOTTOM, horizontal=False, cw=True)

    def rotate_cube(self, plane, angle):
        self.rotate_face_angle(plane, angle, whole_cube=True)

    def animate_rotate_layer(self, layer, angle_start, angle_end, angle_step, cw=True):
        """
        :param cw:
        :param layer: 'M', 'E', 'S'
        :param angle_start:
        :param angle_end:
        :param angle_step:
        :return:
        """
        # logging.debug('animate_rotate_layer')
        for angle in range(angle_start, angle_end, angle_step):
            self.rotate_layer_angle(layer, angle if cw else -angle)
            self.refresh()
            # FIXME: need to call draw_cube here?

    # def fill_v1(self):
    #     for y in range(self.matrix.height):
    #         for x in range(self.matrix.width):
    #             self.pixel(x, y, Color(100, 200, 100))
    #
    # def fill_v2(self):
    #     for y in range(self.matrix.height):
    #         for x in range(self.matrix.width):
    #             self.canvas.SetPixel(x, y, 100, 200, 100)

    def animate_rotate_face(self, face, angle_start, angle_end, angle_step, cw=True):
        """
        :param cw:
        :param face: 'U', 'L', 'F', 'R', 'B', 'D'
        :param angle_start:
        :param angle_end:
        :param angle_step:
        :return:
        """
        p = face_to_plane(face).value
        t0 = time.time()
        i = 0   # debug
        # angle_step = 10  # DEBUG

        self.refresh()  # PROBLEM HERE

        # for angle in range(angle_start, angle_end, angle_step):
        for angle in range(angle_step, angle_end, angle_step):
            i = i+1
            self.rotate_face_angle(p, angle if not cw else -angle)
            self.refresh()

        t1 = time.time()
        # logging.debug((t1 - t0) * 1000, 'ms total,', (t1 - t0) * 1000 / i, 'ms per iteration')

    def animate_rotate_cube(self, axis, angle_start, angle_end, angle_step):
        """
        :param axis: 'X', 'Y', 'Z'
        :param angle_start:
        :param angle_end:
        :param angle_step:
        :return:
        """
        # TODO: axis to face
        if axis == 'X':
            face = 'R'
        elif axis == 'Y':
            face = 'U'
        elif axis == 'Z':
            face = 'F'
        else:
            raise ValueError("Invalid axis for the cube rotation")
        p = face_to_plane(face).value
        for angle in range(angle_start, angle_end, angle_step):
            self.rotate_face_angle(p, angle)
            self.refresh()
            # FIXME: need to call draw_cube here?

    def move_cube(self, movement):
        # logging.debug("=== move_cube", type(movement), isinstance(movement, Move), movement.face, movement.clockwise, "===")

        # self.send_message(f"move cube {movement.raw}")

        # redraw the cube to remove any selection outline
        self.redraw_cube()

        # self.cube.move(movement)
        # self.redraw_cube()
        # return

        # angle_range = RANGE_180 if movement.double else RANGE_90

        # to simplify the animation routines, we do two 90 rotations instead of one 180.
        steps = 2 if movement.double else 1
        # logging.debug(movement.face, movement.double, movement.clockwise, steps)
        # save CW because set Move.double setter is bugged
        cw = movement.clockwise
        movement.double = False
        movement.clockwise = cw
        for _ in range(steps):
            update_cube = False
            if movement.face in rubik_faces:
                self.animate_rotate_face(movement.face, *RANGE_90, movement.clockwise)
                update_cube = True
            if update_cube:
                self.cube.move(movement)
                self.redraw_cube()

            # update_cube = False
            # self.refresh()

        # TODO
        # elif movement.face in rubik_slices:
        #     # TODO
        #     self.animate_rotate_layer(movement.face, *angle_range, movement.clockwise)
        #     update_cube = True
        # elif movement.face in rubik_axes:
        #     # TODO
        #     self.animate_rotate_cube(movement.face, *angle_range)
        #     update_cube = True
        # if update_cube:
        #     logging.debug("    >>> self.cube.move", movement)
        #     self.cube.move(movement)
        #     # self.debug_logging.debug_cube()
        #     self.redraw_cube()

    def auto_solve(self, progress_callback=None):
        logging.debug("rubik.auto_solve")

        self.selected_slice = None
        self.selected_face = None
        s = string_representation(self.cube)
        kociemba = color_to_face(s)
        ok = False
        steps = ""
        try:
            steps = sv.solve(kociemba, 30, 2)
            # TODO: check result of sv.solve
            ok = 'error' not in steps.lower()
        except TypeError:
            pass
        if not ok:
            logging.warning("rubik.auto_solve failed; return")
            # TODO : signal error to user
            return

        # if progress_callback is not None:
        #     # TODO: implement progress callback
        #     progress_callback('solution found')
        #     pass

        steps = steps.replace("3", "'").replace("1", '').split(' ')[:-1]

        self.send_message(f"auto-solve: solution found with {len(steps)} moves")

        n_steps = len(steps)
        abort = False
        i = 0
        for step in steps:
            try:
                logging.debug("rubik.auto_solve: step", step, self.task_commands.qsize())

                while not abort and self.task_commands.qsize() > 0:
                    command = self.task_commands.get()
                    logging.debug("rubik.auto-solve: received task_command: ", command)
                    if command == "stop":
                        logging.info("rubik.auto_solve: stop requested")
                        self.send_message("auto-solve abort")
                        abort = True

                if abort:
                    logging.debug("rubik.auto-solve: abort auto-solve", command)
                    break

                i += 1
                self.send_message(f'{step} ({i}/{n_steps})')
                m = Move(step)
                self.move_cube(m)
                self.redraw_cube()

            except ValueError:
                logging.debug("rubik.auto_solve: invalid move", step)
                break

        logging.info(f"rubik.auto-solve {'completed' if not abort else 'aborted'}")
        self.send_message(f"auto-solve {'completed' if not abort else 'aborted'}")

