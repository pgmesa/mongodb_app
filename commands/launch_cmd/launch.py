
import logging
# Imports de definicionde comando
from mypy_modules.cli import Command, Flag, Option
# Imports para la funcion del comando
from ..open_cmd.open import open_
from ..start_cmd.start import start

def get_launch_cmd() -> Command:
    launch = Command(
        'launch', description='initializes and opens the app'
    )
    return launch

def launch(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    # Llamar a .bat para que ejecute la orden
    open_()
    start()
    