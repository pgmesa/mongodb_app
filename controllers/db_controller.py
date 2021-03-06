
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId

PORT = 27017
HOST = "localhost"

client = MongoClient(host=HOST, port=PORT)
# --------------------------------------------------------------------
# ----------------------- DATABASE OPERATIONS -----------------------
def list_dbs(only_app_dbs:bool=False) -> list[str]:
    dbs = client.list_database_names()
    if only_app_dbs:
        filtered = []
        for db in dbs:
            if bool(list_collections(db, only_app_coll=True)):
                filtered.append(db)
            dbs = filtered
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
def get_password_info(db_name:str, collection_name:str, encrypted_pw:str):
    passwords = get_passwords(db_name, collection_name)
    pw_info = passwords.get(encrypted_pw, None)
    if pw_info is not None:
        pw_info = pw_info["encryption_info"]
    return pw_info

def get_passwords(db_name:str, collection_name:str, with_id=False) -> dict or None:
    collection = client[db_name][collection_name]
    passwords = list(collection.find({"_id": "passwords"}))
    if not bool(passwords):
        passwords = {}
    else:
        passwords = passwords[0] 
        if not with_id:
            passwords.pop("_id")
    return passwords

def add_password(db_name:str, collection_name:str, enc_password:str, pw_info:dict):
    collection = client[db_name][collection_name]
    passwords = get_passwords(db_name, collection_name)
    if bool(passwords):
        passwords.update({enc_password: pw_info})
        # Guardamos las contrase??as
        collection.replace_one({"_id": "passwords"}, passwords)
    else:
        passwords = {"_id": "passwords", enc_password: pw_info}
        # Guardamos las contrase??as
        collection.insert_one(passwords)
        
def delete_password(db_name:str, collection_name:str, enc_password:str):
    collection = client[db_name][collection_name]
    passwords = get_passwords(db_name, collection_name)
    if bool(passwords) and enc_password in passwords:
        passwords.pop(enc_password)
    else:
        return
    if len(passwords) == 0:
        collection.delete_one({"_id": "passwords"})
    else:
        collection.replace_one({"_id": "passwords"}, passwords)

def _get_type(type_name:str):
    if type_name == 'str':
        type_func = str
    elif type_name == 'int':
        type_func = int
    elif type_name == 'float':
        type_func = float
    return type_func

def update_model(db_name:str, collection_name:str, new_model:dict, override_types:bool=False) -> None:
    old_model = get_model(db_name, collection_name)
    docs = get_documents(db_name, collection_name)
    if old_model is None: return
    # Miramos que atributos antiguos se han eliminado o modificado
    for attr, attr_dict in old_model.items():
        old_name = attr_dict["name"]
        old_type = attr_dict["type"]
        if attr in new_model:
            new_name = new_model[attr]["name"]
            new_type = new_model[attr]["type"]
            if old_name != new_name:
                for doc in docs:
                    value = doc.pop(old_name)
                    doc[new_name] = value
            if old_type != new_type or override_types:
                for doc in docs:
                    type_func = _get_type(new_type)
                    value = doc[new_name]
                    if value != "" and value != "-":
                        try:
                            parsed = type_func(value)
                        except Exception as err:
                            if type_func is int:
                                try:
                                    parsed = float(value)
                                    parsed = int(parsed)
                                except:
                                    raise err
                        doc[new_name] = parsed
        else:
            for attr_dict in new_model.values():
                if old_name == attr_dict["name"]:
                    break
            else: 
                for doc in docs:
                    doc.pop(old_name)   
    # Miramos que atributos nuevos se han a??adido
    for attr, attr_dict in new_model.items():
        if attr not in old_model:
            added_name = attr_dict["name"]
            for doc in docs:
                doc[added_name] = "-"
    # Nombramos bien los atributos del nuevo modelo
    new_model_ordered = {}
    attr_dicts = list(new_model.values())
    for i, attr_dict in enumerate(attr_dicts):
        new_model_ordered[f"attr{i+1}"] = attr_dict
    # Guardamos las actualizaciones de los documentos
    for doc in docs:
        # No usar update_document(), el model se va a actualizar despues
        col = client[db_name][collection_name]
        doc_id = doc.pop("id")
        col.replace_one({"_id": ObjectId(doc_id)}, doc)
    # Guardamos el nuevo modelo renombrado
    collection = client[db_name][collection_name]
    collection.replace_one({"_id": "model"}, new_model_ordered)

def rename_collection(db_name:str, old_name:str, new_name:str) -> None:
    collection = client[db_name][old_name]
    collection.rename(new_name)
    
def remove_collecttion(db_name:str, collection_name:str) -> None:
    collection = client[db_name][collection_name]
    collection.drop()

# --------------------------------------------------------------------
# ------------------------ DOCUMENT OPERATIONS -----------------------
def get_documents(db_name:str, collection_name:str, queries:dict={},
                  sort_dict:dict={}, invert_sort=False, with_app_format=True) -> list[dict]:
    collection = client[db_name][collection_name]
    if bool(sort_dict):
        sort_list = []
        for attr, value in sort_dict.items():
            if value == 'asc':
                if invert_sort: operator = pymongo.DESCENDING
                else: operator = pymongo.ASCENDING
            elif value == 'desc':
                if invert_sort: operator = pymongo.ASCENDING
                else: operator = pymongo.DESCENDING
            sort_list.append((attr, operator))
        docs = list(collection.find(queries).sort(sort_list))
    else:
        docs = list(collection.find(queries))
    if with_app_format:
        model = get_model(db_name, collection_name, with_id=True)
        if bool(model) and model in docs:
            docs.remove(model)
        passwords = get_passwords(db_name, collection_name, with_id=True)
        if bool(passwords) and passwords in docs:
            docs.remove(passwords)
        for doc in docs:
            doc["id"] = str(doc["_id"])
            doc.pop("_id")
    else:
        for doc in docs:
            doc["_id"] = str(doc["_id"])
    return docs

def find_doc_by_id(db_name:str, collection_name:str, _id:str) -> dict:
    return get_documents(db_name, collection_name, queries={"_id": ObjectId(_id)})[0]

def add_document(db_name:str, collection_name:str, doc:str) -> None:
    collection = client[db_name][collection_name]
    _id = doc.get("_id", None)
    if _id is not None and not isinstance(_id, ObjectId) and _id != "model" and _id != "passwords":
        doc["_id"] = ObjectId(_id)
    collection.insert_one(doc)
    
def update_document(db_name:str, collection_name:str, old_doc_id, new_doc:dict):
    # Actualizamos el documento
    col = client[db_name][collection_name]
    if "id" in new_doc:
        new_doc.pop("id")
    # Miramos si se ha a??adido una nueva contrase??a al registro (se ha actualizado 
    # la vieja) para eliminar la antigua
    model = get_model(db_name, collection_name)
    old_doc = find_doc_by_id(db_name, collection_name, old_doc_id)
    if bool(model):
        for attr_dict in model.values():
            name = attr_dict["name"]
            old_val = old_doc[name]; new_val = new_doc.get(name, None)
            if attr_dict["type"] == "password" and old_val != new_val:
                delete_password(db_name, collection_name, old_val)
                
    col.replace_one({"_id": ObjectId(old_doc_id)}, new_doc)
    
def delete_document(db_name:str, collection_name:str, doc_id:str, delete_pwds=True) -> None:
    collection = client[db_name][collection_name]
    if delete_pwds:
        doc = find_doc_by_id(db_name, collection_name, doc_id)
        model = get_model(db_name, collection_name)
        if bool(model):
            for attr_dict in model.values():
                name = attr_dict["name"]
                if attr_dict["type"] == "password":
                    enc_pw = doc[name]
                    delete_password(db_name, collection_name, enc_pw)
                
    collection.delete_one({"_id": ObjectId(doc_id)})