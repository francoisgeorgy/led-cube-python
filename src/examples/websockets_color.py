import asyncio
import json
import threading
from enum import Enum
from queue import Queue
import random

import uvicorn
from fastapi import FastAPI, Response, status, WebSocket, WebSocketDisconnect

from ledcube.core.cube import Cube
from ledcube.core.remote import get_cube_ip

"""Example how to use websockets.
"""

# if running_on_pi:
#     sys.argv += ["--led-chain", "3", "--led-parallel", "2", "--led-brightness", "60", "--led-slowdown-gpio", "5"]
# else:
#     sys.argv += ["--led-chain", "4", "--led-parallel", "3", "--led-brightness", "100"]

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
        self.running = True
        # the application starts itself:
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        print("ThreadedApp __init__() end")

    def set_color(self, color):
        # ...
        print("set_color", color)
        self.refresh()

    def run(self):

        print("ThreadedApp run()")

        self.setup()

        self.canvas.Fill(20, 40, 60)
        self.refresh()

        print("enter running")
        while self.running:
            # print("waiting for command")
            # self.message_callback("waiting for command")

            # debug
            # if self.command_queue.empty():
            # print("command queue empty")
            # self.message_callback(f"hello from colors")
            # continue

            command, params = self.command_queue.get()
            print(f"run: command: {command}, params: {params}")
            if command == Command.RESET.value:
                self.clear()
            elif command == Command.COLOR.value:
                r, g, b = (params['r'], params['g'], params['b'])
                print("run: set color to", r, g, b)
                self.canvas.Fill(r, g, b)
                self.refresh()

            elif command == 'cmd1':
                # color = (random.randint(10, 255), random.randint(10, 255), random.randint(10, 255))
                self.canvas.Fill(random.randint(10, 255), random.randint(10, 255), random.randint(10, 255))
                self.refresh()
            else:
                print("run: invalid command")

    def enqueue_command(self, command, args=()):
        print("enqueue_command", command)
        self.command_queue.put((command, args))

    def stop(self):
        self.running = False
        self.thread.join()
        if self.current_task is not None and self.current_task.is_alive():
            self.current_task.join()  # Wait for the current task to finish
        # Any other cleanup


def broadcast_message(message):
    for connection in clients:
        asyncio.run(connection.send_json({"message": message}))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    try:
        # The primary function of this loop is to keep the WebSocket connection open. Without this loop, the connection
        # would close immediately after being established. The await websocket.receive_text() call waits for a message
        # from the client, keeping the connection alive.
        while True:
            message = await websocket.receive_text()
            # Handle incoming message
            m = json.loads(message)
            print("received text", message, m)

            # debug:
            cube_app.enqueue_command(m['command'], m['parameters'] if 'parameters' in m else ())

            # if m['command'] in valid_commands:
            #     cube_app.enqueue_command(m['command'], m['parameters'] if 'parameters' in m else ())
            # else:
            #     print("invalid command", m['command'])
    except Exception as e:
        # https://www.rfc-editor.org/rfc/rfc6455#section-7.4.1
        print("websocket_endpoint Exception", e)
    finally:
        clients.remove(websocket)


if __name__ == "__main__":
    cube_app = ThreadedApp(message_callback=broadcast_message)
    # The cub_app.run() method is called in the cube_app constructor.
    host_ip = get_cube_ip()
    uvicorn.run(app, host=f'{host_ip}', port=5041)
