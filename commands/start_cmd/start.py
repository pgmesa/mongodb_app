
import logging
# Imports de definicionde comando
from mypy_modules.cli import Command, Flag, Option
# Imports para la funcion del comando
from mypy_modules.process import process

def get_start_cmd() -> Command:
    start = Command(
        'start', description='initializes the app server'
    )
    return start

start_logger = logging.getLogger(__name__)
def start(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    # Llamar a .bat para que ejecute la orden
    start_logger.info(" Iniciando servidor...")
    process.Popen("mongoapp.bat __start__", shell=True)
        