
import logging
# Imports de definicionde comando
from mypy_modules.cli import Command, Flag, Option
# Imports para la funcion del comando
from mypy_modules.register import register

def get_remove_cmd() -> Command:
    msg = """allows to remove a key of the register"""
    remove = Command(
        'remove', description=msg,
        extra_arg=True, mandatory=True
    )
    
    return remove

# -------------------------------------------------------------------
# -------------------------------------------------------------------
remove_logger = logging.getLogger(__name__)
def remove(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    key = args[0]
    try:
        register.remove(key)
        remove_logger.info(f" Clave '{key}' eliminada con exito")
    except Exception as err:
        msg = (f" No se ha podido eliminar la clave '{key}' del registro" + 
                f"\n    ERROR MSG: {err}")
        remove_logger.error(msg)