
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
    download(); ddbb_path = BASE_DIR/'database'; rel_db_app_path = f'database/{DDBB_CLOUD_NAME}'
    # files = os.listdir(ddbb_path)
    # if DDBB_CLOUD_NAME in files: 
    #     outcome = process.run(f"cd database & del /f/q/s '{DDBB_CLOUD_NAME}' & rmdir /q/s '{DDBB_CLOUD_NAME}'", shell=True)
    #     if outcome == 1:
    #         upload_logger.info(" Fallo al eliminar carpeta mongoapp para reemplazar")
    
    # Metemos la info de mongo en la carpeta
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
