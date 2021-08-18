
import logging
from mypy_modules.process import process

# Imports de definicionde comando
from mypy_modules.cli import Command, Flag, Option
from .add_cmd.add import get_add_cmd, add
from .rm_cmd.rm import get_rm_cmd, rm
from .show_cmd.show import get_show_cmd, show
# Imports para la funcion del comando
from controllers import db_controller as dbc


def get_repo_cmd() -> Command:
    msg = f"""git repository to store the documents of the 
    Mongo databases managed by the app"""
    repo = Command(
        'repo', description=msg, 
        mandatory_nested_cmd=True
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
    usr_opt = def_usr_opt()
    repo.add_option(usr_opt)
    # --------------------------------
    name_opt = def_name_opt()
    repo.add_option(name_opt)
    # --------------------------------
    dir_opt = def_dir_opt()
    repo.add_option(dir_opt)
    
    return repo

# --------------------------------------------------------------------
def def_usr_opt() -> Option:
    msg = """<github_user_name> allows to change the github user"""
    usr = Option(
        '--usr', description=msg,
        extra_arg=True, mandatory=True
    )
    
    return usr

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
    if "add" in nested_cmds:
        cmd_info = nested_cmds.pop("add")
        add(**cmd_info)
    if "rm" in nested_cmds:
        cmd_info = nested_cmds.pop("rm")
        rm(**cmd_info)
    if "show" in nested_cmds:
        cmd_info = nested_cmds.pop("show")
        show(**cmd_info)
    