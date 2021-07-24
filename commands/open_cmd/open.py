
from mypy_modules.cli import Command, Flag, Option

def get_open_cmd() -> Command:
    open_ = Command(
        'open', description='opens the mongodb app in the explorer'
    )
    open_.add_flag(Flag("-p"))
    return open_
    
def open_():
    # Hay que importar process paera ejecutar la orden que abra el explorer
    ...