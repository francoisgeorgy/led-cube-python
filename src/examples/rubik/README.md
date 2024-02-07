Avec le simulateur on doit spécifier une longeur de chaine de 4 et un nombre de chaines de 3, car le simulateur
utilise un mapper spécial pour représenter le cube sous forme dépliée.

    python src/examples/rubik/automatic_rubik.py -c 4 -P 3


Avec le RPi : 

    cd /home/cube/emulator/
    . .venv/bin/activate
    sudo -E env PATH=$PATH python src/examples/rubik/automatic_rubik.py


Python packages : 

    pip install fastapi uvicorn 'uvicorn[standard]'


App structure : 

    websocket_endpoint
        rub = ThreadedRubik
            ThreadedRubik(Rubik)
