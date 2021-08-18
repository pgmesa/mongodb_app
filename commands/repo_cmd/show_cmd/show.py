
import logging
from mypy_modules.process import process

# Imports de definicionde comando
from mypy_modules.cli import Command, Flag, Option
# Imports para la funcion del comando
from mypy_modules.register import register

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
    github_info = register.load("github")
    print()
    if github_info is None:
        print("     -> No hay ningun repositorio añadido")
    else:
        user = github_info["user"]
        print(f"     + Github user: {user}")
        name = github_info["repo_name"]
        print(f"     + Repository name: {name}")
        dir_ =  github_info["dir_name"]
        print(f"     + Directory: {dir_}")
    print()