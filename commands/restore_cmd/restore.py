
import logging
import os
import json
from mypy_modules.process import process

# Imports de definicionde comando
from mypy_modules.cli import Command, Flag, Option
# Imports para la funcion del comando
from controllers import db_controller as dbc
from configs.settings import BASE_DIR
from ..reused_code import (
    MongoNotInstalledError, download_repo, check_mongo_installed, remove_repo, GITHUB_URL,
    get_github_info, save_github_info, SECURE_DIR
)

def get_restore_cmd() -> Command:
    msg = f"""restores the last saved mongoapp state in 
    the github repository specified"""
    restore = Command(
        'restore', description=msg
    )

    return restore

# --------------------------------------------------------------------
# --------------------------------------------------------------------
restore_logger = logging.getLogger(__name__)
def restore(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    try:
        check_mongo_installed()
    except MongoNotInstalledError as err:
        restore_logger.error(err)
        return
    save_github_info()
    try:
        download_repo()
    except process.ProcessErr as err:
        restore_logger.error(err); return
    github_user, repo_name, dir_name = get_github_info()    
    files = os.listdir(BASE_DIR/f'{SECURE_DIR}')
    if dir_name in files:
        # Almacenamos y comprobamos que el formato de la carpeta del repositorio y
        # sus archivos tienen el formato correcto
        msg = (" Migrando ultimo estado guardado en " + 
                    f"({GITHUB_URL}/{github_user}/{repo_name}/{dir_name})")
        restore_logger.info(msg)
        dbs = os.listdir(BASE_DIR/f'{SECURE_DIR}/{dir_name}')
        restored_dbs = {}
        try:
            for db in dbs:
                db_path = BASE_DIR/f'{SECURE_DIR}/{dir_name}/{db}'
                if not os.path.isdir(db_path): continue
                restored_dbs[db] = {}
                collections = os.listdir(db_path)
                for collection in collections:
                    path = db_path/f'{collection}'
                    if not os.path.isfile(path):
                        msg = f"'{collection}' no es un fichero .json"
                        raise Exception(msg)
                    try:
                        with open(path, "r") as file:
                            docs = json.load(file)
                    except Exception as err:
                        err_type = type(err)
                        err_msg = (f"Fichero no valido.\nTypeError => " + 
                                   f"{err_type}, {err}") 
                        raise Exception(err_msg)
                    else:
                        collection = collection.removesuffix(".json")
                        restored_dbs[db][collection] = {}
                        if type(docs) is dict:
                            doc = docs
                            restored_dbs[db][collection] = [doc]
                        elif type(docs) is list:
                            restored_dbs[db][collection] = docs
        except Exception as err:
            msg = (f" No se pudo realizar la migracion, error en el formato " + 
                f"\n    ERR MSG -> {err}")
            restore_logger.error(msg)
        else:
            # Eliminamos el estado actual de la app en mongo
            msg = " Eliminando estado actual de las bases de datos de la aplicacion"
            restore_logger.info(msg)
            app_mongo_dbs = dbc.list_dbs(only_app_dbs=True)
            for db in app_mongo_dbs:
                collections = dbc.list_collections(db, only_app_coll=True)
                for collection in collections:
                    dbc.remove_collecttion(db, collection)
            # Guardamos en mongo el estado anterior guardado en e repositorio
            existing_collec = dbc.list_collections(db)
            for db in restored_dbs:
                collections = restored_dbs[db]
                for collection in collections:
                    if collection in existing_collec: continue
                    docs = restored_dbs[db][collection]
                    for doc in docs:
                        dbc.add_document(db, collection, doc)
    else:
        msg = (" No existe ningun estado anterior guardado en el repositorio " +
                f"{GITHUB_URL}/{github_user}/{repo_name}/{dir_name}")
        restore_logger.error(msg)
    # Eliminamos el repositorio descargado anteriormente
    try:
        remove_repo()
    except process.ProcessErr as err:
        restore_logger.error(err); return
    
    
