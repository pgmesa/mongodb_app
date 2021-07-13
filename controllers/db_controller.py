
from pymongo import MongoClient
import pymongo

PORT = 27017
HOST = "localhost"

client = MongoClient(host=HOST, port=PORT)
# --------------------------------------------------------------------
# ----------------------- DATA BASE OPERATIONS -----------------------
def add_db(db_name:str) -> None:
    db = client[db_name]
    # collection = db["prueba"]
    # collection.insert_one({
    #     "name": "prueba"
    # })

def list_dbs() -> list[str]:
    dbs = client.list_database_names()
    
    return dbs

def rename_db(old_name:str, new_name:str) -> None:
    db = client[old_name]
    if old_name == new_name: return
    col = db[old_name]
    col.rename(new_name)
    
def drop_db(db_name:str) -> None:
    client.drop_database(db_name)
    
# --------------------------------------------------------------------
# ----------------------- COLLECTION OPERATIONS ----------------------   
def add_collection(db_name:str, collection_name:str, model:dict) -> None:
    collection = client[db_name][collection_name]
    collection.insert_one(model)
    
def list_collections(db_name:str, all_coll:bool=False) -> list[str]:
    db = client[db_name]
    collections = db.list_collection_names()
    if not all_coll:
        filtered = []
        for coll in collections:
            model = get_model(db_name, coll)
            if model is not None:
                filtered.append(coll)
        collections = filtered
        
    return collections
    
def get_model(db_name:str, collection_name:str, with_id=False) -> dict or None:
    collection = client[db_name][collection_name]
    model = list(collection.find({"_id": "model"}))
    if not bool(model):
        model = None
    else:
        model = model[0] 
        if not with_id:
            model.pop("_id")
    return model

def rename_collection(db_name:str, old_name:str, new_name:str) -> None:
    collection = client[db_name][old_name]
    collection.rename(new_name)
    
def remove_collecttion(db_name:str, collection_name:str) -> None:
    collection = client[db_name][collection_name]
    collection.drop()

# --------------------------------------------------------------------
# ------------------------ DOCUMENT OPERATIONS -----------------------
def get_documents(db_name:str, collection_name:str) -> list[dict]:
    collection = client[db_name][collection_name]
    docs = list(collection.find({}))
    model = get_model(db_name, collection_name, with_id=True)
    print(model)
    if bool(model):
        docs.remove(model)
    return docs

def add_document(db_name:str, collection_name:str, doc:str) -> None:
    collection = client[db_name][collection_name]
    collection.insert_one(doc)