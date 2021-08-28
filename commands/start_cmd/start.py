
import logging
# Imports de definicionde comando
from mypy_modules.cli import Command, Flag, Option
# Imports para la funcion del comando
from mypy_modules.process import process
from configs.settings import BASE_DIR

def get_start_cmd() -> Command:
    start = Command(
        'start', description='initializes the app server'
    )
    return start

start_logger = logging.getLogger(__name__)
def start(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    # Llamar a .bat para que ejecute la orden
    start_logger.info(" Iniciando servidor...")
    cmd = f" cd {BASE_DIR/'appvenv/Scripts'}"
    cmd += " & activate"
    cmd += f"& cd {BASE_DIR}"
    cmd += " & python manage.py runserver"
    cmd += " & exit"
    final_cmd = f'start cmd /k "{cmd}"'
    process.Popen(final_cmd, shell=True)
    start_logger.info(" Servidor Iniciado...")
  
        