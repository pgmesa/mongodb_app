
import logging
# Imports de definicionde comando
from mypy_modules.cli import Command, Flag, Option
# Imports para la funcion del comando
from mypy_modules.register import register
from ..rm_cmd.rm import rm

def get_clear_cmd() -> Command:
    msg = """Deletes every key of the register"""
    clear = Command(
        'clear', description=msg
    )
    # -----------------
    y = Flag('-y', description="doesn't ask for confirmation")
    clear.add_flag(y)
    
    
    return clear

clear_logger = logging.getLogger(__name__)
def clear(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    if not "-y" in flags:
        msg = "¿Estas seguro de eliminar el registro permanentemente? (y/n): "
        response = str(input(msg))
        if response.lower() != "y":
            clear_logger.info(" Operacion cancelada")
            return
    try:
        reg = register.load()
        if reg is None:
            clear_logger.warning(" El registro ya esta vacio")
        else:
            reg_keys = list(reg.keys())
            rm(args=reg_keys)
            clear_logger.info(" Registro eliminado con exito")
    except Exception as err:
        msg = (f" Fallo al intentar eliminar el registro" + 
                f"\n    ERROR MSG: {err}")
        clear_logger.error(msg)