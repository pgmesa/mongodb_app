
from mypy_modules.cli import Command, Flag, Option
# imports de los comandos asociados
from .open_cmd.open import open_, get_open_cmd
from .start_cmd.start import get_start_cmd

def get_mongoapp_cmd() -> Command:
    msg = """
    allows to interact with the mongoapp
    """
    mongoapp = Command(
        'main.py', description=msg
    )
    # ++++++++++++++++++++++++++++++++
    open_cmd = get_open_cmd()
    mongoapp.nest_cmd(open_cmd)
    # ++++++++++++++++++++++++++++++++
    start_cmd = get_start_cmd()
    mongoapp.nest_cmd(start_cmd)
    
    return mongoapp
    
def mongoapp(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    if "open" in nested_cmds:
        cmd_info = nested_cmds.pop("open")
        open_(**cmd_info)
    elif "start" in nested_cmds:
        pass
    