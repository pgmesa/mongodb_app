
import logging
import json

# Imports de definicionde comando
from mypy_modules.cli import Command, Flag, Option
# Imports para la funcion del comando
from mypy_modules.register import register

def get_show_cmd() -> Command:
    msg = """<void or register_keys> shows the information stored in
    the register keys or all the register if a key is not specified"""
    show = Command(
        'show', description=msg,
        extra_arg=True, multi=True
    )
    
    return show

# --------------------------------------------------------------------
# --------------------------------------------------------------------
show_logger = logging.getLogger(__name__)
def show(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    reg = register.load()
    if reg is not None:
        valid_args_dict = {}
        if len(args) > 0:
            for arg in args:
                if arg in reg:
                    valid_args_dict[arg] = reg[arg]
                else:
                    msg = f" La clave '{arg}' no existe en el registro"
                    show_logger.error(msg)
            if not bool(valid_args_dict): return
            pretty = json.dumps(valid_args_dict, indent=4, sort_keys=True)
        else:
            pretty = json.dumps(reg, indent=4, sort_keys=True)
        print(); print(pretty); print()
    else:
        show_logger.error(" EL registro esta vacio")