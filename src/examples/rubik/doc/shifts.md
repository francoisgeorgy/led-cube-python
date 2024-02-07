
l2r : left to right
r2l : right to left
u2b : up to bottom
b2u : bottom to up

left: slide to left
right : slide to right
up : slide to top
down : slide to bottom

> The letters x, y and z are used to signify cube rotations.
> x signifies rotating the cube in the R direction.
> y signifies the rotation of the cube in the U direction.
> z signifies the rotation of the cube on the F direction.

functions : 

    shift_x_slice(slice, cw, distance) :
        top, back, bottom, front
        
    shift_y_slice(slice, cw, distance) :
        front, right, back, left
        
    shift_z_slice(slice, cw, distance)
        top, right, bottom, left

implementation : 

    y is 0 at bottom, max at top, oriented bottom to top, this is inverse of the panel
    x is 0 at left, max at right, oriented left to right

    shift_x_slice(slice, cw, distance) :
        top, back, bottom, front are oriented the same
        shift is vertical
        cw :  top --> back --> bottom --> front --> top ...
        ccw : top --> front --> bottom --> back --> top ...
        

    shift_y_slice(slice, cw, distance) :
        front, right, back, left front are vertically oriented the same; back as X reversed
        shift is horizontal
        cw :  front --> right --> back --> left --> front ...
        ccw : front --> left --> back --> right --> front ...
        



