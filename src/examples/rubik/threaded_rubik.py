import logging
import threading
from enum import Enum
from queue import Queue

from examples.rubik.rubik import Rubik
from examples.rubik.utils import rubik_faces


class Command(Enum):
    RESET = 'reset'         # reset the cube
    SHUFFLE = 'shuffle'     # shuffle/scramble the cube
    SCRAMBLE = 'scramble'   # same as shuffle
    SOLVE = 'solve'         # start auto-solve
    STOP = 'stop'           # stop current task
    FACE = 'face'           # select a face; arg is one of ['U', 'D', 'L', 'G', 'F', 'B']
    MOVE = 'move'           # move the selected face; arg is one of ['cw', 'ccw', or '180']
    INIT = 'init'           # init from a string (auto-detect format)
    STATE = 'state'         # return the cube representation
    HINT = 'hint'           # show which face to rotate next
    NAMES = 'names'         # toggle face name display

# TODO: add "cube" and slices to the list of selectables and the targets of movement.


# currently implement commands :
# TODO: implement INIT
valid_commands = (
    Command.FACE.value,
    Command.MOVE.value,
    Command.NAMES.value,
    Command.RESET.value,
    Command.SCRAMBLE.value,
    Command.SHUFFLE.value,
    Command.SOLVE.value,
    Command.STOP.value
)


class ThreadedRubik(Rubik):

    def __init__(self, message_callback):
        super().__init__(message_callback)
        self.command_queue = Queue()
        self.current_task = None        # to keep track of the long running task
        self.running = True
        # the application starts itself:
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def run(self):
        logging.debug("run()")
        while self.running:
            command, parameters = self.command_queue.get()
            logging.info(f'run: received command [{command}] with parameters [{parameters}]')
            busy = self.current_task is not None and self.current_task.is_alive()

            # if self.current_task is None or not self.current_task.is_alive():
            if busy and command == Command.STOP.value:
                logging.debug("run: put stop command into task_commands")
                self.task_commands.put(Command.STOP.value)
                # if self.current_task is not None and self.current_task.is_alive():
                #     self.current_task.join()  # Wait for the current task to finish
            elif busy:
                logging.debug("run: busy, command ignored")
            else:

                if command == Command.RESET.value:
                    self.reset_cube()

                elif command == Command.SHUFFLE.value or command == Command.SCRAMBLE.value:
                    self.shuffle_cube()

                elif command == Command.FACE.value:
                    if isinstance(parameters, str):
                        face = parameters.upper()
                        if face not in rubik_faces:
                            # response.status_code = status.HTTP_400_BAD_REQUEST
                            # return {"error": "invalid face"}
                            # TODO: signal an error
                            pass
                        self.toggle_face(face)
                        self.redraw_cube()
                    else:
                        # TODO: signal an error
                        pass

                elif command == Command.MOVE.value:
                    if isinstance(parameters, str):
                        self.move_selection(parameters)
                    else:
                        # TODO: signal an error
                        pass

                elif command == Command.NAMES.value:
                    self.names()

                elif command == Command.SOLVE.value:
                    self.auto_solve()

                else:
                    logging.debug("        run: invalid command")

            # logging.debug("    run: command executed")

    def enqueue_command(self, command, args=()):
        logging.debug("enqueue_command", command)
        # self.command_queue.put((command, args))
        if command == Command.STOP.value:
            # we need to handle the stop command here because the run() method
            # is maybe be busy running auto_solve().
            logging.debug("enqueue_command: put stop command into task_commands")
            self.task_commands.put(Command.STOP.value)
        else:
            self.command_queue.put((command, args))

    def stop(self):
        self.running = False
        self.thread.join()
        if self.current_task is not None and self.current_task.is_alive():
            self.current_task.join()  # Wait for the current task to finish
        # Any other cleanup
