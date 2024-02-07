
def pixel_mapper(x, y):
    """
    Map coordinates from logical to emulator :

    LOGICAL COORDINATES :

    ┌──────┬──────┬──────┬──────┐
    │0,0   │64,0  │128,0 │192,0 │
    │Front │Right │Back  │Left  │
    ├──────┼──────┼──────┴──────┘
    │0,64  │64,64 │
    │Top   │Bottom│
    └──────┴──────┘

    Emulator DISPLAY coordinates :

           ┌──────┐
           │64,0  │
           │Top   │
    ┌──────┼──────┼──────┬──────┐
    │0,64  │64,64 │128,64│192,64│
    │Left  │Front │Right │Back  │
    └──────┼──────┼──────┴──────┘
           │64,128│
           │Bottom│
           └──────┘

    """

    if y >= 128:
        return 0, 0             # non cube pixels are mapped to (0, 0)
    elif y >= 64:
        if x >= 128:
            return 0, 0         # non cube pixels are mapped to (0, 0)
        elif x >= 64:
            return x, y+64      # Bottom
        else:
            return x+64, y-64   # Top
    else:
        if x >= 192:
            return x-192, y+64  # Left
        elif x >= 128:
            return x+64, y+64   # Back
        elif x >= 64:
            return x+64, y+64   # Right
        else:
            return x+64, y+64   # Front

