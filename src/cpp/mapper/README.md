How to update the pixel-mapper 
------------------------------

Copy `pixel-mapper.cc` in `/home/cube/rpi-rgb-led-matrix/lib/` .

And do : 

(note: do _not_ do that in a python venv.)

    deactivate      # make sure to exit any active python venv
    cd /home/cube/rpi-rgb-led-matrix/
    sudo make -C bindings/python clean PYTHON=$(command -v python3)
    make build-python PYTHON=$(command -v python3)
    sudo make install-python PYTHON=$(command -v python3)

Test :

    cd /home/cube/emulator/
    . .venv/bin/activate
    ./run-sample.sh src/samples/cube_layout.py




