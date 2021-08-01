
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
    msg = """uploads the mongoapp to (github.com/pgmesa/databases)"""
    upload = Command(
        'upload', description=msg
    )

    return upload

upload_logger = logging.getLogger(__name__)
def upload(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    # Descargamos la base de datos de github y eliminamos el registro anterior de la
    # mongoapp para reemplazarlo
    download(); ddbb_path = BASE_DIR/'databases'; rel_db_app_path = f'databases/{DDBB_CLOUD_NAME}'
    files = os.listdir(ddbb_path)
    if DDBB_CLOUD_NAME in files:
        try:
            process.run(f'cd databases & del /f/q/s "{DDBB_CLOUD_NAME}" & rmdir /q/s "{DDBB_CLOUD_NAME}"', shell=True)
        except process.ProcessErr as err:
            msg = f" Fallo al eliminar carpeta mongoapp para reemplazar -> {err}"
            upload_logger.error(msg) 
            return
    # Metemos la info de mongo en la nueva carpeta (la estamos reemplazando)
    msg = " Descargando documentos de mongodb pertenecientes a la aplicacion..."
    upload_logger.info(msg)
    process.run(f'cd databases & mkdir "{DDBB_CLOUD_NAME}"', shell=True)
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
    upload_logger.info(f" Actualizando base de datos '{DDBB_CLOUD_NAME}' en github...")
    order = f'cd databases'
    order += ' & git add .'
    order += f' & git commit -m "Actualizando {DDBB_CLOUD_NAME}"'
    order += ' & git push origin main'
    try:
        process.run(order, shell=True)
    except process.ProcessErr as err:
        msg = f" No se ha podido actualizar la informacion en github -> {err}"
        upload_logger.error(msg)
    else:
        upload_logger.info(" Cambios actualizados en github con exito")
    
    # Eliminamos la base de datos anterior descargada (carpeta 'databases')
    try:
        process.run('del /f/q/s databases & rmdir /q/s databases', shell=True)
    except process.ProcessErr as err:
        msg = f" Fallo al eliminar carpeta 'databases' descargada de github -> {err}"
        upload_logger.error(msg)