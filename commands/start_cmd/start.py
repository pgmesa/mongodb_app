
import logging
# Imports de definicionde comando
from mypy_modules.cli import Command, Flag, Option

def get_start_cmd() -> Command:
    start = Command(
        'start', description='initialize the app server'
    )
    return start

def start(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    # Llamar a .bat para que ejecute la orden
    
    ...