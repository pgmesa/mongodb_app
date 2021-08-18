
import logging
from mypy_modules.process import process

# Imports de definicionde comando
from mypy_modules.cli import Command, Flag, Option
from .add_cmd.add import get_add_cmd, add
from .rm_cmd.rm import get_rm_cmd, rm
from .show_cmd.show import get_show_cmd, show
# Imports para la funcion del comando
from mypy_modules.register import register


def get_repo_cmd() -> Command:
    msg = f"""git repository to store the documents of the 
    Mongo databases managed by the app"""
    repo = Command(
        'repo', description=msg
    )
    # ++++++++++++++++++++++++++++++++
    add_cmd = get_add_cmd()
    repo.nest_cmd(add_cmd)
    # ++++++++++++++++++++++++++++++++
    rm_cmd = get_rm_cmd()
    repo.nest_cmd(rm_cmd)
    # ++++++++++++++++++++++++++++++++
    show_cmd = get_show_cmd()
    repo.nest_cmd(show_cmd)
    # --------------------------------
    user_opt = def_user_opt()
    repo.add_option(user_opt)
    # --------------------------------
    name_opt = def_name_opt()
    repo.add_option(name_opt)
    # --------------------------------
    dir_opt = def_dir_opt()
    repo.add_option(dir_opt)
    
    return repo

# --------------------------------------------------------------------
def def_user_opt() -> Option:
    msg = """<github_user_name> allows to change the github user"""
    user = Option(
        '--user', description=msg,
        extra_arg=True, mandatory=True
    )
    
    return user

def def_name_opt() -> Option:
    msg = """<github_repo_name> allows to change the github repository name"""
    name = Option(
        '--name', description=msg,
        extra_arg=True, mandatory=True
    )
    
    return name
    
def def_dir_opt() -> Option:
    msg = """<dir_inside_github_repo> allows to change the directory of the repository
    where the documents will be stored/downloaded from"""
    dir_ = Option(
        '--dir', description=msg,
        extra_arg=True, mandatory=True
    )
    
    return dir_

# --------------------------------------------------------------------
# --------------------------------------------------------------------
repo_logger = logging.getLogger(__name__)
def repo(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    # Miramos las opciones
    github_info = register.load('github')
    if "--user" in options:
        if github_info is not None:
            new_user = options['--user'][0]
            github_info['user'] = new_user
            register.update('github', github_info)
            msg = f" Usuario de github actualizado con exito a '{new_user}'"
            repo_logger.info(msg)
        else:
            msg = f" No se ha añadido ningun repositorio todavia"
            repo_logger.info(msg)
    elif "--name" in options:
        if github_info is not None:
            new_name = options['--name'][0]
            github_info['repo_name'] = new_name
            register.update('github', github_info)
            msg = (f" Nombre del repositorio de github actualizado " + 
                    f"con exito a '{new_name}'")
            repo_logger.info(msg)
        else:
            msg = f" No se ha añadido ningun repositorio todavia"
            repo_logger.info(msg)
    elif "--dir" in options:
        if github_info is not None:
            new_dir = options['--dir'][0]
            github_info['dir_name'] = new_dir
            register.update('github', github_info)
            msg = (" Directorio del repositorio actualizado " + 
                    f"con exito a '{new_dir}'")
            repo_logger.info(msg)
        else:
            msg = f" No se ha añadido ningun repositorio todavia"
            repo_logger.info(msg)
            
    # Miramos los comandos anidados
    if "add" in nested_cmds:
        cmd_info = nested_cmds.pop("add")
        add(**cmd_info)
    elif "rm" in nested_cmds:
        cmd_info = nested_cmds.pop("rm")
        rm(**cmd_info)
    elif "show" in nested_cmds:
        cmd_info = nested_cmds.pop("show")
        show(**cmd_info)
    