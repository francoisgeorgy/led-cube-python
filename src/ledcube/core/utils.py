import math
from importlib.resources import files
from math import atan2, sqrt, pi

from ledcube.core import rgb_graphics


# import numpy as np

def r2d(r):
    return r * 180.0 / pi


def matrix_multiplication(a, b):
    # check if matrices can be multiplied
    if len(a[0]) != len(b):
        raise ValueError("Invalid matrix dimensions")

    # p = len(a)
    # q = len(a[0])
    #
    # t = len(b)
    # r = len(b[0])

    # creating the product matrix of dimensions p×r
    # and filling the matrix with 0 entries
    c = []
    for row in range(len(a)):
        curr_row = []
        for col in range(len(b[0])):
            curr_row.append('')
        c.append(curr_row)

    for i in range(len(a)):
        for j in range(len(b[0])):
            tmp = []
            for k in range(len(a[0])):
                tmp.append(f'{a[i][k]}*{b[k][j]}')
            c[i][j] = ' + '.join(tmp)

    return c


def cross_product(v1, v2):
    return [v1[1]*v2[2] - v1[2]*v2[1],
            v1[2]*v2[0] - v1[0]*v2[2],
            v1[0]*v2[1] - v1[1]*v2[0]]


def dot_product(v1, v2):
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]


def u(x):
    return x


def v(y):
    return 63 - y


def reverse(y):
    return 63 - y


def acceleration(p, g):
    ax = g[X] * p[0][X] + g[Y] * p[1][X] + g[Z] * p[2][X]
    ay = g[X] * p[0][Y] + g[Y] * p[1][Y] + g[Z] * p[2][Y]
    az = g[X] * p[0][Z] + g[Y] * p[1][Z] + g[Z] * p[2][Z]
    return [ax, ay, az]


# roll
def rot_x(v):
    return atan2(v[1], v[2])  # atan2(y,z)


# pitch
def rot_y(v):
    x, y, z = v
    # intrinsic
    return atan2(-v[0], sqrt(v[1] ** 2 + v[2] ** 2))


# yaw
def rot_z(v):
    return 0


def get_non_zero_axis_label(vec):
    if vec[0] == 1:
        return "+X"
    elif vec[0] == -1:
        return "-X"
    elif vec[1] == 1:
        return "+Y"
    elif vec[1] == -1:
        return "-Y"
    elif vec[2] == 1:
        return "+Z"
    elif vec[2] == -1:
        return "-Z"
    else:
        return "?"


def get_other_axis_label(x_vec, y_vec):
    if x_vec[0] == 0 and y_vec[0] == 0:
        return "X"
    elif x_vec[1] == 0 and y_vec[1] == 0:
        return "Y"
    elif x_vec[2] == 0 and y_vec[2] == 0:
        return "Z"


def normalize(v):
    length = sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
    return [v[0] / length, v[1] / length, v[2] / length]


# def normalize(vec):
#     d = vec[0] * vec[0] + vec[1] * vec[1] + vec[2] * vec[2]
#     if d > 0:
#         d = math.sqrt(d)
#         for i in range(3):
#             vec[i] /= d


# def strvec(v):
#     return f"({v[0]:5.2f} {v[1]:5.2f} {v[2]:5.2f})"
#     # return f"{v[0]:5} {v[1]:5} {v[2]:5}"


def get_orthonormal_basis_vectors(z):
    """
    https://stackoverflow.com/questions/7753361/construct-an-orthonormal-base-given-only-one-vector-in-3d
    """
    u = (1.0, 0.0, 0.0)
    if abs(dot_product(u, z)) < 0.0001:
        # u is too close to z, choose another vector
        u = (0.0, 1.0, 0.0)
    x = normalize(cross_product(z, u))
    y = normalize(cross_product(z, x))
    return x, y


def strvec(v):
    return f"({v[0]:2} {v[1]:2} {v[2]:2})"
    # return f"{v[0]:5} {v[1]:5} {v[2]:5}"


def strvecf(v):
    return f"({v[0]:5.2f} {v[1]:5.2f} {v[2]:5.2f})"


def map_to_panel(u, v):
    return int((u + 0.5) * 63), int((v + 0.5) * 63)


def clamp(n, min, max):
    if n < min:
        return min
    elif n > max:
        return max
    else:
        return n


def load_font(font_filename):
    font = rgb_graphics.Font()
    # LoadFont argument must be a path (string). This can not be a file.
    font.LoadFont(str(files('ledcube.data.fonts').joinpath(font_filename)))
    return font


