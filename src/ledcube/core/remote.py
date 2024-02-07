import ifaddr
from enum import Enum


class RemoteCmd(Enum):
    # NONE = 0
    QUIT = 1
    CANCEL = 2      # e.g. cancel last action
    RUBIK_SELECT_FACE = 10
    RUBIK_SELECT_SLICE = 11
    RUBIK_ROTATE_CW = 12
    RUBIK_ROTATE_CCW = 13
    RUBIK_ROTATE_180 = 14
    RUBIK_ROTATE_CUBE = 15
    RUBIK_RESET = 16
    RUBIK_SHUFFLE = 17
    RUBIK_AUTO_SOLVE = 18
    RUBIK_FACE_HINT = 19
    RUBIK_NAMES = 20


remote_commands = {
    'quit': RemoteCmd.QUIT,
    'cancel': RemoteCmd.CANCEL,
    'face': RemoteCmd.RUBIK_SELECT_FACE,
    'slice': RemoteCmd.RUBIK_SELECT_SLICE,
    'cw': RemoteCmd.RUBIK_ROTATE_CW,
    'ccw': RemoteCmd.RUBIK_ROTATE_CCW,
    '180': RemoteCmd.RUBIK_ROTATE_180,
    'cube': RemoteCmd.RUBIK_ROTATE_CUBE,
    'reset': RemoteCmd.RUBIK_RESET,
    'shuffle': RemoteCmd.RUBIK_SHUFFLE,
    'scramble': RemoteCmd.RUBIK_SHUFFLE,
    'random': RemoteCmd.RUBIK_SHUFFLE,
    'auto': RemoteCmd.RUBIK_AUTO_SOLVE,
    'hint': RemoteCmd.RUBIK_FACE_HINT,
    'names': RemoteCmd.RUBIK_NAMES
}


def get_cube_ip(starts_with=['192', '10'], default='localhost'):
    adapters = ifaddr.get_adapters()
    for adapter in adapters:
        for ip in adapter.ips:
            if isinstance(ip.ip, str):
                for c in starts_with:
                    if ip.ip.startswith(c):
                        return ip.ip
    return default
