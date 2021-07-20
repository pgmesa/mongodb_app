
import json
from contextlib import suppress
# django imports
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.http.request import QueryDict
from django.shortcuts import render
# program imports
from controllers import db_controller as dbc


def _clean_form(form:QueryDict) -> dict:
    cleaned = form.dict()
    with suppress(Exception):
        cleaned.pop("csrfmiddlewaretoken")
    
    return cleaned

_extra_vars = {}
def _get_extra_vars(view_name:str) -> dict:
    global _extra_vars
    extra_vars = _extra_vars.get(view_name, None)
    if extra_vars is None:
        extra_vars = {}
    else:
        _extra_vars.pop(view_name)
    
    return extra_vars

def _set_extra_vars(extra_vars:dict, view_name:str) -> None:
    global _extra_vars
    ex_extra_vars = _extra_vars.get(view_name, None)
    if not bool(ex_extra_vars):
        _extra_vars[view_name] = extra_vars
    else:
        for var, value in extra_vars:
            _extra_vars[view_name][var] = value
    
# --------------------------------------------------------------------
# ------------------------- DATA BASE VIEWS --------------------------
def home(request:HttpRequest) -> HttpResponse:
    client_ip = request.META['REMOTE_ADDR']; print(client_ip)
    context_dict = _get_extra_vars("home")
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
            elif " " in new_db:
                err_msg = f"El nombre no puede contener espacios en blanco"
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
            elif " " in new_name:
                err_msg = f"El nombre no puede contener espacios en blanco"
                context_dict["err_msg"] = err_msg
            else:
                dbc.rename_db(db, new_name)
                msg = (f"Base de Datos '{db}' actualizada con exito " + 
                        f"-> '{new_name}'")
                _set_extra_vars({"msg": msg}, "home")
                return HttpResponseRedirect("/")
            
    context_dict["update_db"] = True
    return render(request, "update.html", context_dict)

def delete_db(request:HttpRequest, db:str):
    context_dict = {"db": db}; conf_dict = _clean_form(request.POST)
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
            
        _set_extra_vars(context_dict, "home")
        return HttpResponseRedirect("/")
    
    context_dict["delete_db"] = True
    return render(request, 'ask_confirmation.html', context_dict)

# --------------------------------------------------------------------
# ------------------------- COLLECTION VIEWS -------------------------
def display_collections(request:HttpRequest, db:str):
    context_dict = _get_extra_vars("display_collections")
    context_dict["db"] = db
    try:
        collections = dbc.list_collections(db)
        app_collections = dbc.list_collections(db, only_app_coll=True)
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
                _set_extra_vars({"add_model": True}, "create_doc_model")
                return HttpResponseRedirect(f'/doc_model/{db}/{new_collection}')
                
    context_dict["add_collection"] = True
    return render(request, "add.html", context_dict)
    
def create_doc_model(request:HttpRequest, db:str, collection:str):
    context_dict = {"db": db, "collection": collection, "model":{"attr1": {"name": "","type": ""}}}
    extra_vars = _get_extra_vars("create_doc_model")
    for var, value in extra_vars.items():
        context_dict[var] = value
    ex_model = dbc.get_model(db, collection)
    if ex_model is not None:
        context_dict["model"] = ex_model
        if "num_attrs" not in context_dict:
            context_dict["num_attrs"] = len(ex_model)

    def process_model_from_form(form:dict) -> dict:
        attrs = []; types = []; model = {}
        for inpt in form_dict:
            if "type" in inpt:
                types.append(inpt)
            else:
                attrs.append(inpt)
        for attr in attrs:
            attr_dict = {"name": form_dict[attr], "type": ""}
            for tp in types:
                if attr in tp:
                    attr_dict["type"] = form_dict[tp]
                    break
            model[attr] = attr_dict
        return model
    
    form_dict = _clean_form(request.POST)
    if bool(form_dict):
        if "add" in form_dict:
            form_dict.pop("add")
            context_dict["num_attrs"] += 1
            num_attrs = context_dict["num_attrs"]
            model = process_model_from_form(form_dict)
            new_attr = f"attr{num_attrs}"            
            model[new_attr] = {"name": "","type": ""}
        elif "remove" in form_dict:
            attr_to_rm = form_dict.pop("remove")
            model = process_model_from_form(form_dict)
            if len(model) == 1:
                err_msg = "La coleccion debe tener al menos algun atributo"
                context_dict["err_msg"] = err_msg
            else:
                model.pop(attr_to_rm)
        elif "up" in form_dict:
            attr_to_move_up = form_dict.pop("up")
            model = process_model_from_form(form_dict)
            attrs = list(model.keys()); 
            index_to_move_up = attrs.index(attr_to_move_up)
            if index_to_move_up > 0:
                index_to_move_down = index_to_move_up-1
                attr_to_move_down = attrs[index_to_move_down]
                sorted_model = {}; i = 0
                for attr, attr_dict in model.items():
                    if i == index_to_move_down:
                        pass
                    elif i == index_to_move_up:
                        old_down = attr_dict
                        old_up = model[attr_to_move_down]
                        sorted_model[attr_to_move_up] = old_down
                        sorted_model[attr_to_move_down] = old_up
                    else:
                        sorted_model[attr] = attr_dict
                    i += 1
                model = sorted_model
        elif "down" in form_dict:
            attr_to_move_down = form_dict.pop("down")
            model = process_model_from_form(form_dict)
            attrs = list(model.keys()); 
            index_to_move_down = attrs.index(attr_to_move_down)
            if index_to_move_down < len(model) - 1:
                index_to_move_up = index_to_move_down+1
                attr_to_move_up = attrs[index_to_move_up]
                sorted_model = {}; i = 0
                for attr, attr_dict in model.items():
                    if i == index_to_move_down:
                        pass
                    elif i == index_to_move_up:
                        old_down = attr_dict
                        old_up = model[attr_to_move_down]
                        sorted_model[attr_to_move_up] = old_down
                        sorted_model[attr_to_move_down] = old_up
                    else:
                        sorted_model[attr] = attr_dict
                    i += 1
                model = sorted_model
        elif "save" in form_dict:
            form_dict.pop("save") 
            submitted_model = process_model_from_form(form_dict)
            attrs_names = []
            for attr_dict in submitted_model.values():
                attrs_names.append(attr_dict["name"])
            # Realizamos una comprobacion previa de parametros
            valid_model = {}; valid = True
            for attr, attr_dict in submitted_model.items():
                name = attr_dict["name"]; attrs_names.remove(name)
                if name == "id" or name == "_id":
                    err_msg = f"El nombre de atributo '{name}' no esta permitido"
                    context_dict["err_msg"] = err_msg
                    valid = False
                elif name in attrs_names and name != "":
                    err_msg = f"El atributo '{name}' esta repetido"
                    context_dict["err_msg"] = err_msg
                    valid = False
                elif name == "":
                    err_msg = "No pueden haber atributos vacios"
                    context_dict["err_msg"] = err_msg
                    valid = False
                else:
                    valid_model[attr] = attr_dict
            if valid:
                if ex_model is not None:
                    dbc.update_model(db, collection, valid_model)
                    msg = f"""El modelo de la coleccion '{collection}' ha sido 
                    actualizado con exito"""
                    _set_extra_vars({"msg": msg}, "display_documents")
                    return HttpResponseRedirect(f"/display/{db}/{collection}")
                else:
                    dbc.add_collection(db, collection, valid_model)
                    msg = f"Coleccion '{collection}' añadida con exito"
                    _set_extra_vars({"msg": msg}, "display_collections")
                    return HttpResponseRedirect(f"/display/{db}")
            model = submitted_model
        _set_extra_vars({"num_attrs": context_dict["num_attrs"]}, "create_doc_model")
        context_dict["model"] = model
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
                _set_extra_vars({"msg": msg}, "display_collections")
                return HttpResponseRedirect(f"/display/{db}")
    
    context_dict["update_collection"] = True
    return render(request, "update.html", context_dict)

def delete_collection(request:HttpRequest, db:str, collection:str):
    context_dict = {"db": db, "collection": collection}
    conf_dict = _clean_form(request.POST)
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
        
        _set_extra_vars(context_dict, "display_collections")
        return HttpResponseRedirect(f"/display/{db}")
    
    context_dict["delete_collection"] = True
    return render(request, 'ask_confirmation.html', context_dict)

# --------------------------------------------------------------------
# -------------------------- DOCUMENT VIEWS --------------------------
def display_documents(request:HttpRequest, db:str, collection:str , extra_vars:dict={}):
    context_dict = {"db": db, "collection": collection}
    extra_vars = _get_extra_vars("display_documents")
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
        clear_form = _clean_form(request.POST)
        if "yes" in clear_form:
            for doc in docs:
                dbc.delete_document(db, collection, doc["id"])
            docs = dbc.get_documents(db, collection)
            if not bool(docs):
                msg = "Coleccion vaciada con exito"
                context_dict["msg"] = msg
        elif "no" in clear_form:
            err_msg = "Operacion cancelada"
            context_dict["err_msg"] = err_msg
        elif bool(clear_form) and "clear" in clear_form:
            context_dict["delete_docs"] = True
            return render(request, 'ask_confirmation.html', context_dict)
        # Mostramos los documentos segun si hay o no hay modelo establecido
        model_doc = dbc.get_model(db, collection)
        if bool(model_doc):
            context_dict["model"] = model_doc
            if not bool(docs):
                err_msg = "No existen documentos en esta coleccion"
                context_dict["err_msg"] = err_msg
            else:
                docs = docs[::-1]
                context_dict["docs"] = docs
        else:
            num = 20; context_dict["show_more"] = True
            form_dict = _clean_form(request.GET); docs_len = len(docs)
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
    form_dict = _clean_form(request.POST)
    if bool(form_dict):
        doc = form_dict
        dbc.add_document(db, collection, doc)
        msg = "Documento añadido con exito"
        _set_extra_vars({"msg": msg}, "display_documents")
        return HttpResponseRedirect(f"/display/{db}/{collection}")
    else:
        try:
            model = dbc.get_model(db, collection)
        except:
            err_msg = f"""Fallo al conectarse a la base de datos 
            (HOST={dbc.HOST}, PORT={dbc.PORT}), conexión rechazada"""
            context_dict["err_msg"] = err_msg
        else:
            context_dict["model"] = model
    
    context_dict["add_doc"] = True
    return render(request, 'add.html', context_dict)

def update_document(request:HttpRequest, db:str, collection:str, doc_id:str):
    context_dict = {"db": db, "collection": collection}
    doc = dbc.find_doc_by_id(db, collection, doc_id)
    context_dict["doc"] = doc
    context_dict["model"] = dbc.get_model(db, collection)
    
    form_dict = _clean_form(request.POST)
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
            _set_extra_vars({"msg": msg}, "display_documents")
            return HttpResponseRedirect(f"/display/{db}/{collection}")
    
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
    
    _set_extra_vars(context_dict, "display_documents")
    return HttpResponseRedirect(f"/display/{db}/{collection}")

def filter_documents():
    ...
    
def sort_documents():
    ...
    
    