
import logging
from mypy_modules.process import process

# Imports de definicionde comando
from mypy_modules.cli import Command, Flag, Option
# Imports para la funcion del comando


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
    ...