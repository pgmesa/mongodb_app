
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
    y = Flag('-y', description="doesn't ask for confirmation")
    clear.add_flag(y)
    
    return clear
    

clear_logger = logging.getLogger(__name__)
def clear(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    if not "-y" in flags:
        msg = "¿Estas seguro de querer vaciar la aplicacion? (y/n): "
        response = str(input(msg))
        if response.lower() != "y":
            clear_logger.info(" Operacion cancelada")
            return
    try:
        clear_logger.info(" Eliminando Bases de Datos...")
        dbs = dbc.list_dbs(only_app_dbs=True)
        for db in dbs:
            dbc.drop_db(db)
            clear_logger.info(f"'{db}' ha sido eliminada")
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
    
    