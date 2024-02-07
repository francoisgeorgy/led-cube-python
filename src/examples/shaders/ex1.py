import math

equal_brightness = True


def shader(x: float, y: float, z: float, t: float = 0.0) -> [float, float, float]:

    # return (math.sin(y*8+t/1)+1)/2, 0, 0
    # return 0, (math.sin(x*8+t/1)+1)/2, 0

    # return (math.sin(y*8+t/1)+1)/2, (math.sin(x*8+t/1)+1)/2, (math.sin(z*8+t/1)+1)/2
    # return (math.sin(y*11+t/1)+1)/2, (math.sin(x*13+t/1)+1)/2, (math.sin(z*8+t/1)+1)/3
    return ((math.sin(y * (5+(math.sin(t/13)+1)*11) + t/1)+1)/2,
            (math.sin(x * (5+(math.sin(t/13)+1)*11) + t/1)+1)/2,
            (math.sin(z*8+t/1)+1)/3)

    # r = x + 0.5
    # g = y + 0.5
    # b = z + 0.5
    # if equal_brightness:
    #     gamma = .43
    #     # print(r)
    #     # print(gamma)
    #     r, g, b = r ** (1 / gamma), g ** (1 / gamma), b ** (1 / gamma)
    #     t = r + g + b
    #     # print(r, g, b)
    #     # print(t)
    #     if t < 0.000001:
    #         r, g, b = 0, 0, 0
    #     else:
    #         r = r / t
    #         g = g / t
    #         b = b / t
    #         r, g, b = r ** gamma, g ** gamma, b ** gamma
    # return r, g, b

