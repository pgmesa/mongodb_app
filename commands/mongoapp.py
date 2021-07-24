
from mypy_modules.cli import Command, Flag, Option
# imports de los comandos asociados
from .open_cmd.open import open_, get_open_cmd

def get_mongoapp_cmd() -> Command:
    msg = """
    allows to interact with the mongoapp
    """
    mongoapp = Command(
        'main.py', description=msg
    )
    open_cmd = get_open_cmd()
    mongoapp.nest_cmd(open_cmd)
    
    return mongoapp
    
def mongoapp(*args, **kwargs):
    # if 'open' in nest_commands:
    #     ...
    ...