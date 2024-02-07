class OffLimitException(Exception):
    """todo"""
    pass


def x_from_yz(y, z, a, b, c, d=0.0):
    """
    ax + by + cz + d = 0
    x = (-d - by - cz) / a
    """
    if a != 0:
        return (-d - b * y - c * z) / a
    else:
        raise OffLimitException("a is 0")


def y_from_xz(x, z, a, b, c, d=0.0):
    """
    ax + by + cz + d = 0
    y = (-d - ax - cz) / b
    """
    if b != 0:
        return (-d - a * x - c * z) / b
    else:
        raise OffLimitException("b is 0")


def z_from_xy(x, y, a, b, c, d=0.0):
    """
    ax + by + cz + d = 0
    z = (-d - ax - by) / c
    """
    if c != 0:
        return (-d - a * x - b * y) / c
    else:
        raise OffLimitException("c is 0")


def intersection_plane_xz(x, y, a, b, c):
    """
    FRONT and BACK planes
    :param x:
    :param y: fixe
    :return:

    x0, y0 = map_to_panel(*intersection_plane_xz(x=-0.5, y=-0.5, a, b, c))
    x1, y1 = map_to_panel(*intersection_plane_xz(x=0.5, y=-0.5, a, b, c))
    """
    try:
        z = z_from_xy(x, y, a, b, c)
        if z < -0.5:
            z = -0.5
            return x_from_yz(y, z, a, b, c), z
        elif z > 0.5:
            z = 0.5
            return x_from_yz(y, z, a, b, c), z
        return x, z
    except OffLimitException:
        if x < 0:
            return x_from_yz(y, -0.5, a, b, c), -0.5
        else:
            return x_from_yz(y, 0.5, a, b, c), 0.5


def intersection_plane_yz(x, y, a, b, c):
    """
    LEFT and RIGHT
    :param x: fixe
    :param y:
    :return:

    x0, y0 = map_to_panel(*intersection_plane_yz(0.5, -0.5, a, b, c))
    x1, y1 = map_to_panel(*intersection_plane_yz(0.5, 0.5, a, b, c))
    """
    try:
        z = z_from_xy(x, y, a, b, c)
        if z < -0.5:
            z = -0.5
            return y_from_xz(x, z, a, b, c), z
        elif z > 0.5:
            z = 0.5
            return y_from_xz(x, z, a, b, c), z
        return y, z
    except OffLimitException:
        if y < 0:
            return y_from_xz(x, -0.5, a, b, c), -0.5
        else:
            return y_from_xz(x, 0.5, a, b, c), 0.5


def intersection_plane_xy(x, z, a, b, c):
    """
    TOP and BACK
    :param x:
    :param z: fixe
    :return:

    x0, y0 = map_to_panel(*intersection_plane_xy(-0.5, 0.5, a, b, c))
    x1, y1 = map_to_panel(*intersection_plane_xy(0.5, 0.5, a, b, c))
    """
    try:
        y = y_from_xz(x, z, a, b, c)
        if y < -0.5:
            y = -0.5
            return x_from_yz(y, z, a, b, c), y
        elif y > 0.5:
            y = 0.5
            return x_from_yz(y, z, a, b, c), y
        return x, y
    except OffLimitException:
        if x < 0:
            return x_from_yz(-0.5, z, a, b, c), -0.5
        else:
            return x_from_yz(0.5, z, a, b, c), 0.5
