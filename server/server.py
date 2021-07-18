
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
    context_dict = {"db": db, "collection": collection, "model":{"attr1": {"name": "","type": ""}}}
    ex_model = dbc.get_model(db, collection)
    if ex_model is not None:
        context_dict["model"] = ex_model
    print(ex_model)
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
            model = process_model_from_form(form_dict)
            num = 1; new_attr = f"attr{num}"
            while new_attr in model:
                num += 1
                new_attr = f"attr{num}"            
            model[new_attr] = {"name": "","type": ""}
        elif "remove" in form_dict:
            attr_to_rm = form_dict.pop("remove")
            model = process_model_from_form(form_dict)
            if len(model) == 1:
                err_msg = "La coleccion debe tener al menos algun atributo"
                context_dict["err_msg"] = err_msg
            else:
                model.pop(attr_to_rm)
        elif "save" in form_dict:
            form_dict.pop("save") 
            submitted_model = process_model_from_form(form_dict)
            print(submitted_model)
            attrs_names = []
            for attr_dict in submitted_model.values():
                attrs_names.append(attr_dict["name"])
            print(attrs_names)
            # Realizamos una comprobacion previa de parametros
            valid_model = {}
            for attr, attr_dict in submitted_model.items():
                name = attr_dict["name"]; attrs_names.remove(name)
                if name == "id" or name == "_id":
                    err_msg = f"El nombre de atributo '{name}' no esta permitido"
                    context_dict["err_msg"] = err_msg
                    break
                elif name in attrs_names:
                    err_msg = f"El atributo '{name}' esta repetido"
                    context_dict["err_msg"] = err_msg
                    break
                elif name != "":
                    valid_model[attr] = attr_dict
            else:
                print(valid_model)
                if len(valid_model) == 0:
                    err_msg = "La coleccion debe tener al menos algun atributo no vacio"
                    context_dict["err_msg"] = err_msg
                elif ex_model is not None:
                    dbc.update_model(db, collection, valid_model.values())
                    msg = f"""El modelo de la coleccion '{collection}' ha sido 
                    actualizado con exito"""
                    _set_extra_vars({"msg": msg}, "display_documents")
                    return HttpResponseRedirect(f"/display/{db}/{collection}")
                else:
                    dbc.add_collection(db, collection, valid_model.values())
                    msg = f"Coleccion '{collection}' añadida con exito"
                    _set_extra_vars({"msg": msg}, "display_collections")
                    return HttpResponseRedirect(f"/display/{db}")
            model = valid_model
        context_dict["model"] = model
    response = render(request, "create_doc_model.html", context_dict)
    return response

# def create_doc_model(request:HttpRequest, db:str, collection:str):
#     context_dict = {"db": db, "collection": collection, "attrs":{"attr1": ""}}
#     model = dbc.get_model(db, collection)
#     if model is not None:
#         context_dict["attrs"] = model
#     form_dict = _clean_form(request.POST)
#     if bool(form_dict):
#         if "add" in form_dict:
#             form_dict.pop("add")
#             num = 1; tag = f"attr{num}"
#             while tag in form_dict:
#                 num += 1
#                 tag = f"attr{num}"            
#             form_dict[tag] = ""
#         elif "remove" in form_dict:
#             attr_to_rm = form_dict.pop("remove")
#             if len(form_dict) == 1:
#                 err_msg = "La coleccion debe tener al menos algun atributo"
#                 context_dict["err_msg"] = err_msg
#             else:
#                 form_dict.pop(attr_to_rm)
#         elif "save" in form_dict:
#             form_dict.pop("save") 
#             new_model = []
#             # Realizamos una comprobacion previa de parametros
#             for attr in form_dict:
#                 value = form_dict[attr]
#                 if value == "id" or value == "_id":
#                     err_msg = f"El nombre de atributo '{value}' no esta permitido"
#                     context_dict["err_msg"] = err_msg
#                     break
#                 elif value in new_model:
#                     err_msg = f"El atributo '{value}' esta repetido"
#                     context_dict["err_msg"] = err_msg
#                 elif value != "":
#                     new_model.append(value)
#             else:
#                 if len(new_model) == 0:
#                     err_msg = "La coleccion debe tener al menos algun atributo no vacio"
#                     context_dict["err_msg"] = err_msg
#                 elif model is not None:
#                     dbc.update_model(db, collection, new_model)
#                     msg = f"""El modelo de la coleccion '{collection}' ha sido 
#                     actualizado con exito"""
#                     _set_extra_vars({"msg": msg}, "display_documents")
#                     return HttpResponseRedirect(f"/display/{db}/{collection}")
#                 else:
#                     dbc.add_collection(db, collection, new_model)
#                     msg = f"Coleccion '{collection}' añadida con exito"
#                     _set_extra_vars({"msg": msg}, "display_collections")
#                     return HttpResponseRedirect(f"/display/{db}")
#         context_dict["attrs"] = form_dict
        
#     response = render(request, "create_doc_model.html", context_dict)
#     return response

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
        print(clear_form)
        if "yes" in clear_form:
            print("mal")
            for doc in docs:
                dbc.delete_document(db, collection, doc["id"])
            docs = dbc.get_documents(db, collection)
            if not bool(docs):
                msg = "Coleccion vaciada con exito"
                context_dict["msg"] = msg
        elif "no" in clear_form:
            print("bien")
            err_msg = "Operacion cancelada"
            context_dict["err_msg"] = err_msg
        elif bool(clear_form) and "clear" in clear_form:
            context_dict["delete_docs"] = True
            return render(request, 'ask_confirmation.html', context_dict)
        # Mostramos los documentos segun si hay o no hay modelo establecido
        model_doc = dbc.get_model(db, collection)
        if bool(model_doc):
            context_dict["model"] = list(model_doc.values())
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
            context_dict["model"] = model.values()
    
    context_dict["add_doc"] = True
    return render(request, 'add.html', context_dict)

def update_document(request:HttpRequest, db:str, collection:str, doc_id:str):
    context_dict = {"db": db, "collection": collection}
    doc = dbc.find_doc_by_id(db, collection, doc_id)
    context_dict["doc"] = doc
    
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
    
    