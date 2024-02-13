LED Cube Python software installation
=====================================

### Prerequisites : 

You must have setup the Raspberry Pi OS as documented in [LED-Cube main repository](https://github.com/francoisgeorgy/led-cube/blob/main/os-installation.md).

## Python libraries and sample apps : 

First, we will create a [Python virtual environment](https://docs.python.org/3/library/venv.html) (venv) for all the cube software: 

    cd /home/cube
    python3 -m venv --system-site-packages .venv

Activate this venv : 

    source .venv/bin/activate

Checkout the led-cube-python code : 
 
    git clone https://github.com/francoisgeorgy/led-cube-python python

and install this led-cube-python code as a library into our venv : 

    cd python
    pip install --editable .

If all goes well, you must get a message like :

    Successfully installed ledcube-0.1.0

Continue installation : 

    pip install RPi.GPIO adafruit-blinka fastapi uvicorn 'uvicorn[standard]' bottle ifaddr segno 
    # dependencies for the emulator : 
    pip install bdfparser Pillow tornado libsixel-python pygame

### Update the pixel-mapper for the Cube : 

We need to compile a new pixel-mapper for the Cube. This is a C++ code that need to be updated in the
rpi-rgb-matrix library. 

(Note: these instructions are also available in [src/cpp/mapper/README.md](src%2Fcpp%2Fmapper%2FREADME.md))

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

### Rubiks' Cube demo prerequisites : 

If you plan to run the Rubik's Cube demo, install this package : 

    pip install RubikTwoPhase

After having installed the `RubikTwoPhase` you have to generate some data which will be used to solve the cubes. 

Open a python interpreter and do :  

    import twophase.solver  as sv

This will create a `twophase` directory with pre-computed data files in it. About 70MB. 

This directory can be copied in the Raspberry Pi. This way you don't need to generate the data on the Raspberry itself.

For more details, see https://github.com/hkociemba/RubiksCube-TwophaseSolver. 

### Test LIS3DH access with Python : 

Test with the script `lis3dh_simpletest.py` available in the ledcube package :

    python src/ledcube/imu/lis3dh_simpletest.py

### Test the rpi-rgb-led-matrix library bindings for Python : 

We will use the python bindings created while installing the rpi-rgb library before.

Test : 

    # one panel : 
    sudo -E env PATH=$PATH python src/examples/rgb.py --led-slowdown-gpio 5

    # all panels : 
    sudo -E env PATH=$PATH python src/examples/rgb3d.py --led-slowdown-gpio 5 --led-rows=64 --led-cols=64 --led-chain 3 --led-parallel 2


----

## Notes : 

### Using "sudo" in a Python venv : 

We need to have root privileges to get good performances, so we need to use sudo.

Here is how to use a python venv with sudo  :

    sudo -E env PATH=$PATH ...

example : 

    (.venv) $ sudo -E env PATH=$PATH python -c 'import sys; print(sys.path)'
    (.venv) $ sudo -E env PATH=$PATH pip -VV

Note: sudo is only needed when running a python script which uses the rip-rgb lib. It is not needed otherwise.


