import asyncio
import json
import threading
import time
from queue import Queue

import board
import uvicorn
from fastapi import FastAPI, WebSocket

from ledcube.core.remote import get_cube_ip
from ledcube.imu import lis3dh_basic

"""Example how to use websockets.
"""

# if running_on_pi:
#     sys.argv += ["--led-chain", "3", "--led-parallel", "2", "--led-brightness", "60", "--led-slowdown-gpio", "5"]
# else:
#     sys.argv += ["--led-chain", "4", "--led-parallel", "3", "--led-brightness", "100"]

app = FastAPI()
clients = set()  # web sockets clients


class ThreadedApp:

    def __init__(self, message_callback):
        # super().__init__(message_callback)
        print("ThreadedApp __init__() start")
        self.message_callback = message_callback
        self.command_queue = Queue()
        self.current_task = None        # to keep track of the long running task
        self.running = True

        # i2c = busio.I2C(board.SCL, board.SDA)
        i2c = board.I2C()  # uses board.SCL and board.SDA
        self.imu = lis3dh_basic.LIS3DH_I2C(i2c, address=0x18)
        self.imu.range = lis3dh_basic.RANGE_2_G
        # imu.align(ACCEL_ORIENTATION)
        self.imu.use_offset = False

        # the application starts itself:
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        print("ThreadedApp __init__() end")

    def clear(self):
        pass

    def run(self):
        while self.running:
            try:
                x, y, z = self.imu.acceleration
                self.message_callback(json.dumps({'x': x, 'y': y, 'z': z}))
                time.sleep(0.1)
            except OSError:
                pass

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
            # cube_app.enqueue_command(m['command'], m['parameters'] if 'parameters' in m else ())

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
