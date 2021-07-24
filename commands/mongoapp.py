
from mypy_modules.cli import Command, Flag, Option

def get_mongoapp_cmd() -> Command:
    msg = """
    allows to interact with the mongoapp
    """
    mongoapp = Command(
        'main.py', description=msg
    )
    return mongoapp
    
def mongoapp():
    ...