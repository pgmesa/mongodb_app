
import logging
# Imports de definicionde comando
from mypy_modules.cli import Command, Flag, Option
# Imports para la funcion del comando
from mypy_modules.register import register

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
                try:
                    register.remove(key)
                    rm_logger.info(f" Clave '{key}' eliminada con exito")
                except Exception as err:
                    msg = (f" No se ha podido eliminar la clave '{key}' " + 
                            f"del registro\n    ERROR MSG: {err}")
                    rm_logger.error(msg)
            else:
                rm_logger.error(f" La clave {key} no existe en el registro")
    else:
        rm_logger.error(" EL registro esta vacio")