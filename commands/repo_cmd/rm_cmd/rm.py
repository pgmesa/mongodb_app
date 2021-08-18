
import logging
from mypy_modules.process import process

# Imports de definicionde comando
from mypy_modules.cli import Command, Flag, Option
# Imports para la funcion del comando


def get_rm_cmd() -> Command:
    msg = f"""removes the git repository"""
    rm = Command(
        'rm', description=msg
    )
    
    return rm

# --------------------------------------------------------------------
# --------------------------------------------------------------------
rm_logger = logging.getLogger(__name__)
def rm(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    ...