
import logging
from mypy_modules.process import process

# Imports de definicionde comando
from mypy_modules.cli import Command, Flag, Option
# Imports para la funcion del comando


def get_show_cmd() -> Command:
    msg = f"""shows the git repository configuration"""
    show = Command(
        'show', description=msg
    )
    
    return show

# --------------------------------------------------------------------
# --------------------------------------------------------------------
show_logger = logging.getLogger(__name__)
def show(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    ...