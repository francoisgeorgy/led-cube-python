import math


def shader(x: float, y: float, z: float, t: float = 0.0) -> [float, float, float]:

    # TODO: use perlin noise for the amplitude factor

    # angle = math.atan2(y, x) * math.sin(t/10)
    angle = math.atan2(z, x)
    # if angle < 0:
    #     angle += 2 * math.pi
    # if abs(z - math.sin(angle*3*math.pi + t/20) / math.pi) < 0.01:
    # if abs(z - math.sin(angle*5) / math.pi) < 0.01:

    # the period MUST be a integer multiple of "angle"
    # if abs(z - math.sin(angle*5 + t/10) / math.pi) < 0.01:
    # if abs(z - math.sin(angle*5 + t/10) / 2) < 0.01:
    if abs(y - math.sin(angle*5 + t/11) / abs(math.cos(t/10)*2+5)) < 0.01:
        return 0, 1, 1
    elif abs(y - math.cos(angle*4 - t/7) / abs(math.cos(t/10+3)*2+6)) < 0.01:
        return 1, 1, 0
    else:
        return 0, 0, 0


# def shader(x: float, y: float, z: float, t: float = 0.0) -> [float, float, float]:
#     if abs(z - math.sin(x*2*math.pi) / 2) < 0.01:
#         return 1, 1, 1
#     else:
#         return 0.1, 0.1, 0.1


# def shader(x: float, y: float, z: float, t: float = 0.0) -> [float, float, float]:
#     if abs(z - math.sin(t/10) / 2) < 0.01:
#         return 1, 1, 1
#     else:
#         return 0.1, 0.1, 0.1


# def shader(x: float, y: float, z: float, t: float = 0.0) -> [float, float, float]:
#     if abs(math.sin(x*y) * z) < 0.01:
#         return 1, 1, 1
#     else:
#         return 0.1, 0.1, 0.1

