
import logging
# Imports de definicionde comando
from mypy_modules.cli import Command, Flag, Option
# Imports para la funcion del comando
from mypy_modules.process import process
from configs.settings import BASE_DIR
from .remove_cmd.remove import remove, get_remove_cmd
from .clear_cmd.clear import clear, get_clear_cmd

def get_register_cmd() -> Command:
    msg = """allows to interact with the configuration 
    register of the app"""
    register = Command(
        'register', description=msg,
        mandatory_nested_cmd=True,
    )
    # +++++++++++++++++++
    remove_cmd = get_remove_cmd()
    register.nest_cmd(remove_cmd)
    # +++++++++++++++++++
    clear_cmd = get_clear_cmd()
    register.nest_cmd(clear_cmd)
    
    return register

register_logger = logging.getLogger(__name__)
def register(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    if "remove" in nested_cmds:
        cmd_info = nested_cmds.pop('remove')
        remove(**cmd_info)
    elif "clear" in nested_cmds:
        cmd_info = nested_cmds.pop('clear')
        clear(**cmd_info)
    