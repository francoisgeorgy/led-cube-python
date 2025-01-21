> [!NOTE]  
> **Project Status: On Hold**
> 
> This project is currently on hold as I’m occupied with other priorities. I still plan to continue working on it and aim to provide updates and complete the documentation before this summer.
> 
> Thank you for your interest and understanding!



LED Cube - Python
=================

Checkout the [main repository](https://github.com/francoisgeorgy/led-cube) to get more information about the LED Cube.

Installation
------------

If you want to run the Rubik's Cube demo, see the dedicated chapter later on. 

### For development

    pip install --editable .
    pip install fastapi uvicorn 'uvicorn[standard]' bottle ifaddr segno

### In the Cube

    pip install --editable .
    pip install RPi.GPIO adafruit-blinka fastapi uvicorn 'uvicorn[standard]' bottle ifaddr segno

Rubik's Cube demo
-----------------

    pip install RubikTwoPhase

After having installed the `RubikTwoPhase` you have to generate some data which will be used to solve the cubes. 

Open a python interpreter and do :  

    import twophase.solver  as sv

This will create a `twophase` directory with pre-computed data files in it. About 70MB. 

This directory can be copied in the Raspberry Pi. This way you don't need to generate the data on the Raspberry itself.

For more details, see https://github.com/hkociemba/RubiksCube-TwophaseSolver. 

Running the examples
--------------------

To be documented...

Known issues
------------

To be documented...

Credits
-------

- https://github.com/hzeller/rpi-rgb-led-matrix 
- https://github.com/ty-porter/RGBMatrixEmulator

For the Rubik's Cube demo : 

- https://github.com/hkociemba/RubiksCube-TwophaseSolver
- https://github.com/robertofiguz/python-rubik/tree/master
