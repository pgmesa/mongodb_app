
import logging
from mypy_modules.process import process

# Imports de definicionde comando
from mypy_modules.cli import Command, Flag, Option
# Imports para la funcion del comando


def get_add_cmd() -> Command:
    msg = f"""adds a git repository"""
    add = Command(
        'add', description=msg
    )
    
    return add

# --------------------------------------------------------------------
# --------------------------------------------------------------------
add_logger = logging.getLogger(__name__)
def add(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    ...