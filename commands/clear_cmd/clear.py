
import os
import logging
from contextlib import suppress
# Imports de definicion de comando
from mypy_modules.cli import Command, Option, Flag
# Imports para la funcion del comando
from controllers import db_controller as dbc
from mypy_modules.register import register

def get_clear_cmd() -> Command:
    clear = Command(
        'clear', description='deletes every database and info stored in the app'
    )
    
    return clear
    

clear_logger = logging.getLogger(__name__)
def clear(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    try:
        clear_logger.info(" Eliminando Bases de Datos...")
        dbs = dbc.list_dbs(only_app_dbs=True)
        for db in dbs:
            clear_logger.info(f" Eliminando db '{db}'")
            dbc.drop_db(db)
        clear_logger.info(" Eliminando registro...")
        register.remove()
        clear_logger.info(" Eliminando migraciones...")
        os.remove('db.sqlite3')
    except Exception as err:
        msg = f" Error al vaciar la aplicacion\n     ERR MSG: {err}"
        msg += "\n -> Revisa que el servidor no este en funcionamiento"
        clear_logger.error(msg)
    else:
        clear_logger.info(" Aplcacion vaciada con exito")
    
    