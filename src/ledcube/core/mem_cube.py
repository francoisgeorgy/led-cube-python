

class MemCube:
    def __init__(self, n):
        # Each face of the cube is an n x n matrix (initially zeros)
        self.n = n
        self.faces = [[[[0, 0, 0] for _ in range(n)] for _ in range(n)] for _ in range(6)]

    def set_pixel(self, face, row, col, color):
        """Set the value of a specific pixel"""
        self.faces[face][row][col] = [color.red, color.green, color.blue]

    def get_pixel(self, face, row, col):
        """Get the value of a specific pixel"""
        return tuple(self.faces[face][row][col])

    # def rotate_cube(self, axis, angle):
    #     """Rotate the entire cube around a given axis ('x', 'y', or 'z') by a specified angle"""
    #     radians = math.radians(angle)
    #     cos_angle = math.cos(radians)
    #     sin_angle = math.sin(radians)
    #
    #     new_faces = [[[[0, 0, 0] for _ in range(self.n)] for _ in range(self.n)] for _ in range(6)]
    #
    #     # Apply rotation to each pixel in the cube
    #     for face in range(6):
    #         for row in range(self.n):
    #             for col in range(self.n):
    #                 x, y, z = self._face_row_col_to_xyz(face, row, col)
    #
    #                 # Apply rotation based on the axis
    #                 if axis == 'x':
    #                     y, z = y * cos_angle - z * sin_angle, y * sin_angle + z * cos_angle
    #                 elif axis == 'y':
    #                     x, z = x * cos_angle + z * sin_angle, -x * sin_angle + z * cos_angle
    #                 else:  # 'z' axis
    #                     x, y = x * cos_angle - y * sin_angle, x * sin_angle + y * cos_angle
    #
    #                 new_face, new_row, new_col = self._xyz_to_face_row_col(x, y, z)
    #                 if new_face is not None:
    #                     new_faces[new_face][new_row][new_col] = self.faces[face][row][col]
    #
    #     self.faces = new_faces

    # def _face_row_col_to_xyz(self, face, row, col):
    #     """Convert face, row, col to x, y, z coordinates in 3D space"""
    #     # This is a simplified conversion assuming a unit cube centered at the origin
    #     # Further calculation is needed for a more accurate representation
    #     x = y = z = -1 + 2 * col / (self.n - 1) if face % 2 == 0 else 1 - 2 * row / (self.n - 1)
    #     if face == 0:   y = 1
    #     elif face == 1: y = -1
    #     elif face == 2: z = 1
    #     elif face == 3: z = -1
    #     elif face == 4: x = 1
    #     elif face == 5: x = -1
    #     return x, y, z
    #
    # def _xyz_to_face_row_col(self, x, y, z):
    #     """Convert x, y, z coordinates back to face, row, col"""
    #     # Identify the face based on the largest coordinate magnitude
    #     largest = max(abs(x), abs(y), abs(z))
    #     if largest == abs(x):
    #         face = 4 if x > 0 else 5
    #         row = int((1 - z) * (self.n - 1) / 2)
    #         col = int((y + 1) * (self.n - 1) / 2)
    #     elif largest == abs(y):
    #         face = 0 if y > 0 else 1
    #         row = int((1 - z) * (self.n - 1) / 2)
    #         col = int((x + 1) * (self.n - 1) / 2)
    #     elif largest == abs(z):
    #         face = 2 if z > 0 else 3
    #         row = int((1 - y) * (self.n - 1) / 2)
    #         col = int((x + 1) * (self.n - 1) / 2)
    #     else:
    #         return None, None, None
    #
    #     # Ensure the row and col are within bounds
    #     if 0 <= row < self.n and 0 <= col < self.n:
    #         return face, row, col
    #     else:
    #         return None, None, None
