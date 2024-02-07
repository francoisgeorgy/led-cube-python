import importlib
import math
import os
import sys
import time

from ledcube.core.color import Color
from ledcube.core.cube import Cube
from ledcube.core.mapper_matrix_to_cube import canvas_to_3d

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
"""

# https://stackoverflow.com/questions/46695726/generating-pure-colors-of-equal-brightness-for-display-on-leds

# Usage : python src/examples/shaders/shader.py -c 4 -P 3 --shader src/examples/shaders/rgbt.py


def load_module_from_path(path):
    module_name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None:
        raise ImportError(f"Cannot load module from {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Shader(Cube):

    def __init__(self):
        super().__init__()

        # Add additional command line options :
        self.parser.add_argument("shader", help="The shader script", type=str)

    def run(self):

        if not self.args.shader:
            print("ERROR: shader script missing")
            sys.exit(0)

        mod = load_module_from_path(self.args.shader)

        # shader_script = os.path.splitext(self.args.shader)[0]   # remove extension if any
        # mod = __import__(shader_script, fromlist=["shader"])

        t = 0
        while True:
            self.canvas.Clear()
            for v in range(64):
                for u in range(4 * 64):
                    # print(u, v)
                    r, g, b = mod.shader(*canvas_to_3d(u, v), t)
                    # r, g, b = shader_rgb_t(*canvas_to_3d(u, v), t)
                    self.pixel(u, v, Color(r * 255, g * 255, b * 255))
            for v in range(64, 128):
                for u in range(128):
                    # r, g, b = shader_rgb_t(*canvas_to_3d(u, v), t)
                    r, g, b = mod.shader(*canvas_to_3d(u, v), t)
                    self.pixel(u, v, Color(r * 255, g * 255, b * 255))
            # for v in range(self.matrix.height):
            #     for u in range(self.matrix.width):
            #         r, g, b = shader_rgb(*canvas_to_3d(u, v))
            #         self.pixel(u, v, Color(r * 255, g * 255, b * 255))
            #         return
            # self.pixel(u, v, Color(((r * 255) + i) % 256, ((g * 255) + i) % 256, ((b * 255) + i) % 256))
            # print(i, ((r * 255) + i) % 256)
            # i = (i+1) % 256
            t = t + 1
            self.refresh()


if __name__ == "__main__":
    s = Shader()
    try:
        s.setup()
        s.run()
    except KeyboardInterrupt:
        print("bye\n")
        s.clear()
