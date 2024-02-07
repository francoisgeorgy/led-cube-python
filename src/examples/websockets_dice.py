import asyncio
import json
import threading
import random
import time
from enum import Enum
from queue import Queue

import uvicorn
from fastapi import FastAPI, WebSocket

from ledcube.core import Face
from ledcube.core.color import Color
from ledcube.core.cube import Cube


"""Ensemble of small demos to show various capabilities of the Cube.
"""


DICE_MIN = 1
DICE_MAX = 6
ROLLS = 10      # rolls n times before showing the result
DELAY = 180     # ms between rolls

# Mapping of dice number to dot indices
NUMBER_TO_DOTS = {
    1: [3],
    2: [0, 6],
    3: [1, 3, 5],
    4: [0, 1, 5, 6],
    5: [0, 1, 3, 5, 6],
    6: [0, 1, 2, 4, 5, 6]
}

#
#   O   O       0   1
#   O O O  ==>  2 3 4
#   O   O       5   6
#
# Constants for dot positions
DOT_RADIUS = 7
DOT_POSITION_START = 12
DOT_POSITION_MIDDLE = 31
DOT_POSITION_END = 50


def calculate_dot_positions(start, middle, end):
    return [
        [start, start], [end, start],
        [start, middle], [middle, middle], [end, middle],
        [start, end], [end, end]
    ]


# Dot positions
dot_positions = calculate_dot_positions(DOT_POSITION_START, DOT_POSITION_MIDDLE, DOT_POSITION_END)


app = FastAPI()
clients = set()  # web sockets clients


# def broadcast_message(message):
#     for connection in clients:
#         asyncio.run(connection.send_json({"message": message}))


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


class ThreadedApp(Cube):

    def __init__(self, message_callback):
        super().__init__()
        print("ThreadedApp __init__() start")
        self.message_callback = message_callback
        self.command_queue = Queue()
        self.current_task = None        # to keep track of the long running task

        self.dice_color = Color(200, 0, 0)
        self.dots_color = Color(255, 255, 255)
        self.dots_border_color = None   # Color(150, 150, 150)
        # Mapping of top values to the clockwise sequence of the four vertical sides for a right-handed dice.
        self.vertical_sides_mapping = {
            1: [2, 3, 5, 4],  # 1 on top
            2: [6, 3, 1, 4],  # 2 on top, and so on...
            3: [2, 6, 5, 1],
            4: [2, 1, 5, 6],
            5: [1, 3, 6, 4],
            6: [2, 4, 5, 3]
        }
        self.top_value = 6
        self.running = True
        # the application starts itself:
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def draw_face(self, face, value, border_color=None, label=False):
        if not 1 <= value <= 6:
            raise ValueError("Dice value must be between 1 and 6")
        p = self.planes[face.value]
        if border_color:
            p.border(border_color)
        if label:
            p.text(29, 8, Color.WHITE(), f'{value}')
        for dot_index in NUMBER_TO_DOTS[value]:
            x, y = dot_positions[dot_index]
            p.fill_circle(x, y, DOT_RADIUS, self.dots_color)
            if self.dots_border_color:
                p.circle(x, y, DOT_RADIUS, self.dots_border_color)

    def draw_dice(self):
        bottom_value = 7 - self.top_value
        vertical_sides = self.vertical_sides_mapping[self.top_value]
        self.canvas.Clear()
        self.canvas.Fill(*self.dice_color.to_tuple())
        self.draw_face(Face.TOP, self.top_value)
        self.draw_face(Face.BOTTOM, bottom_value)
        self.draw_face(Face.FRONT, vertical_sides[0])
        self.draw_face(Face.RIGHT, vertical_sides[1])
        self.draw_face(Face.BACK, vertical_sides[2])
        self.draw_face(Face.LEFT, vertical_sides[3])
        self.refresh()

    def set_dice(self, top_value):
        self.top_value = top_value
        self.draw_dice()

    def throw_dice(self, rolls):
        last_n = -1
        n = last_n
        for r in range(rolls):
            while n == last_n:
                n = random.randint(1, 6)
            last_n = n
            self.set_dice(n)
            time.sleep(DELAY / 1000)

    def set_dice_color(self, r, g, b):
        self.dice_color = Color(r, g, b)
        self.draw_dice()

    def set_dots_color(self, r, g, b):
        self.dots_color = Color(r, g, b)
        self.draw_dice()

    def run(self):
        self.setup()
        self.clear()
        # self.throw_dice(10)
        self.set_dice(6)
        # TODO: add shake detection
        # while True:
        #     if self.imu.shake():
        #         self.throw_dice(6)
        #     time.sleep(0.1)
        self.refresh()
        while self.running:
            command, params = self.command_queue.get()
            if command == Command.RESET.value:
                self.clear()
            elif command == 'dice_throw':
                self.throw_dice(10)
            elif command == 'dice_color':
                self.set_dice_color(params['r'], params['g'], params['b'])
            elif command == 'dots_color':
                self.set_dots_color(params['r'], params['g'], params['b'])
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
