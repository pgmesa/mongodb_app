
from mypy_modules.process import process

DDBB_CLOUD_NAME = "mongoapp"

def download(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    outcome = process.run("git clone https://github.com/pgmesa/database", shell=True)
    if outcome == 1:
        msg = "Error al descargar la base de datos en la nube (https://github.com/pgmesa/database)"
        raise Exception(msg)