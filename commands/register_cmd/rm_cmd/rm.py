
import logging
from contextlib import suppress

# Imports de definicionde comando
from mypy_modules.cli import Command, Flag, Option
# Imports para la funcion del comando
from mypy_modules.register import register
from commands.reused_code import TASKS_DIR
from mypy_modules.process import process

def get_rm_cmd() -> Command:
    msg = """<register_key> allows to remove a key of the register"""
    rm = Command(
        'rm', description=msg,
        extra_arg=True, mandatory=True, multi=True
    )
    
    return rm

# -------------------------------------------------------------------
# -------------------------------------------------------------------
rm_logger = logging.getLogger(__name__)
def rm(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    reg = register.load()
    if reg is not None:
        for key in args:
            if key in reg:
                value = reg[key]
                try:
                    register.remove(key)
                    rm_logger.info(f" Clave '{key}' eliminada con exito")
                    if key == 'tasks':
                        tasks_names = value.keys()
                        for task in tasks_names:
                            with suppress(Exception):
                                cmd = f'SCHTASKS /DELETE /TN "{TASKS_DIR}\\{task}" /F'
                                process.run(cmd, shell=True)
                except Exception as err:
                    msg = (f" No se ha podido eliminar la clave '{key}' " + 
                            f"del registro\n    ERROR MSG: {err}")
                    rm_logger.error(msg)
            else:
                rm_logger.error(f" La clave {key} no existe en el registro")
    else:
        rm_logger.error(" EL registro esta vacio")