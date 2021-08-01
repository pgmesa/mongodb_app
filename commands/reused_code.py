
import os

from mypy_modules.process import process

DDBB_CLOUD_NAME = "mongoapp"

def download(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    if os.path.exists('database'):
        os.remove('database')
    try:
        process.run("git clone https://github.com/pgmesa/database", shell=True)
    except process.ProcessErr as err:
        msg = (" Error al descargar la base de datos en la nube " + 
            f"(https://github.com/pgmesa/database) -> {err}")
        raise Exception(msg)