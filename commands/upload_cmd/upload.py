
import logging
from mypy_modules import register
import os
import json
from mypy_modules.process import process

# Imports de definicionde comando
from mypy_modules.cli import Command, Flag, Option
# Imports para la funcion del comando
from controllers import db_controller as dbc
from configs.settings import BASE_DIR
from ..reused_code import (
    download_repo, remove_repo, GITHUB_URL, get_github_info, 
    save_github_info, SECURE_DIR
)

def get_upload_cmd() -> Command:
    msg = f"""uploads the mongoapp to the github repository specified"""
    upload = Command(
        'upload', description=msg
    )

    return upload

# --------------------------------------------------------------------
# --------------------------------------------------------------------
upload_logger = logging.getLogger(__name__)
def upload(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    # Descargamos la base de datos de github y eliminamos el registro 
    # anterior de la mongoapp para reemplazarlo
    save_github_info()
    try:
        download_repo()
    except process.ProcessErr as err:
        upload_logger.error(err); return
    github_user, repo_name, dir_name = get_github_info()
    ddbb_path = BASE_DIR/f'{SECURE_DIR}'
    rel_db_app_path = f'{SECURE_DIR}/{dir_name}'
    files = os.listdir(ddbb_path)
    if dir_name in files:
        try:
            process.run(f'cd {SECURE_DIR} & del /f/q/s "{dir_name}" '
                        + f'& rmdir /q/s "{dir_name}"', shell=True)
        except process.ProcessErr as err:
            msg = f" Fallo al eliminar carpeta mongoapp para reemplazar -> {err}"
            upload_logger.error(msg) 
            return
    # Metemos la info de mongo en la nueva carpeta (la estamos reemplazando)
    msg = " Descargando documentos de mongodb pertenecientes a la aplicacion..."
    upload_logger.info(msg)
    process.run(f'cd {SECURE_DIR} & mkdir "{dir_name}"', shell=True)
    dbs = dbc.list_dbs(only_app_dbs=True)
    for db in dbs:
        process.run(f'cd "{rel_db_app_path}" & mkdir "{db}"', shell=True)
        collections = dbc.list_collections(db, only_app_coll=True)
        for collection in collections:
            docs = dbc.get_documents(db, collection, with_app_format=False)
            path = BASE_DIR/f'{rel_db_app_path}/{db}/{collection}.json'
            with open(path, "w") as file:
                json.dump(docs, file, indent=4, sort_keys=True)
    # Actualizamos la informacion en github
    msg = f" Actualizando base de datos '{dir_name}' en github..."
    upload_logger.info(msg)
    try:
        order = f'cd {SECURE_DIR}'
        order += ' & git add .'
        order += f' & git commit -m "Actualizando {dir_name}"'
        branches = process.run(f"cd {SECURE_DIR} & git branch", shell=True)
        if branches == "":
            order += ' & git branch -M main'
        order += ' & git push origin main'
        process.run(order, shell=True)
    except process.ProcessErr as err:
        msg = f" No se ha podido actualizar la informacion en github -> {err}"
        upload_logger.error(msg)
    else:
        upload_logger.info(" Cambios actualizados en github con exito")
    # Eliminamos el repositorio descargado anteriormente
    try:
        remove_repo()
    except process.ProcessErr as err:
        upload_logger.error(err); return