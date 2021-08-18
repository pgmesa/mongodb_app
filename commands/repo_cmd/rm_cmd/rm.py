
import logging
from mypy_modules.process import process

# Imports de definicionde comando
from mypy_modules.cli import Command, Flag, Option
# Imports para la funcion del comando
from mypy_modules.register import register

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
    github_info = register.load("github")
    if github_info is None:
        rm_logger.error(" No se hay ningun repositorio que eliminar")
    else:
        register.remove('github')
        msg = f" Repositorio eliminado con exito\n      -> '{github_info}'"
        rm_logger.info(msg)