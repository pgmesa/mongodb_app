
from mypy_modules.cli import Command, Flag, Option
# imports de los comandos asociados
from .open_cmd.open import open_, get_open_cmd
from .start_cmd.start import get_start_cmd, start
from .launch_cmd.launch import get_launch_cmd, launch

def get_mongoapp_cmd() -> Command:
    msg = """
    allows to interact with the mongoapp
    """
    mongoapp = Command(
        'mongoapp', description=msg, mandatory_nested_cmd=True
    )
    # ++++++++++++++++++++++++++++++++
    open_cmd = get_open_cmd()
    mongoapp.nest_cmd(open_cmd)
    # ++++++++++++++++++++++++++++++++
    start_cmd = get_start_cmd()
    mongoapp.nest_cmd(start_cmd)
    # ++++++++++++++++++++++++++++++++
    launch_cmd = get_launch_cmd()
    mongoapp.nest_cmd(launch_cmd)
    
    return mongoapp
    
def mongoapp(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    if "open" in nested_cmds:
        cmd_info = nested_cmds.pop("open")
        open_(**cmd_info)
    elif "start" in nested_cmds:
        cmd_info = nested_cmds.pop("start")
        start(**cmd_info)
    elif "launch" in nested_cmds:
        cmd_info = nested_cmds.pop("launch")
        launch(**cmd_info)
    elif "download" in nested_cmds:
        cmd_info = nested_cmds.pop("download")
        download(**cmd_info)
    