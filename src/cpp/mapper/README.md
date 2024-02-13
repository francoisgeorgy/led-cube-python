How to update the pixel-mapper 
------------------------------

Copy the new mapper in the rpi-rgb-matrix library : 

    cd /home/cube
    cp python/src/cpp/mapper/pixel-mapper.cc rpi-rgb-led-matrix/lib/

Compile the new mapper : 

(note: do _not_ do that in a python venv.)

    deactivate      # make sure to exit any active python venv
    cd /home/cube/rpi-rgb-led-matrix/
    sudo make -C bindings/python clean PYTHON=$(command -v python3)
    make build-python PYTHON=$(command -v python3)
    sudo make install-python PYTHON=$(command -v python3)

Test :

    cd /home/cube/
    . .venv/bin/activate
    cd python 
    sudo -E env PATH=$PATH python src/examples/rgb.py --led-slowdown-gpio 5




