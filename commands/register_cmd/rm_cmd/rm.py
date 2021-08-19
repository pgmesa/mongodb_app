
import logging
# Imports de definicionde comando
from mypy_modules.cli import Command, Flag, Option
# Imports para la funcion del comando
from mypy_modules.register import register

def get_rm_cmd() -> Command:
    msg = """<register_key> allows to remove a key of the register"""
    rm = Command(
        'rm', description=msg,
        extra_arg=True, mandatory=True
    )
    
    return rm

# -------------------------------------------------------------------
# -------------------------------------------------------------------
rm_logger = logging.getLogger(__name__)
def rm(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    key = args[0]
    try:
        register.remove(key)
        rm_logger.info(f" Clave '{key}' eliminada con exito")
    except Exception as err:
        msg = (f" No se ha podido eliminar la clave '{key}' del registro" + 
                f"\n    ERROR MSG: {err}")
        rm_logger.error(msg)