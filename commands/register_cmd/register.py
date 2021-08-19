
import logging
# Imports de definicionde comando
from mypy_modules.cli import Command, Flag, Option
from .rm_cmd.rm import rm, get_rm_cmd
from .clear_cmd.clear import clear, get_clear_cmd
from .show_cmd.show import get_show_cmd, show
# Imports para la funcion del comando


def get_register_cmd() -> Command:
    msg = """allows to interact with the configuration 
    register of the app"""
    register = Command(
        'register', description=msg,
        mandatory_nested_cmd=True,
    )
    # ++++++++++++++++++++++++++++
    rm_cmd = get_rm_cmd()
    register.nest_cmd(rm_cmd)
    # ++++++++++++++++++++++++++++
    clear_cmd = get_clear_cmd()
    register.nest_cmd(clear_cmd)
    # ++++++++++++++++++++++++++++
    show_cmd = get_show_cmd()
    register.nest_cmd(show_cmd)
    
    return register

register_logger = logging.getLogger(__name__)
def register(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    if "rm" in nested_cmds:
        cmd_info = nested_cmds.pop('rm')
        rm(**cmd_info)
    elif "clear" in nested_cmds:
        cmd_info = nested_cmds.pop('clear')
        clear(**cmd_info)
    elif "show" in nested_cmds:
        cmd_info = nested_cmds.pop('show')
        show(**cmd_info)
    
    