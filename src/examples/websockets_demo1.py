import asyncio
import json
import os
import platform
import threading
import time
from enum import Enum
from math import copysign, sin, cos
from queue import Queue

import segno
import uvicorn
from fastapi import FastAPI, WebSocket

from ledcube.core import Face, rgb_graphics
from ledcube.core.color import Color
from ledcube.core.cube import Cube
from ledcube.core.mapper_matrix_to_cube import canvas_to_3d
from ledcube.core.remote import get_cube_ip
from ledcube.core.utils import normalize, rot_y, r2d, rot_x, reverse, load_font, get_orthonormal_basis_vectors, \
    map_to_panel
from ledcube.geometry.planes import intersection_plane_xy, OffLimitException, intersection_plane_xz, \
    intersection_plane_yz


"""Ensemble of small demos to show various capabilities of the Cube.
"""


app = FastAPI()
clients = set()  # web sockets clients


# def broadcast_message(message):
#     for connection in clients:
#         asyncio.run(connection.send_json({"message": message}))


fonts_text = (
    # '8pt_15_H.bdf',
    # 'Espy_Sans_Bold_14.bdf',
    # 'Espy_Sans_Bold_16.bdf',
    # 'Modern_12pt_10_H.bdf',
    # 'Modern_12pt_H.bdf',
    'Athens_18.bdf',
    'Classic_18pt_H.bdf',
    'Cory_24.bdf',
    'Courier_15.bdf',
    'Dwinelle_18.bdf',
    'Espy_Sans_16.bdf',
    'Geneva_24.bdf',
    'Helv (2).bdf',
    'MS_Sans_Serif_24.bdf',
    'Modern_12pt_H.bdf',
    'Modern_24pt_C.bdf',
    'New_York_18.bdf',
    'San_Francisco_18.bdf',
    'figlet-banner.bdf',
    'shaston-16.bdf',
    'spleen-32x64.bdf',
    'superpet-ascii.bdf',
    'swiss-36-ega.bdf',
    'swiss-36-vga.bdf'
)

fonts_symbols = (
    'Cairo_18.bdf',
    'Mobile_18.bdf'
)

class Command(Enum):
    RESET = 'reset'         # reset the cube
    STOP = 'stop'           # stop current task
    INIT = 'init'
    COLOR = 'color'


# currently implement commands :
valid_commands = (
    Command.RESET.value,
    Command.STOP.value,
    Command.INIT.value,
    Command.COLOR.value,
)

BORDER_COLOR = Color.BLUE()
AXES_COLOR = Color.ORANGE()

SHOW_AXES = True
SHOW_VECTOR = True
SHOW_ACCEL = False
SHOW_ACCEL_PANEL = True
SHOW_DOT = False
SHOW_DOT_SPEED = False

GRAVITY = 1
MAX_SPEED = 1   # absolute value
FILTER_ACC = False
INVERSE_X = False
ACC_VECTOR_FULL = True
ACCEL_ORIENTATION = [0, 1, 0]


class ThreadedApp(Cube):

    def __init__(self, message_callback):
        super().__init__()
        print("ThreadedApp __init__() start")
        self.message_callback = message_callback
        self.command_queue = Queue()
        self.current_task = None        # to keep track of the long running task
        self.running = True
        # the application starts itself:
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        print("ThreadedApp __init__() end")

    def demo_solid_color(self, r, g, b):
        self.canvas.Fill(r, g, b)
        self.refresh()

    def demo_gradient_color(self):
        self.clear()
        f = self.planes[Face.FRONT.value]
        for y in range(64):
            c = (63-y) * 255 / 63;
            self.planes[Face.FRONT.value].line(0, y, 63, y, Color(c, 0, 0))
            self.planes[Face.RIGHT.value].line(0, y, 63, y, Color(0, c, 0))
            self.planes[Face.LEFT.value].line(0, y, 63, y, Color(0, 0, c))
            self.planes[Face.BACK.value].line(0, y, 63, y, Color(c, c, c))
        self.refresh()

    def demo_gradient_color_gamma(self, gamma=None):
        self.clear()
        f = self.planes[Face.FRONT.value]
        for v in range(self.matrix.height):
            for u in range(self.matrix.width):
                x, y, z = canvas_to_3d(u, v)
                r = x+0.5
                g = y+0.5
                b = z+0.5
                c = Color(r * 255, g * 255, b * 255)
                if gamma is not None and gamma > 0.0:
                    c.gamma(gamma)
                    # gamma = .43
                    # r, g, b = r**(1/gamma), g**(1/gamma), b**(1/gamma)
                    # t = r + g + b
                    # if t < 0.000001:
                    #     r, g, b = 0, 0, 0
                    # else:
                    #     r = r / t
                    #     g = g / t
                    #     b = b / t
                    #     r, g, b = r**gamma, g**gamma, b**gamma
                self.pixel(u, v, c)
        self.refresh()

    def demo_text1(self):
        text = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        pyxis = 'PYXIS'
        # font = rgb_graphics.Font()
        # font.LoadFont(f'{fonts_path}/{filename}')
        self.clear()
        # self.canvas.Fill(0, 0, 60)
        w = 8
        h = 9
        k = 0
        j = 0
        for y in range(self.canvas.height//h + 1):
            for x in range(self.canvas.width//w):
                # write 'PYXIS' on line 3, starting at 2nd column:
                if 1 <= x <= len(pyxis) and y == 4:
                    letter = pyxis[j]
                    j = (j + 1) % len(pyxis)
                    color = Color.RED()
                else:
                    letter = text[k]
                    color = Color.WHITE()
                yy = y * h
                if yy < 64:
                    yy = yy - 1
                self.text(x*w + 1, yy, color, letter)
                k = (k + 1) % len(text)
        self.refresh()
        # while self.command_queue.empty():
        #     time.sleep(0.1)

    def demo_text2(self):
        fonts_path = f'{os.path.dirname(__file__)}/../../fonts'
        fonts = {}
        word = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        i = 0
        k = 0
        while self.command_queue.empty():
            self.clear()
            self.canvas.Fill(0, 0, 0)
            for face in Face:
                filename = fonts_text[k]
                if filename not in fonts:
                    fonts[filename] = rgb_graphics.Font()
                    fonts[filename].LoadFont(f'{fonts_path}/{filename}')
                c = word[(i+k) % len(word)]
                x = (64 - fonts[filename].CharacterWidth(ord(c))) // 2
                y = (64 - fonts[filename].height) // 2 + fonts[filename].baseline
                self.planes[face.value].text(x, reverse(y), Color.WHITE(), c, fonts[filename])
                k = (k + 1) % len(fonts_text)
            self.refresh()
            i = (i+1) % len(word)
            time.sleep(0.1)

    def demo_text_scroll(self, text='Bonjour'):
        # font = load_font('10x20.bdf')
        fonts_path = f'{os.path.dirname(__file__)}/../../fonts'
        font = rgb_graphics.Font()
        font.LoadFont(f'{fonts_path}/swiss-36-vga.bdf')
        h = 64 - int((64 - font.height) * 2)

        pos = self.canvas.width
        i = 0
        while self.command_queue.empty():
            r = (sin(i/100) + 1) / 2 * 255
            g = (cos(i/150) + 1) / 2 * 255
            b = (sin(i/50) + 1) / 2 * 255
            self.canvas.Clear()
            n = rgb_graphics.DrawText(self.canvas, font, pos, h, Color(r, g, b), text)
            pos -= 1
            if pos + n < 0:
                pos = self.canvas.width
            self.refresh()
            i = i + 1
            time.sleep(0.01)

    def demo_clock(self):
        #TODO
        pass

    def show_axes(self):
        # Copié de cubes_axes.py
        self.clear()
        f = load_font('6x9.bdf')
        for p in self.planes:
            p.border(BORDER_COLOR)
            p.draw_x_axis(AXES_COLOR, font=f)
            p.draw_y_axis(AXES_COLOR, font=f)
            p.draw_z_axis(AXES_COLOR, font=f)
            p.text(50, 50, Color.WHITE(), f'{p.get_label()}')
        self.refresh()

    def show_faces(self):
        # Copié de cubes_faces.py
        self.clear();
        f = load_font('10x20.bdf')
        for p in self.planes:
            p.text(26, 25, Color.YELLOW(), f'{p.get_label()}', f)
            # p.text(2, 50, Color.YELLOW(), f'{FACES_NAMES["default"][p.face]}')
            # p.text(2, 38, Color.YELLOW(), f'{FACES_NAMES["fr"][p.face]}')
            p.border(Color.ORANGE())
        self.refresh()

    def show_layout(self):
        # Copié de cube_layout.py
        self.clear();
        f1 = load_font('9x18.bdf')
        f2 = load_font('5x8.bdf')
        for p in self.planes:
            p.text(2, 50, Color.YELLOW(), f'{p.offset.x} {p.offset.y}', f1)
            p.text(2, 38, Color.YELLOW(), f'{p.get_name()}', f1)
            p.text(21, 10, Color.BLUE(), 'panel', f2)
            p.text(3, 2, Color.BLUE(), '___bottom___', f2)
            p.border(Color.ORANGE())
        self.refresh()

    def show_angles(self):
        # Copié de roll-pitch-angles.py
        p = self.planes[Face.FRONT.value]
        while self.command_queue.empty():
            self.clear()
            x, y, z = 0, 0, 0
            try:
                gx, gy, gz = self.imu.acceleration
                if FILTER_ACC:
                    gx = round(gx*10) / 10
                    gy = round(gy*10) / 10
                    gz = round(gz*10) / 10
                x = gx
                y = gy
                z = gz
            except OSError:
                continue
            vn = normalize([x, y, z])
            pitch = rot_y(vn)
            roll = rot_x(vn)
            color = Color.GREEN()
            p.text(4, 52, color, f'R {r2d(roll):>6.2f}')
            p.text(4, 42, color, f'P {r2d(pitch):>6.2f}')
            p.text(4, 4, color, f'X {x:>6.2f}')
            p.text(4, 14, color, f'Y {y:>6.2f}')
            p.text(4, 24, color, f'Z {z:>6.2f}')
            self.refresh()
            time.sleep(0.1)

    def show_planes(self):
        while self.command_queue.empty():
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
            except OSError:
                continue

    def draw_line(self, face, x0, y0, x1, y1, color):
        if 0 <= x0 <= 63 and 0 <= y0 <= 63 and 0 <= x1 <= 63 and 0 <= y1 <= 63:
            self.planes[face].line(x0, y0, x1, y1, color)

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

    def show_gravity(self):
        # copié de gravity-all-planes.py
        while self.command_queue.empty():
            self.clear()

            try:
                gx, gy, gz = self.imu.acceleration
                if FILTER_ACC:
                    gx = round(gx*10) / 10
                    gy = round(gy*10) / 10
                    gz = round(gz*10) / 10
                if INVERSE_X:
                    gx = -gx
            except OSError:
                continue

            # for i in [FRONT_PLANE]:
            # for i in [LEFT_PLANE, FRONT_PLANE, RIGHT_PLANE, BACK_PLANE, TOP_PLANE, BOTTOM_PLANE]:
            for face in Face:

                p = self.planes[face.value]
                p.text(57, 55, Color.BLUE(), p.get_label())

                # p.update_acceleration(gx, gy, -gz)  # why do we need -gz ???
                p.update_acceleration(gx, gy, gz)

                dx = 32 * p.ax
                dy = 32 * p.ay

                if SHOW_AXES:
                    # X acceleration
                    p.line(31, 31, 31 + dx, 31, Color.GREEN() if p.ax > 0 else Color.BLUE())
                    p.line(31, 32, 31 + dx, 32, Color.GREEN() if p.ax > 0 else Color.BLUE())

                    # Y acceleration
                    p.line(31, 32, 31, 31 + dy, Color.GREEN() if p.ay > 0 else Color.BLUE())
                    p.line(32, 32, 32, 31 + dy, Color.GREEN() if p.ay > 0 else Color.BLUE())

                    # Z acceleration
                    # p.circle(31, 31, 16 * abs(p.vz), Color.GREEN() if p.vz > 0 else Color.BLUE())

                # XY vector
                if SHOW_VECTOR:
                    if ACC_VECTOR_FULL:
                        # not proportional, up to the panel border
                        if dx == 0:
                            x = 0
                            y = 32 * copysign(1, dy)
                        else:
                            slope = dy / dx
                            x = 32 * copysign(1, dx)
                            y = slope * x
                            if abs(y) > 32:
                                y = 32 * copysign(1, dy)
                                x = int(y / slope)
                        p.line(31, 31, 31 + x, 31 + y, Color.RED())
                    else:
                        p.line(31, 31, 31 + dx, 31 + dy, Color.RED())

                if SHOW_ACCEL:
                    # IMU :
                    p.text(1, 54, Color.GREEN(), f"{gx:4}")
                    p.text(1, 45, Color.GREEN(), f"{gy:4}")
                    p.text(1, 36, Color.GREEN(), f"{gz:4}")
                if SHOW_ACCEL_PANEL:
                    # Plane (panel) coords :
                    axt = int(p.ax*100)
                    ayt = int(p.ay*100)
                    # azt = int(p.az*100)
                    p.text(1, 10, Color.RED(), f"{axt:4}")
                    p.text(1, 1, Color.RED(), f"{ayt:4}")
                    # p.text(1,  1, Color.RED(), f"{azt:4}")

            self.refresh()
            time.sleep(0.1)

    def show_infos(self):
        """
        Max Size = 32
        32 = 17 + (Version Number × 4)
        Version Number = (32 − 17) / 4
        :param data:
        :return:
        """
        ip = get_cube_ip()
        hostname = platform.node().split('.')[0]
        a = ip.split('.')

        qr = segno.make_qr(f"http://{ip}:5040/", version=2)

        # Convert QR code to a binary matrix
        qr_matrix = []
        for row in qr.matrix_iter(scale=2):
            qr_matrix.append([col == 0x1 for col in row])

        c = Color.WHITE()
        while self.command_queue.empty():
            self.clear()
            y = 0
            for row in qr_matrix:
                x = 0
                for col in row:
                    if col:
                        self.planes[Face.FRONT.value].pixel(x, reverse(y), c)
                        self.planes[Face.RIGHT.value].pixel(x, reverse(y), c)
                        self.planes[Face.BACK.value].pixel(x, reverse(y), c)
                        self.planes[Face.LEFT.value].pixel(x, reverse(y), c)
                    x = x + 1
                y = y + 1

            uptime_h = int(time.monotonic() // 3600)
            uptime_m = (int(time.monotonic()) % 3600) // 60
            uptime_s = int(time.monotonic()) % 60

            # self.planes[Face.TOP.value].text(3, 52, Color.GREY(), hostname)
            self.planes[Face.TOP.value].text(3, 52, Color.GREY(), f'{a[0]}.{a[1]}.')
            self.planes[Face.TOP.value].text(3, 42, Color.GREY(), f'{a[2]}.{a[3]}')
            self.planes[Face.TOP.value].text(3, 32, Color.GREY(), f':5040')
            self.planes[Face.TOP.value].text(2, 2, Color.GREY(), f'{uptime_h:02}:{uptime_m:02}:{uptime_s:02}')
            self.refresh()

    def run(self):
        self.setup()
        self.clear()
        self.refresh()
        while self.running:
            command, params = self.command_queue.get()
            if command == Command.RESET.value:
                self.clear()
            elif command == 'demo_color':
                self.demo_solid_color(params['r'], params['g'], params['b'])
            elif command == 'demo_gradient':
                self.demo_gradient_color()
            elif command == 'demo_gradient3d':
                self.demo_gradient_color_gamma(params['gamma'] if params else None)
            elif command == 'demo_text1':
                self.demo_text1()
            elif command == 'demo_text2':
                self.demo_text2()
            elif command == 'demo_text_scroll':
                self.demo_text_scroll('Bienvenue chez Pyxis')
            elif command == 'show_faces':
                self.show_faces()
            elif command == 'show_axes':
                self.show_axes()
            elif command == 'show_layout':
                self.show_layout()
            elif command == 'show_angles':
                self.show_angles()
            elif command == 'show_planes':
                self.show_planes()
            elif command == 'show_gravity':
                self.show_gravity()
            elif command == 'show_infos':
                self.show_infos()
            else:
                print("run: invalid command")

    def enqueue_command(self, command, args=()):
        self.command_queue.put((command, args))

    def stop(self):
        self.running = False
        self.thread.join()
        if self.current_task is not None and self.current_task.is_alive():
            self.current_task.join()  # Wait for the current task to finish


def broadcast_message(message):
    for connection in clients:
        asyncio.run(connection.send_json({"message": message}))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            # Handle incoming message
            m = json.loads(message)
            cube_app.enqueue_command(m['command'], m['parameters'] if 'parameters' in m else ())
    except Exception as e:
        print("websocket_endpoint Exception", e)
    finally:
        clients.remove(websocket)


if __name__ == "__main__":
    cube_app = ThreadedApp(message_callback=broadcast_message)
    # The cub_app.run() method is called in the cube_app constructor.
    # host_ip = get_cube_ip()
    host_ip = '0.0.0.0'
    uvicorn.run(app, host=f'{host_ip}', port=5041)
