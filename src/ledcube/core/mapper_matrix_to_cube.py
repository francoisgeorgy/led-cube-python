
"""
    Shader coordinate system
    ------------------------
    
    https://learnopengl.com/Getting-started/Coordinate-Systems
    
    By convention, OpenGL is a right-handed system. What this basically says is that 
    the positive x-axis is to your right, the positive y-axis is up and 
    the positive z-axis is backwards. 
    Think of your screen being the center of the 3 axes and the positive z-axis going through your screen towards you.
    
    Also : https://blogs.oregonstate.edu/learnfromscratch/2021/10/05/understanding-various-coordinate-systems-in-opengl/ 
    
    OpenGL requires x, y, z coordinates of vertices ranging from -1.0 to 1.0 in order to show up on the screen.
    
    Convention choosen and used for the LED Cube
    ============================================
    
    The cube is a **unit cube**, with side length of 1 unit.
    
    The center of the cube is 0, 0, 0. 
    
    The x, y, z range is -0.5 to 0.5.
     
    The cube will use a Right-Handed Coordinate System:

        X-Axis: Horizontal, pointing to the right.
        Y-Axis: Vertical, pointing upwards.
        Z-Axis: Depth, pointing out of the screen (towards the viewer).        
    
    For a unit cube centered at the origin (0,0,0) in a right-handed coordinate system, 
    the vertices can be determined by considering each axis ranging from −0.5 to +0.5. 
    The cube will have 8 vertices, with each vertex represented by a combination of these 
    values along the X, Y, and Z axes.
    
    Here are the coordinates of the vertices:
    
    1. **Front Face**  (Z = +0.5, facing the viewer):

    - Top Right: (+0.5,+0.5,+0.5)
    - Top Left: (−0.5,+0.5,+0.5)
    - Bottom Right: (+0.5,−0.5,+0.5)
    - Bottom Left: (−0.5,−0.5,+0.5)

    2. **Back Face**  (Z = -0.5, away from the viewer):

    - Top Right: (+0.5,+0.5,−0.5)
    - Top Left: (−0.5,+0.5,−0.5)
    - Bottom Right: (+0.5,−0.5,−0.5)
    - Bottom Left: (−0.5,−0.5,−0.5)

    3. **Top Face**  (Y = +0.5):

    - Front Right: (+0.5,+0.5,+0.5)
    - Front Left: (−0.5,+0.5,+0.5)
    - Back Right: (+0.5,+0.5,−0.5)
    - Back Left: (−0.5,+0.5,−0.5)

    4. **Bottom Face**  (Y = -0.5):

    - Front Right: (+0.5,−0.5,+0.5)
    - Front Left: (−0.5,−0.5,+0.5)
    - Back Right: (+0.5,−0.5,−0.5)
    - Back Left: (−0.5,−0.5,−0.5)

    5. **Right Face**  (X = +0.5):

    - Top Front: (+0.5,+0.5,+0.5)
    - Top Back: (+0.5,+0.5,−0.5)
    - Bottom Front: (+0.5,−0.5,+0.5)
    - Bottom Back: (+0.5,−0.5,−0.5)

    6. **Left Face**  (X = -0.5):
    
    - Top Front: (−0.5,+0.5,+0.5)
    - Top Back: (−0.5,+0.5,−0.5)
    - Bottom Front: (−0.5,−0.5,+0.5)
    - Bottom Back: (−0.5,−0.5,−0.5)

   Shader XY origin is at lower-left. See https://registry.khronos.org/OpenGL-Refpages/gl4/html/gl_FragCoord.xhtml

"""


def canvas_to_3d(x0, y0):
    """Return a 3D coord (x, y, z) from a canvas (x, y) coord.

    The mapping is from the logical coordinates to 3D coord.

    Logical coordinates of the canvas :
    ┌──────┬──────┬──────┬──────┐
    │0,0   │64,0  │128,0 │192,0 │
    │Front │Right │Back  │Left  │
    ├──────┼──────┼──────┴──────┘
    │0,64  │64,64 │
    │Top   │Bottom│
    └──────┴──────┘

    (0, 0) is the upper left corner of a panel.

    The returned coordinates are in the range of (-.5, .5).
    """
    x = x0  # + 0.5   # +0.5 in order to put the middle on a pixel instead of between pixels
    y = y0  # + 0.5
    cx, cy, cz = 0, 0, 0

    if y >= 128:
        cx, cy, cz = 0, 0, 0        # coord outside the canvas are mapped to (0, 0, 0)
    elif y >= 64:
        if x >= 128:
            return 0, 0, 0
        elif x >= 64:
            # BOTTOM
            cx = (x - 64) / 63 - 0.5
            cy = -0.5
            cz = 1 - (y - 64) / 63 - 0.5
        else:
            # TOP
            cx = x / 63 - 0.5
            cy = 0.5
            cz = (y - 64) / 63 - 0.5
    else:
        if x >= 192:
            # LEFT
            cx = -0.5
            cy = 1 - y / 63 - 0.5
            cz = (x - 192) / 63 - 0.5
        elif x >= 128:
            # BACK
            cx = 1 - (x - 128) / 63 - 0.5
            cy = 1 - y / 63 - 0.5
            cz = -0.5
        elif x >= 64:
            # RIGHT
            cx = 0.5
            cy = 1 - y / 63 - 0.5
            cz = 1 - (x - 64) / 63 - 0.5
        else:
            # FRONT
            cx = x / 63 - 0.5
            cy = 1 - y / 63 - 0.5
            cz = 0.5
    return cx, cy, cz


# def canvas_to_3d(x0, y0):
#     """Return a 3D coord (x, y, z) from a canvas (x, y) coord.
#
#     (0, 0) is the upper left corner of a panel.
#     """
#     x = x0 + 0.5   # +0.5 in order to put the middle on a pixel instead of between pixels
#     y = y0 + 0.5
#     cx, cy, cz = 0, 0, 0
#
#     if y >= 128:
#         cx, cy, cz = 0, 0, 0
#     elif y >= 64:
#         if x >= 128:
#             return 0, 0, 0
#         elif x >= 64:
#             # BOTTOM
#             cx = (x - 64) / 63.5 - 0.5
#             cy = -0.5
#             cz = 1 - (y - 64) / 63.5 - 0.5
#         else:
#             # TOP
#             cx = x / 63.5 - 0.5
#             cy = 0.5
#             cz = (y - 64) / 63.5 - 0.5
#     else:
#         if x >= 192:
#             # LEFT
#             cx = -0.5
#             cy = 1 - y / 63.5 - 0.5
#             cz = (x - 192) / 63.5 - 0.5
#         elif x >= 128:
#             # BACK
#             cx = 1 - (x - 128) / 63.5 - 0.5
#             cy = 1 - y / 63.5 - 0.5
#             cz = -0.5
#         elif x >= 64:
#             # RIGHT
#             cx = 0.5
#             cy = 1 - y / 63.5 - 0.5
#             cz = 1 - (x - 64) / 63.5 - 0.5
#         else:
#             # FRONT
#             cx = x / 63.5 - 0.5
#             cy = 1 - y / 63.5 - 0.5
#             cz = 0.5
#     return cx, cy, cz
    # map to range of (-0.5, 0.5) :
    # return cx - 0.5, cy - 0.5, cz - 0.5


# def physical_canvas_to_3d(x0, y0):
#     """Return a 3D coord (x, y, z) from a canvas (x, y) coord.
#     """
#     # TODO : check
#     x = x0 + 0.5    # +0.5 in order to put the middle on a pixel instead of between pixels
#     y = y0 + 0.5
#     cx, cy, cz = 0, 0, 0
#     if x < 64 and y < 64:
#         # LEFT
#         cx = 0
#         cy = 1 - x / 64
#         cz = y / 64
#     elif x < 64 and y < 128:
#         # BOTTOM
#         # cx = 1 - (x / 64)
#         # cy = 1 - (y - 64) / 64
#         cx = (x / 64)
#         cy = (y - 64) / 64
#         # cz = 0
#         cz = 1
#     elif x < 128 and y < 64:
#         # FRONT
#         cx = (x - 64) / 64
#         cy = 0
#         cz = y / 64
#     elif x < 128 and y < 128:
#         # BACK
#         cx = 1 - (x - 64) / 64
#         cy = 1
#         cz = (y - 64) / 64
#     elif x < 192 and y < 64:
#         # RIGHT
#         cx = 1
#         cy = (x - 128) / 64
#         cz = y / 64
#     elif x < 192 and y < 128:
#         # TOP
#         # cx = 1 - (x - 128) / 64
#         cx = (x - 128) / 64
#         # cy = (y - 64) / 64
#         cy = 1 - (y - 64) / 64
#         # cz = 1
#         cz = 0
#     # map to range of (-0.5, 0.5) :
#     return cx - 0.5, cy - 0.5, cz - 0.5
#
#
# def canvas_from_3d(x, y, z):
#     """Return a tuple (face, x, y) from a 3D coord (x, y, z)
#     """
#     # TODO
#     pass
