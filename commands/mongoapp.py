
from commands.upload_cmd.upload import upload
from mypy_modules.cli import Command, Flag, Option
# imports de los comandos asociados
from .open_cmd.open import open_, get_open_cmd
from .start_cmd.start import get_start_cmd, start
from .launch_cmd.launch import get_launch_cmd, launch
from .upload_cmd.upload import get_upload_cmd, upload
from .restore_cmd.restore import get_restore_cmd, restore
from .register_cmd.register import get_register_cmd, register

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
    # ++++++++++++++++++++++++++++++++
    upload_cmd = get_upload_cmd()
    mongoapp.nest_cmd(upload_cmd)
    # ++++++++++++++++++++++++++++++++
    restore_cmd = get_restore_cmd()
    mongoapp.nest_cmd(restore_cmd)
    # ++++++++++++++++++++++++++++++++
    register_cmd = get_register_cmd()
    mongoapp.nest_cmd(register_cmd)
    
    
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
    elif "upload" in nested_cmds:
        cmd_info = nested_cmds.pop("upload")
        upload(**cmd_info)
    elif "restore" in nested_cmds:
        cmd_info = nested_cmds.pop("restore")
        restore(**cmd_info)
    elif "register" in nested_cmds:
        cmd_info = nested_cmds.pop("register")
        register(**cmd_info)
        
    