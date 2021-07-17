
import json
from contextlib import suppress
# django imports
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.http.request import QueryDict
from django.shortcuts import render
# program imports
from controllers import db_controller as dbc


def clean_form(form:QueryDict) -> dict:
    cleaned = form.dict()
    with suppress(Exception):
        cleaned.pop("csrfmiddlewaretoken")
    
    return cleaned
        
# --------------------------------------------------------------------
# ------------------------- DATA BASE VIEWS --------------------------
def home(request:HttpRequest, extra_vars:dict={}) -> HttpResponse:
    client_ip = request.META['REMOTE_ADDR']; print(client_ip)
    context_dict = {}
    for var, val in extra_vars.items():
        context_dict[var] = val
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

def add_db(request:HttpRequest):
    context_dict = {}; post_dict = request.POST.dict()
    
    if bool(post_dict):
        try:
            dbs = dbc.list_dbs()
        except:
            err_msg = f"""Fallo al conectarse a la base de datos 
            (HOST={dbc.HOST}, PORT={dbc.PORT}), conexión rechazada"""
            context_dict["err_msg"] = err_msg
        else:
            new_db = post_dict['name']
            if new_db == "":
                err_msg = "Campo nombre obligatorio"
                context_dict["err_msg"] = err_msg
            elif new_db in dbs:
                err_msg = f"Este nombre ya esta usado"
                context_dict["err_msg"] = err_msg
            else:
                return HttpResponseRedirect(f'/add/{new_db}')
                
    context_dict["add_db"] = True
    return render(request, "add.html", context_dict)

def update_db(request:HttpRequest, db:str):
    context_dict = {"db": db}
    form_dict = request.POST.dict()
    if bool(form_dict):
        new_name = form_dict["name"]
        try:
            ex_dbs = dbc.list_dbs()
        except:
            err_msg = f"""Fallo al conectarse a la base de datos 
            (HOST={dbc.HOST}, PORT={dbc.PORT}), conexión rechazada"""
            context_dict["err_msg"] = err_msg
        else:
            new_name = form_dict['name']
            if new_name == "":
                err_msg = "Campo nombre obligatorio"
                context_dict["err_msg"] = err_msg
            elif new_name in ex_dbs and new_name != db:
                err_msg = ("Ya existe una coleccion en la base de datos " +
                        f"'{db}' con este nombre")
                context_dict["err_msg"] = err_msg
            else:
                dbc.rename_db(db, new_name)
                msg = (f"Base de Datos '{db}' actualizada con exito " + 
                        f"-> '{new_name}'")
                return home(request, extra_vars={"msg": msg})
            
    context_dict["update_db"] = True
    return render(request, "update.html", context_dict)

def delete_db(request:HttpRequest, db:str):
    context_dict = {"db": db}; conf_dict = clean_form(request.POST)
    if bool(conf_dict): 
        if "yes" in conf_dict:
            try:
                dbc.drop_db(db)
            except:
                err_msg = f"""Fallo al conectarse a la base de datos 
                (HOST={dbc.HOST}, PORT={dbc.PORT}), conexión rechazada"""
                context_dict["err_msg"] = err_msg
            else:
                msg = f"Base de Datos '{db}' eliminada con exito"
                context_dict["msg"] = msg
        else:
            err_msg = "Operacion cancelada"
            context_dict["err_msg"] = err_msg
            
        return home(request, extra_vars=context_dict)
    
    context_dict["delete_db"] = True
    return render(request, 'ask_confirmation.html', context_dict)


# --------------------------------------------------------------------
# ------------------------- COLLECTION VIEWS -------------------------
def display_collections(request:HttpRequest, db:str, extra_vars:dict={}):
    context_dict = {"db": db};
    for var, val in extra_vars.items():
        context_dict[var] = val
    try:
        collections = dbc.list_collections(db, all_coll=True)
        app_collections = dbc.list_collections(db)
    except:
        err_msg = f"""Fallo al conectarse a la base de datos 
        (HOST={dbc.HOST}, PORT={dbc.PORT}), conexión rechazada"""
        context_dict["err_msg"] = err_msg
    else:
        if not bool(collections):
            err_msg = "No existen colecciones en esta base de datos"
            context_dict["err_msg"] = err_msg
        else:
            context_dict["collections"] = True
            for col in app_collections:
                collections.remove(col)
            context_dict["app_collections"] = app_collections
            context_dict["not_app_collections"] = collections
    
    return render(request, 'collections.html', context_dict)

def add_collection(request:HttpRequest, db:str):
    context_dict = {"db": db}; post_dict = request.POST.dict()
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
        if "add" in form_dict:
            form_dict.pop("add")
            num = 1; tag = f"attr{num}"
            while tag in form_dict:
                num += 1
                tag = f"attr{num}"            
            form_dict[tag] = ""
        elif "remove" in form_dict:
            attr_to_rm = form_dict.pop("remove")
            if len(form_dict) == 1:
                err_msg = "La coleccion debe tener al menos algun atributo"
                context_dict["err_msg"] = err_msg
            else:
                form_dict.pop(attr_to_rm)
        elif "save" in form_dict:
            form_dict.pop("save")
            if dbc.get_model(db, collection) is not None:
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
            (HOST={dbc.HOST}, PORT={dbc.PORT}), conexión rechazada"""
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
                return display_collections(request, db, extra_vars={"msg": msg})
    
    context_dict["update_collection"] = True
    return render(request, "update.html", context_dict)

def delete_collection(request:HttpRequest, db:str, collection:str):
    context_dict = {"db": db, "collection": collection}
    conf_dict = clean_form(request.POST)
    if bool(conf_dict): 
        if "yes" in conf_dict:
            try:
                dbc.remove_collecttion(db, collection)
            except:
                err_msg = f"""Fallo al conectarse a la base de datos 
                (HOST={dbc.HOST}, PORT={dbc.PORT}), conexión rechazada"""
                context_dict["err_msg"] = err_msg
            else:
                msg = f"Coleccion '{collection}' eliminada con exito"
                context_dict["msg"] = msg
        else:
            err_msg = "Operacion cancelada"
            context_dict["err_msg"] = err_msg
    
        return display_collections(request, db, extra_vars=context_dict)
    
    context_dict["delete_collection"] = True
    return render(request, 'ask_confirmation.html', context_dict)

# --------------------------------------------------------------------
# -------------------------- DOCUMENT VIEWS --------------------------
def display_documents(request:HttpRequest, db:str, collection:str , extra_vars:dict={}):
    context_dict = {"db": db, "collection": collection}
    for var, val in extra_vars.items():
        context_dict[var] = val
    try:
        docs = dbc.get_documents(db, collection)
    except:
        err_msg = f"""Fallo al conectarse a la base de datos 
        (HOST={dbc.HOST}, PORT={dbc.PORT}), conexión rechazada"""
        context_dict["err_msg"] = err_msg
    else:
        # Miramos si hay que eliminar todos los docs
        clear_form = clean_form(request.POST)
        if bool(clear_form) and "clear" in clear_form:
            for doc in docs:
                dbc.delete_document(db, collection, doc["id"])
            docs = dbc.get_documents(db, collection)
            if not bool(docs):
                msg = "Coleccion vaciada con exito"
                context_dict["msg"] = msg
        # if "yes" in clear_form:
        #     for doc in docs:
        #         dbc.delete_document(db, collection, doc["id"])
        #     docs = dbc.get_documents(db, collection)
        #     if not bool(docs):
        #         msg = "Coleccion vaciada con exito"
        #         context_dict["msg"] = msg
        # elif "no" in clear_form:
        #     err_msg = "Operacion cancelada"
        #     context_dict["err_msg"] = err_msg
        # elif bool(clear_form) and "clear" in clear_form:
        #     context_dict["delete_docs"] = True
        #     context_dict["form_path"] = f'/display/{db}/{collection}'
        #     return render(request, 'ask_confirmation.html', context_dict)
        # Mostramos los documentos segun si hay o no hay modelo establecido
        model_doc = dbc.get_model(db, collection)
        if bool(model_doc):
            context_dict["model"] = list(model_doc.values())
            if not bool(docs):
                err_msg = "No existen documentos en esta coleccion"
                context_dict["err_msg"] = err_msg
            else:
                context_dict["docs"] = docs
        else:
            num = 20; context_dict["show_more"] = True
            form_dict = clean_form(request.GET); docs_len = len(docs)
            if "show_more" in form_dict:
                num = int(form_dict["show_more"]) + 10
            if num >= docs_len: 
                num = docs_len
                context_dict.pop("show_more")
            context_dict["num"] = num
            context_dict["docs_len"] = docs_len
            
            str_docs = []
            for i, doc in enumerate(docs):
                if i == num: break
                for attr, value in doc.items():
                    doc[attr] = str(value)
                str_doc = json.dumps(doc, indent=4, sort_keys=True)
                str_docs.append(str_doc)
            context_dict["docs"] = str_docs
    
    return render(request, 'documents.html', context_dict)

def add_document(request:HttpRequest, db:str, collection:str):
    context_dict = {"db": db, "collection": collection}
    form_dict = request.POST.dict()
    
    if bool(form_dict):
        form_dict.pop("csrfmiddlewaretoken")
        doc = form_dict
        dbc.add_document(db, collection, doc)
        msg = "Documento añadido con exito"
        return display_documents(request, db, collection, extra_vars={"msg": msg})
    else:
        try:
            model = dbc.get_model(db, collection)
        except:
            err_msg = f"""Fallo al conectarse a la base de datos 
            (HOST={dbc.HOST}, PORT={dbc.PORT}), conexión rechazada"""
            context_dict["err_msg"] = err_msg
        else:
            context_dict["model"] = model.values()
    
    context_dict["add_doc"] = True
    return render(request, 'add.html', context_dict)

def update_document(request:HttpRequest, db:str, collection:str, doc_id:str):
    context_dict = {"db": db, "collection": collection}
    doc = dbc.find_doc_by_id(db, collection, doc_id)
    context_dict["doc"] = doc
    
    form_dict = clean_form(request.POST)
    if bool(form_dict):
        new_doc = form_dict
        try:
            dbc.update_document(db, collection, doc_id, new_doc)
        except IndexError:
            err_msg = f"""Fallo al conectarse a la base de datos 
            (HOST={dbc.HOST}, PORT={dbc.PORT}), conexión rechazada"""
            context_dict["err_msg"] = err_msg
        else:
            msg = (f"Documento con id '{doc_id}' actualizado con exito")
            return display_documents(request, db, collection, extra_vars={"msg": msg})
    
    context_dict["update_doc"] = True
    return render(request, "update.html", context_dict)

def delete_document(request:HttpRequest, db:str, collection:str, doc_id:str):
    context_dict = {}
    try:
        dbc.delete_document(db, collection, doc_id)
    except:
        err_msg = f"""Fallo al conectarse a la base de datos 
        (HOST={dbc.HOST}, PORT={dbc.PORT}), conexión rechazada"""
        context_dict["err_msg"] = err_msg
    else:
        msg = f"Documento con id '{doc_id}' eliminado con exito"
        context_dict["msg"] = msg
    
    return display_documents(request, db, collection, extra_vars=context_dict)

def filter_documents():
    ...
    
def sort_documents():
    ...
    
    