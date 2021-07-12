
from contextlib import suppress
# django imports
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.shortcuts import render
# program imports
from controllers import db_controller as dbc

# --------------------------------------------------------------------
# ------------------------- DATA BASE VIEWS --------------------------
def home(request:HttpRequest) -> HttpResponse:
    client_ip = request.META['REMOTE_ADDR']; print(client_ip)
    context_dict = {}
    try:
        dbs = dbc.list_dbs()
    except:
        err_msg = f"""Fallo al conectarse a  mongodb  
        (HOST={dbc.HOST}, PORT={dbc.PORT}), conexión rechazada"""
        context_dict["err_msg"] = err_msg
    else:
        context_dict["dbs"] = dbs
    response:HttpResponse = render(request, 'home.html', context_dict)
    return response

def add_db(request:HttpRequest, db:str):
    ...

def update_db(request:HttpRequest, db:str):
    context_dict = {"db": db}
    
    context_dict["update_db"] = True
    return render(request, "update.html", context_dict)

# --------------------------------------------------------------------
# ------------------------- COLLECTION VIEWS -------------------------
def display_collections(request:HttpRequest, db:str, extra_vars:dict={}):
    context_dict = {"db": db};
    for var, val in extra_vars.items():
        context_dict[var] = val
    try:
        collections = dbc.list_collections(db)
    except:
        err_msg = f"""Fallo al conectarse a la base de datos 
        (HOST={dbc.HOST}, PORT={dbc.PORT}), conexión rechazada"""
        context_dict["err_msg"] = err_msg
    else:
        if not bool(collections):
            err_msg = "No existen colecciones en esta base de datos"
            context_dict["err_msg"] = err_msg
        else:
            context_dict["collections"] = collections
    
    return render(request, 'collections.html', context_dict)

def add_collection(request:HttpRequest, db:str):
    context_dict = {"db": db}; post_dict = request.POST.dict()
    print(post_dict)
    # return create_model(request, "prueba")
    # Procesamos peticion POST
    if bool(post_dict):
        try:
            collections = dbc.list_collections(db)
        except:
            err_msg = f"""Fallo al conectarse a la base de datos 
            (HOST={dbc.HOST}, PORT={dbc.PORT}), conexión rechazada"""
            context_dict["err_msg"] = err_msg
        else:
            new_collection = post_dict['name']
            if new_collection == "":
                err_msg = "Campo nombre obligatorio"
                context_dict["err_msg"] = err_msg
            elif new_collection in collections:
                err_msg = f"Este nombre ya esta usado"
                context_dict["err_msg"] = err_msg
            else:
                return HttpResponseRedirect(f'/doc_model/{db}/{new_collection}')
                
    context_dict["add_collection"] = True
    return render(request, "add.html", context_dict)
    
def create_doc_model(request:HttpRequest, db:str, collection:str):
    context_dict = {"db": db, "collection": collection, "attrs":{"attr1": ""}}
    form_dict = request.POST.dict()
    if bool(form_dict):
        form_dict.pop("csrfmiddlewaretoken")
        print(form_dict)
        if "add" in form_dict:
            form_dict.pop("add")
            num = 1; tag = f"attr{num}"
            while tag in form_dict:
                num += 1
                tag = f"attr{num}"            
            form_dict[tag] = ""
        elif "remove" in form_dict:
            attr_to_rm = form_dict.pop("remove")
            print(form_dict)
            if len(form_dict) == 1:
                err_msg = "La coleccion debe tener al menos algun atributo"
                context_dict["err_msg"] = err_msg
            else:
                form_dict.pop(attr_to_rm)
        elif "save" in form_dict:
            form_dict.pop("save")
            if dbc.is_model_defined(db, collection):
                err_msg = f"La coleccion '{collection}' ya tiene un modelo creado"
                context_dict["err_msg"] = err_msg
            else:
                model = {"_id": "model"}; i = 1
                for attr in form_dict:
                    value = form_dict[attr]
                    if value != "":
                        model[f"attr{i}"] = value
                        i += 1
                if len(model) == 1:
                    err_msg = "La coleccion debe tener al menos algun atributo no vacio"
                    context_dict["err_msg"] = err_msg
                else:
                    dbc.add_collection(db, collection, model)
                    msg = f"Coleccion '{collection}' añadida con exito"
                    return display_collections(request, db, extra_vars={"msg": msg})
        context_dict["attrs"] = form_dict
    print(form_dict)
    response = render(request, "create_doc_model.html", context_dict)
    return response

def update_collection(request:HttpRequest, db:str, collection:str):
    context_dict = {"db": db, "collection": collection}
    form_dict = request.POST.dict()
    if bool(form_dict):
        new_name = form_dict["name"]
        try:
            ex_collections = dbc.list_collections(db)
        except:
            err_msg = f"""Fallo al conectarse a la base de datos 
            (HOST={db.HOST}, PORT={db.PORT}), conexión rechazada"""
            context_dict["err_msg"] = err_msg
        else:
            new_name = form_dict['name']
            if new_name == "":
                err_msg = "Campo nombre obligatorio"
                context_dict["err_msg"] = err_msg
            elif new_name in ex_collections and new_name != collection:
                err_msg = ("Ya existe una coleccion en la base de datos " +
                        f"'{db}' con este nombre")
                context_dict["err_msg"] = err_msg
            else:
                dbc.rename_collection(db, collection, new_name)
                msg = (f"Coleccion '{collection}' actualizada con exito " + 
                        f"-> '{new_name}'")
                context_dict["msg"] = msg
                return display_collections(request, db, extra_vars={"msg": msg})
    
    context_dict["update_collection"] = True
    return render(request, "update.html", context_dict)

def delete_collection(request:HttpRequest, db:str, collection:str):
    context_dict = {}
    form_dict = request.POST.dict()
    try:
        dbc.remove_collecttion(db, collection)
    except:
        err_msg = f"""Fallo al conectarse a la base de datos 
        (HOST={dbc.HOST}, PORT={dbc.PORT}), conexión rechazada"""
        context_dict["err_msg"] = err_msg
    else:
        msg = f"Coleccion '{collection}' eliminada con exito"
        context_dict["msg"] = msg
    
    return display_collections(request, db, extra_vars=context_dict)

# --------------------------------------------------------------------
# -------------------------- DOCUMENT VIEWS --------------------------
def display_documents(request:HttpRequest, db:str, collection:str):
    context_dict = {"db": db, "collection": collection};
    try:
        docs = dbc.get_documents(db, collection)
    except:
        err_msg = f"""Fallo al conectarse a la base de datos 
        (HOST={dbc.HOST}, PORT={dbc.PORT}), conexión rechazada"""
        context_dict["err_msg"] = err_msg
    else:
        model_doc = {}
        for doc in docs:
            with suppress(Exception):
                if doc["_id"] == "model":
                    model_doc = doc
                    break
        if bool(model_doc):
            docs.remove(model_doc)
            if not bool(docs):
                err_msg = "No existen documentos en esta coleccion"
                context_dict["err_msg"] = err_msg
            else:
                context_dict["docs"] = docs
        else:
            err_msg = ("Esta coleccion se ha creado desde fuera de la aplicacion, " + 
                        "no se ha especificado un modelo")
            context_dict["err_msg"] = err_msg
            # Preguntar si intentar desplegar pero sin opcion a añadir y pudiendo verse mal
            ...
    
    return render(request, 'documents.html', context_dict)