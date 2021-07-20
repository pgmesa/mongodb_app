
from pymongo import MongoClient
from bson.objectid import ObjectId

PORT = 27017
HOST = "localhost"

client = MongoClient(host=HOST, port=PORT)
# --------------------------------------------------------------------
# ----------------------- DATA BASE OPERATIONS -----------------------
def list_dbs() -> list[str]:
    dbs = client.list_database_names()
    return dbs

def rename_db(old_name:str, new_name:str) -> None:
    if old_name == new_name: return
    
    db = client[old_name]; db_dict = {}
    for col_name in db.list_collection_names():
        col = db[col_name]; docs = list(col.find({}))
        db_dict[col_name] = docs
    drop_db(old_name)
    
    new_db = client[new_name]
    for col_name, docs in db_dict.items():
        new_col = new_db[col_name]
        new_col.insert_many(docs)
    
def drop_db(db_name:str) -> None:
    client.drop_database(db_name)
    
# --------------------------------------------------------------------
# ----------------------- COLLECTION OPERATIONS ----------------------   
def add_collection(db_name:str, collection_name:str, model:dict) -> None:
    collection = client[db_name][collection_name]
    model_dict = {"_id": "model"}
    for attr, attr_dict in model.items():
        model_dict[attr] = attr_dict
    collection.insert_one(model_dict)
    
def list_collections(db_name:str, only_app_coll:bool=False) -> list[str]:
    db = client[db_name]
    collections = db.list_collection_names()
    if only_app_coll:
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

def update_model(db_name:str, collection_name:str, new_model:dict) -> None:
    old_model = get_model(db_name, collection_name)
    docs = get_documents(db_name, collection_name)
    if old_model is None: return
    old_model_dicts = list(old_model.values())
    old_model_names = []
    for attr_dict in old_model_dicts:
        old_model_names.append(attr_dict["name"])
    # Miramos los atributos nuevos que se han añadido y los que 
    for attr, attr_dict in new_model:
        if attr not in old_model:
            for doc in docs:
                doc[name] = ""
            continue
        name = attr_dict["name"]
        old_name = old_model[attr]["name"]
        if name != old_name and name not in old_model_names:
            for doc in docs:
                doc.pop(old_name)
                doc[name] = ""
        old_model.pop(attr)
    # Los que sigan estando en old_model es que se han eliminado
    deleted_attrs = old_model
    
    
    
    
    # Miramos los atributos nuevos que se han añadido y los que permanecen
    new_model_doc = {}; added_attrs = []
    for i, attr_dict in enumerate(new_model):
        new_model_doc[f"attr{i+1}"] = attr_dict
        attr_name = attr_dict["name"]
        if attr_name not in old_model_names:
            added_attrs.append(attr_name)
        else:
            old_model_names.remove(attr_name)
    # Los que sigan estando en old_model es que se han eliminado
    removed_attrs = old_model_names
    for doc in docs:
        for attr_name in added_attrs:
            doc[attr_name] = ""
        for attr_name in removed_attrs:
            doc.pop(attr_name)
        update_document(db_name, collection_name, doc["id"], doc)
    collection = client[db_name][collection_name]
    collection.replace_one({"_id": "model"}, new_model_doc)

def rename_collection(db_name:str, old_name:str, new_name:str) -> None:
    collection = client[db_name][old_name]
    collection.rename(new_name)
    
def remove_collecttion(db_name:str, collection_name:str) -> None:
    collection = client[db_name][collection_name]
    collection.drop()

# --------------------------------------------------------------------
# ------------------------ DOCUMENT OPERATIONS -----------------------
def get_documents(db_name:str, collection_name:str, queries:dict={}) -> list[dict]:
    collection = client[db_name][collection_name]
    docs = list(collection.find(queries))
    model = get_model(db_name, collection_name, with_id=True)
    if bool(model) and model in docs:
        docs.remove(model)
    for doc in docs:
        doc["id"] = str(doc["_id"])
        doc.pop("_id")
    return docs

def find_doc_by_id(db_name:str, collection_name:str, _id:str) -> list[dict]:
    return get_documents(db_name, collection_name, queries={"_id": ObjectId(_id)})[0]

def add_document(db_name:str, collection_name:str, doc:str) -> None:
    collection = client[db_name][collection_name]
    _id = doc.get("_id", None)
    if _id is not None and not isinstance(_id, ObjectId):
        doc["_id"] = ObjectId(_id)
    collection.insert_one(doc)
    
def update_document(db_name:str, collection_name:str, old_doc_id, new_doc:dict):
    # Actualizamos el documento
    col = client[db_name][collection_name]
    if "id" in new_doc:
        new_doc.pop("id")
    col.replace_one({"_id": ObjectId(old_doc_id)}, new_doc)
    
def delete_document(db_name:str, collection_name:str, doc_id:str) -> None:
    collection = client[db_name][collection_name]
    collection.delete_one({"_id": ObjectId(doc_id)})