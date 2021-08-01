

import logging
import os
import json
from mypy_modules.process import process

# Imports de definicionde comando
from mypy_modules.cli import Command, Flag, Option
# Imports para la funcion del comando
from controllers import db_controller as dbc
from configs.settings import BASE_DIR
from ..reused_code import download_repo, remove_repo, REPO_NAME, DDBB_CLOUD_NAME

def get_restore_cmd() -> Command:
    msg = f"""restores the last saved mongoapp state in 
    (github.com/pgmesa/{REPO_NAME}/{DDBB_CLOUD_NAME})"""
    restore = Command(
        'restore', description=msg
    )

    return restore

# --------------------------------------------------------------------
# --------------------------------------------------------------------
restore_logger = logging.getLogger(__name__)
def restore(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    try:
        download_repo()
    except process.ProcessErr as err:
        restore_logger.error(err); return
    # Eliminamos el estado actual de la app en mongo
    msg = " Eliminando estado actual de las bases de datos de la aplicacion"
    restore_logger.info(msg)
    app_mongo_dbs = dbc.list_dbs(only_app_dbs=True)
    for db in app_mongo_dbs:
        collections = dbc.list_collections(db, only_app_coll=True)
        for collection in collections:
            dbc.remove_collecttion(collection)
    # Guardamos en mongo el estado anterior de la app
    msg = (" Migrando ultimo estado guardado en " + 
                f"(github.com/pgmesa/{REPO_NAME}/{DDBB_CLOUD_NAME})")
    restore_logger.info(msg)
    files = os.listdir(BASE_DIR/f'{REPO_NAME}')
    if DDBB_CLOUD_NAME in files:
        dbs = os.listdir(BASE_DIR/f'{REPO_NAME}/{DDBB_CLOUD_NAME}')
        for db in dbs:
            collections = os.listdir(BASE_DIR/f'{REPO_NAME}/{DDBB_CLOUD_NAME}/{db}')
            for collection in collections:
                path = BASE_DIR/f'{REPO_NAME}/{DDBB_CLOUD_NAME}/{db}/{collection}'
                try:
                    with open(path, "r") as file:
                        docs = json.load(file)
                except Exception as err:
                    err_type = type(err)
                    err_msg = ("Fallo al realizar las migraciones, " + 
                        f"fichero no valido. TypeError => {err_type}")
                    restore_logger.error(err_msg)
                else:
                    if type(docs) is dict:
                        doc = docs
                        dbc.add_document(db, collection, doc)
                    elif type(docs) is list:
                        for doc in docs:
                            dbc.add_document(db, collection, doc)
    # Eliminamos el repositorio descargado anteriormente
    try:
        remove_repo()
    except process.ProcessErr as err:
        restore_logger.error(err); return
    
    
