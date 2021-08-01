
import logging
import os
import json
from mypy_modules.process import process

# Imports de definicionde comando
from mypy_modules.cli import Command, Flag, Option
# Imports para la funcion del comando
from controllers import db_controller as dbc
from configs.settings import BASE_DIR
from ..reused_code import download, DDBB_CLOUD_NAME

def get_upload_cmd() -> Command:
    msg = """uploads the mongoapp to (github.com/pgmesa/database)"""
    upload = Command(
        'upload', description=msg
    )

    return upload

upload_logger = logging.getLogger(__name__)
def upload(args:list=[]) -> None:
    # Descargamos la base de datos de github y eliminamos el registro anterior de la
    # mongoapp para reemplazarlo
    download(); ddbb_path = BASE_DIR/'database'; rel_db_app_path = f'database/{DDBB_CLOUD_NAME}'
    files = os.listdir(ddbb_path)
    if DDBB_CLOUD_NAME in files:
        outcome = process.run(f'cd database & del /f/q/s "{DDBB_CLOUD_NAME}" & rmdir /q/s "{DDBB_CLOUD_NAME}"', shell=True)
        if outcome == 1:
            upload_logger.info(" Fallo al eliminar carpeta mongoapp para reemplazar")
    # Metemos la info de mongo en la nueva carpeta (la estamos reemplazando)
    process.run(f'cd database & mkdir "{DDBB_CLOUD_NAME}"', shell=True)
    dbs = dbc.list_dbs(only_app_dbs=True)
    for db in dbs:
        process.run(f'cd "{rel_db_app_path}" & mkdir "{db}"', shell=True)
        collections = dbc.list_collections(db, only_app_coll=True)
        for collection in collections:
            docs = dbc.get_documents(db, collection)
            path = BASE_DIR/f'{rel_db_app_path}/{db}/{collection}.json'
            with open(path, "w") as file:
                json.dump(docs, file, indent=4, sort_keys=True)
    # Actualizamos la informacion en github
    order = f'cd database'
    order += ' & git add .'
    order += f' & git commit -m "Actualizando {DDBB_CLOUD_NAME}"'
    order += ' & git push origin main'
    process.run(order, shell=True)
    # Eliminamos la base de datos anterior descargada (carpeta 'database')
    outcome = process.run(f'del /f/q/s database & rmdir /q/s database', shell=True)
    if outcome == 1:
        upload_logger.info(" Fallo al eliminar carpeta 'database' descargada de github")