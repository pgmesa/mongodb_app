
import logging
from mypy_modules.process import process

# Imports de definicionde comando
from mypy_modules.cli import Command, Flag, Option
# Imports para la funcion del comando
from mypy_modules.register import register
from ...reused_code import save_github_info

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
    github_info = register.load("github")
    if github_info is not None:
        add_logger.error(" Ya existe un repositorio añadido")
    else:
        save_github_info()
        add_logger.info(" Repositorio añadido con exito")
        