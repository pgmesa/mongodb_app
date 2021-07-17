
import json
import logging

from controllers import db_controller as dbc
from configs.settings import BASE_DIR

def get_migrate_cmd():
    ...

migrate_logger = logging.getLogger(__name__)
def migrate(file, db, collection, attrs_order:list=None):
    path = BASE_DIR/f'app_db_state/backups/{file}'
    try:
        with open(path, "r") as file:
            docs = json.load(file)
    except Exception as err:
        err_type = type(err)
        err_msg = ("Fallo al realizar las migraciones, " + 
            f"fichero no valido. TypeError => {err_type}")
        migrate_logger.error(err_msg)
    else:
        if type(docs) is dict:
            if attrs_order is not None:
                docs = sort_dict(attrs_order, docs)
            dbc.add_document(db, collection, docs)
        elif type(docs) is list:
            for doc in docs:
                if attrs_order is not None:
                    doc = sort_dict(attrs_order, doc)
                dbc.add_document(db, collection, doc)
                
def sort_dict(attrs_order:list, dict_:dict) -> dict:
    sorted_dict = {}
    for i in range(len(dict_)):
        attr = attrs_order[i]
        keys = list(dict_.keys())
        values = list(dict_.values())
        for key, value in zip(keys, values):
            if key == attr:
                dict_.pop(key)
                sorted_dict[key] = value
                break
        else:
            print(f"No se ha encontrado el atributo {key}")
    return sorted_dict
    

        
    