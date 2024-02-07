import asyncio
import json
import logging
import sys

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketException

from ledcube.core import running_on_pi
from ledcube.core.remote import get_cube_ip
from examples.rubik.threaded_rubik import ThreadedRubik, valid_commands

"""Interactive rubik cube with embedded web server.
"""

clients = set()     # web sockets clients
app = FastAPI()

verbose = False

# We force the config of the logging backend because it may have already been setup
# by the wsgi server.
# TODO: understand and solve the logging config
logging.basicConfig(stream=sys.stdout,
                    level=logging.DEBUG if verbose else logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    force=True)


def broadcast_message(message):
    for connection in clients:
        asyncio.run(connection.send_json({"message": message}))


if running_on_pi:
    sys.argv += ["--led-chain", "3", "--led-parallel", "2", "--led-brightness", "60", "--led-slowdown-gpio", "5"]
else:
    sys.argv += ["--led-chain", "4", "--led-parallel", "3", "--led-brightness", "100"]


rub = ThreadedRubik(message_callback=broadcast_message)
rub.setup()         # TODO or FIXME: move .setup() into .run()
rub.reset_cube()    # TODO or FIXME: move .setup() into .run()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    try:
        # The primary function of this loop is to keep the WebSocket connection open. Without this loop, the connection
        # would close immediately after being established. The await websocket.receive_text() call waits for a message
        # from the client, keeping the connection alive.
        while True:
            logging.debug("waiting for a command")
            message = await websocket.receive_text()
            m = json.loads(message)
            logging.debug("message received:", message, m)
            if m['command'] in valid_commands:
                logging.debug("enqueue command", m['command'], m['parameters'] if 'parameters' in m else ())
                rub.enqueue_command(m['command'], m['parameters'] if 'parameters' in m else ())
                # await websocket.send_json({"message": "ERR!"})
            else:
                logging.warning("invalid command", m['command'])
                await websocket.send_json({"message": f"invalid command: {m['command']}"})

    except Exception as e:
        # https://www.rfc-editor.org/rfc/rfc6455#section-7.4.1
        logging.debug("websocket_endpoint Exception", e)
    finally:
        clients.remove(websocket)


if __name__ == "__main__":
    # host_ip = get_cube_ip()
    host_ip = '0.0.0.0'
    uvicorn.run(app, host=f'{host_ip}', port=5041)
