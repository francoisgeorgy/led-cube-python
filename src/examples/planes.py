"""Show the X, Y and Z planes, aligned with the cube origin (0, 0, 0).

The accelerometer output is taken as the normal vector of the Z plane (Z-axis vector).

To find the other orthogonal vectors (for the X and Y planes) :

1. Find X-axis vector:

    Find a vector orthogonal to the Z-axis vector.
    There are many ways to do this, but a common method is to take the cross product of the new Z-axis vector
    with some other vector that is not parallel to it. A good choice is often one of the original coordinate
    axes (like (1,0,0) or (0,1,0)), unless the new Z-axis vector is parallel or nearly parallel to that axis.

2. Find Y-axis vector:

    Once we have the X-axis vector, we can find the Y-axis vector by taking the cross product of the Z-axis vector
    with the X-axis vector. This ensures orthogonality.

Algorithm :

    z is the accelerator unit vector.
    Take u = (1,0,0).
    If dot(u,z) ~= 0, then take u = (0,1,0).
    Then, x = z ^ u and y = z ^ x.

See https://stackoverflow.com/questions/7753361/construct-an-orthonormal-base-given-only-one-vector-in-3d

Units : the cube is of unit "1". The length of the edges is 1. The center of the cube is at (0, 0, 0) and
the faces of the cube are at +-0.5.

"""

from ledcube.core import Face
from ledcube.core.color import Color
from ledcube.core.cube import Cube
from ledcube.core.utils import normalize, reverse, strvecf, dot_product, cross_product, get_orthonormal_basis_vectors, \
    map_to_panel
from ledcube.geometry.planes import intersection_plane_xy, OffLimitException, intersection_plane_xz, \
    intersection_plane_yz


# def map_to_panel(u, v):
#     return int((u + 0.5) * 63), int((v + 0.5) * 63)


class Planes(Cube):

    def draw_line(self, face, x0, y0, x1, y1, color):
        if 0 <= x0 <= 63 and 0 <= y0 <= 63 and 0 <= x1 <= 63 and 0 <= y1 <= 63:
            self.planes[face].line(x0, y0, x1, y1, color)
        # else:
            # print(face.value, x0, y0, 'to', x1, y1, 'is off limit')

    def draw_plane(self, a, b, c, color):

        try:
            self.draw_line(
                Face.TOP.value,
                *map_to_panel(*intersection_plane_xy(-0.5, 0.5, a, b, c)),
                *map_to_panel(*intersection_plane_xy(0.5, 0.5, a, b, c)),
                color)
        except OffLimitException as e:
            pass

        try:
            self.draw_line(
                Face.FRONT.value,
                *map_to_panel(*intersection_plane_xz(-0.5, -0.5, a, b, c)),
                *map_to_panel(*intersection_plane_xz(0.5, -0.5, a, b, c)),
                color)
        except OffLimitException as e:
            pass

        try:
            self.draw_line(
                Face.RIGHT.value,
                *map_to_panel(*intersection_plane_yz(0.5, -0.5, a, b, c)),
                *map_to_panel(*intersection_plane_yz(0.5, 0.5, a, b, c)),
                color)
        except OffLimitException as e:
            pass

        try:
            x0, y0 = map_to_panel(*intersection_plane_xz(0.5, 0.5, a, b, c))
            x1, y1 = map_to_panel(*intersection_plane_xz(-0.5, 0.5, a, b, c))
            self.draw_line(
                Face.BACK.value,
                reverse(x0), y0,
                reverse(x1), y1,
                color)
        except OffLimitException as e:
            pass

        try:
            x0, y0 = map_to_panel(*intersection_plane_yz(-0.5, -0.5, a, b, c))
            x1, y1 = map_to_panel(*intersection_plane_yz(-0.5, 0.5, a, b, c))
            self.draw_line(
                Face.LEFT.value,
                reverse(x0), y0,
                reverse(x1), y1,
                color)
        except OffLimitException as e:
            pass

        try:
            x0, y0 = map_to_panel(*intersection_plane_xy(-0.5, -0.5, a, b, c))
            x1, y1 = map_to_panel(*intersection_plane_xy(0.5, -0.5, a, b, c))
            self.draw_line(
                Face.BOTTOM.value,
                x0, reverse(y0),
                x1, reverse(y1),
                color)
        except OffLimitException as e:
            pass

    def run(self):
        while True:
            try:
                self.clear()

                x, y, z = self.imu.acceleration
                f = 5
                if True:
                    x = round(x*f) / f
                    y = round(y*f) / f
                    z = round(z*f) / f
                a, b, c = normalize((x, y, z))

                self.draw_plane(a, b, c, Color.YELLOW())  # Z plane
                v2, v3 = get_orthonormal_basis_vectors([a, b, c])
                self.draw_plane(*v2, Color.RED())
                self.draw_plane(*v3, Color.BLUE())
                self.refresh()
                # print(strvecf((a, b, c)), strvecf(v2), strvecf(v3))
            except OSError:
                continue
            except KeyboardInterrupt:
                break


if __name__ == "__main__":
    s = Planes()
    try:
        s.setup()
        s.run()
    except KeyboardInterrupt:
        s.clear()
