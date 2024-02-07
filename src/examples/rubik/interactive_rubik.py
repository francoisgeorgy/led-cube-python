import asyncio

from fastapi import FastAPI
import uvicorn
from fastapi import FastAPI, Response, status, WebSocket, WebSocketDisconnect

from ledcube.core.remote import get_cube_ip
from examples.rubik.rubik import Rubik
from examples.rubik.cubie.Move import Move
from examples.rubik.utils import rubik_faces

"""Interactive rubik cube with embedded web server.

replaced by ws_rubik

    API

    /rubik
        /face/<face>
        /face/<face>/action
        /<action>
        
"""

rub = Rubik()
rub.setup()
rub.reset_cube()

app = FastAPI()
clients = set()     # web sockets clients

msg_from_cube = ""


@app.get("/representation")
async def representation():
    return {"state": rub.get_representation()}


@app.get("/state")
async def state():
    return {"state": rub.get_representation()}


@app.get(
    "/init/colors/{state}",
    summary="Init the cube from a string representing the color positions.",
    description="The state string format is UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB")
async def state(state: str):
    rub.init_from_colors(state)
    return {"result": "init done"}


@app.get(
    "/init/faces/{state}",
    summary="Init the cube from a string representing the faces positions.",
    description="The state string format is UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
)
async def state(state: str):
    rub.init_from_faces(state)
    return {"result": "init done"}


@app.get("/test")
async def test():
    global m
    rub.selected_face = 'U'
    rub.redraw_cube()
    rub.selected_slice = None
    rub.selected_face = None
    m = Move('U')
    m.clockwise = True
    rub.move_cube(m)
    return {"status": "test done"}


@app.get("/face/{face}")
async def test(face: str, response: Response):
    if face.upper() not in rubik_faces:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "invalid face"}
    rub.toggle_face(face.upper())
    rub.redraw_cube()
    return {"status": f"face {face.upper()} selected"}


@app.get("/cw")
async def cw():
    rub.move_selection('cw')
    return {"status": "CW"}


@app.get("/ccw")
async def ccw():
    rub.move_selection('ccw')
    return {"status": "CCW"}


@app.get("/180")
async def cw180():
    rub.move_selection('180')
    return {"status": "180"}


# TODO: replace /cw, /ccw amd /180 by a /move/<movement> entry.

@app.get("/shuffle")
async def scramble():
    rub.shuffle_cube()
    return {"status": "cube shuffled"}


@app.get("/reset")
async def reset():
    rub.reset_cube()
    return {"status": "cube reset"}


@app.get("/solve")
async def solve():
    rub.auto_solve(solve_callback)
    return {"status": "cube solving"}


async def broadcast(message):
    print("enter broadcast")
    for client in clients:
        print("broadcast to client", client)
        await client.send_json(message)


def solve_callback(message):
    global msg_from_cube
    print("solve_callback", message)
    msg_from_cube = message
    # await broadcast(message)


async def cube_state_task():
    # global counter
    while True:
        await asyncio.sleep(1)
        # counter += 1
        await broadcast({"message": msg_from_cube})


@app.on_event("startup")
async def on_startup():
    asyncio.create_task(cube_state_task())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # global counter
    await websocket.accept()
    print("add client")
    clients.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "reset":
                # counter = 0
                await broadcast({"message": "-"})
    except WebSocketDisconnect:
        clients.remove(websocket)


if __name__ == "__main__":
    host_ip = get_cube_ip()
    uvicorn.run(app, host=f'{host_ip}', port=5042)
