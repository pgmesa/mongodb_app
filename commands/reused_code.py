
import os

from mypy_modules.process import process

DDBB_CLOUD_NAME = "mongoapp"

def download(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    if os.path.exists('databases'):
        os.remove('databases')
    try:
        process.run("git clone https://github.com/pgmesa/databases", shell=True)
    except process.ProcessErr as err:
        msg = (" Error al descargar la base de datos en la nube " + 
            f"(https://github.com/pgmesa/databases) -> {err}")
        raise Exception(msg)