
import logging
# Imports de definicionde comando
from mypy_modules.cli import Command, Flag, Option
# Imports para la funcion del comando
from mypy_modules.process import process
from configs.settings import BASE_DIR

def get_open_cmd() -> Command:
    open_ = Command(
        'open', description='opens the mongodb app in the explorer'
    )
    return open_

open_logger = logging.getLogger(__name__)
def open_(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    open_logger.info(" Abriendo aplicacion...")
    outcome = process.run("start chrome http://localhost:8000", shell=True)
    if outcome == 1:
        open_logger.error(" Error al abrir la aplicacion en el navegador")
    else:
        open_logger.info(" Aplicacion abierta con exito")
    
    
