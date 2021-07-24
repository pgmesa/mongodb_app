
import json
from contextlib import suppress
from pymongo.errors import ServerSelectionTimeoutError
# django imports
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.http.request import QueryDict
from django.shortcuts import render
# program imports
from controllers import db_controller as dbc
from mypy_modules.register import register


def _clean_form(form:QueryDict) -> dict:
    cleaned = form.dict()
    with suppress(Exception):
        cleaned.pop("csrfmiddlewaretoken")
    
    return cleaned

def _get_extra_vars(view_name:str) -> dict:
    extra_vars:dict = register.load("extra_vars")
    view_extra_vars = {}
    if extra_vars is not None:
        v_vars = extra_vars.get(view_name, None)
        if v_vars is not None:
            extra_vars.pop(view_name)
            register.update("extra_vars", extra_vars)
            view_extra_vars = v_vars
    
    return view_extra_vars

def _set_extra_vars(view_extra_vars:dict, view_name:str) -> None:
    extra_vars = register.load("extra_vars")
    if extra_vars is None:
        extra_vars = {view_name: view_extra_vars}
        register.add("extra_vars", extra_vars)
    else:
        ex_view_extra_vars = extra_vars.get(view_name, None)
        if not bool(ex_view_extra_vars):
            extra_vars[view_name] = view_extra_vars
        else:
            for var, value in view_extra_vars.items():
                extra_vars[view_name][var] = value
        register.update("extra_vars", extra_vars)
    
            
def _parse_doc_attrs(model:dict, doc:dict) -> dict:
    for attr_dict in model.values():
        name = attr_dict["name"]; str_type = attr_dict["type"]
        try:
            value = doc[name]
        except KeyError:
            continue
        if value == "": continue
        if str_type == 'str':
            type_func = str
        elif str_type == 'int':
            type_func = int
        elif str_type == 'float':
            type_func = float
        else:
            err_msg = f"EL tipo '{str_type}' no es válido, debe ser (str, int o float)"
            raise Exception(err_msg)
        try:
            parsed = type_func(value)
        except:
            last_try = False
            if type_func is int:
                try:
                    parsed = float(value)
                    parsed = int(parsed)
                except:
                    pass
                else:
                    last_try = True
            if not last_try:
                err_msg = f"""El valor del atributo '{name}' -> '{value}' no puede 
                ser de tipo '{str_type}'"""
                raise Exception(err_msg)
        doc[name] = parsed
    return doc

def _view_inspector(func):
    def view_inspector(*args, **kwargs) -> HttpResponse:
        # print("register -->", register.load())
        view_params = register.load('view_params')
        if view_params is None:
            view_params = {"last_view": None, "redirected": False}
            register.add('view_params', view_params)
        last_view = view_params["last_view"]
        if last_view != func.__name__:
            view_params["redirected"] = True
        else:
            view_params["redirected"] = False
        view_params["last_view"] = func.__name__
        register.update('view_params', view_params)
        try:
            return func(*args, **kwargs)
        except ServerSelectionTimeoutError as err:
            err_msg = (f"Fallo al conectarse a la base de datos " +
            f"(HOST={dbc.HOST}, PORT={dbc.PORT}), conexión rechazada " +
            f"--> MENSAJE DE ERROR:\n\n({str(err)})")
            _set_extra_vars({"err_msg": err_msg, "conserv_format": True}, 'error')
            return HttpResponseRedirect('/error/')
        except Exception as err:
            err_msg = f"ERROR: {err}"
            _set_extra_vars({"err_msg": err_msg, "failed_path": args[0].path_info}, 'error')
            return HttpResponseRedirect('/error/')
    return view_inspector

# --------------------------------------------------------------------
# --------------------------- ERROR VIEW -----------------------------
def error(request:HttpRequest) -> HttpResponse:
    context_dict = _get_extra_vars('error')
    if "err_msg" not in context_dict:
        return HttpResponseRedirect(context_dict["failed_path"])
    
    _set_extra_vars({"failed_path": context_dict["failed_path"]}, 'error')
    return render(request, 'base.html', context_dict)
    
# --------------------------------------------------------------------
# ------------------------- DATA BASE VIEWS --------------------------
@_view_inspector
def home(request:HttpRequest) -> HttpResponse:
    client_ip = request.META['REMOTE_ADDR']; print(client_ip)
    context_dict = _get_extra_vars("home")
    dbs = dbc.list_dbs()
    context_dict["dbs"] = dbs
    
    if not bool(dbs):
        err_msg = "No hay bases de datos creadas, MongoDB esta vacío"
        context_dict["err_msg"] = err_msg
    else:
        app_dbs = dbc.list_dbs(only_app_dbs=True)
        for app in app_dbs:
            dbs.remove(app)
        dbs = app_dbs + dbs
        context_dict["dbs"] = dbs
        context_dict["app_dbs"] = app_dbs
        
    response:HttpResponse = render(request, 'home.html', context_dict)
    return response

@_view_inspector
def add_db(request:HttpRequest) -> HttpResponse:
    context_dict = {}; post_dict = request.POST.dict()
    
    if bool(post_dict):
        dbs = dbc.list_dbs()
        new_db = post_dict['name']
        context_dict["db_name"] = new_db
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

@_view_inspector
def update_db(request:HttpRequest, db:str) -> HttpResponse:
    context_dict = {"db": db}
    form_dict = request.POST.dict()
    if bool(form_dict):
        new_name = form_dict["name"]
        ex_dbs = dbc.list_dbs()
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

@_view_inspector
def delete_db(request:HttpRequest, db:str) -> HttpResponse:
    context_dict = {"db": db}; conf_dict = _clean_form(request.POST)
    if bool(conf_dict): 
        if "yes" in conf_dict:
            dbc.drop_db(db)
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
@_view_inspector
def display_collections(request:HttpRequest, db:str) -> HttpResponse:
    context_dict = _get_extra_vars("display_collections")
    context_dict["db"] = db
    collections = dbc.list_collections(db)
    if not bool(collections):
        err_msg = "No existen colecciones en esta base de datos"
        context_dict["err_msg"] = err_msg
    else:
        app_collections = dbc.list_collections(db, only_app_coll=True)
        for app in app_collections:
            collections.remove(app)
        collections = app_collections + collections
        context_dict["app_db_collections"] = app_collections
        context_dict["db_collections"] = collections
        
    return render(request, 'collections.html', context_dict)

@_view_inspector
def add_collection(request:HttpRequest, db:str) -> HttpResponse:
    context_dict = {"db": db}; post_dict = request.POST.dict()
    if bool(post_dict):
        collections = dbc.list_collections(db)
        new_collection = post_dict['name']
        context_dict["collection_name"] = new_collection
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

@_view_inspector   
def create_doc_model(request:HttpRequest, db:str, collection:str) -> HttpResponse:
    context_dict = {"db": db, "collection": collection, "model":{"attr1": {"name": "","type": ""}}}
    extra_vars = _get_extra_vars("create_doc_model")
    for var, value in extra_vars.items():
        context_dict[var] = value
    ex_model = dbc.get_model(db, collection)
    if ex_model is not None:
        context_dict["model"] = ex_model
        if "num_attrs" not in context_dict:
            context_dict["num_attrs"] = len(ex_model)
    else:
        if "num_attrs" not in context_dict:
            context_dict["num_attrs"] = 1

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
                    valid = False; break
                elif name in attrs_names and name != "":
                    err_msg = f"El atributo '{name}' esta repetido"
                    context_dict["err_msg"] = err_msg
                    valid = False; break
                elif name == "":
                    err_msg = "No pueden haber atributos vacios"
                    context_dict["err_msg"] = err_msg
                    valid = False; break
                else:
                    valid_model[attr] = attr_dict
            # Comprobamos que los tipos que se quieren actualizar sean validos
            # teniendo encuenta los valores ya añadidos
            if ex_model is not None:
                docs = dbc.get_documents(db, collection)
                for doc in docs:
                    try:   
                        doc = _parse_doc_attrs(valid_model, doc)
                    except Exception as err:
                        err_msg = f"""No todos los documentos pueden ser parseados.
                        El documento con id '{doc["id"]}' ha fallado en la conversion 
                        --> ({str(err)})"""
                        context_dict["err_msg"] = err_msg
                        valid = False; break
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

@_view_inspector
def update_collection(request:HttpRequest, db:str, collection:str) -> HttpResponse:
    context_dict = {"db": db, "collection": collection}
    form_dict = request.POST.dict()
    if bool(form_dict):
        new_name = form_dict["name"]
        ex_collections = dbc.list_collections(db)
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

@_view_inspector
def delete_collection(request:HttpRequest, db:str, collection:str) -> HttpResponse:
    context_dict = {"db": db, "collection": collection}
    conf_dict = _clean_form(request.POST)
    if bool(conf_dict): 
        if "yes" in conf_dict:
            dbc.remove_collecttion(db, collection)
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
@_view_inspector
def display_documents(request:HttpRequest, db:str, collection:str , extra_vars:dict={}) -> HttpResponse:
    context_dict = {"db": db, "collection": collection}
    extra_vars = _get_extra_vars("display_documents")
    for var, val in extra_vars.items():
        context_dict[var] = val

    docs = dbc.get_documents(db, collection)
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

@_view_inspector
def add_document(request:HttpRequest, db:str, collection:str) -> HttpResponse:
    context_dict = {"db": db, "collection": collection}
    context_dict["textareas"] = []
    context_dict["values"] = {}
    extra_vars = _get_extra_vars('add_document')
    for var, value in extra_vars.items():
        context_dict[var] = value
    view_params = register.load('view_params')
    if view_params["redirected"]:
        context_dict["textareas"] = []
        
    form_dict = _clean_form(request.POST)
    if bool(form_dict):
        if "add" in form_dict:
            form_dict.pop("add")
            doc = form_dict
            model = dbc.get_model(db, collection)
            try:
                doc = _parse_doc_attrs(model, doc)
            except Exception as err:
                context_dict["err_msg"] = str(err)
            else:
                dbc.add_document(db, collection, doc)
                msg = "Documento añadido con exito"
                _set_extra_vars({"msg": msg}, "display_documents")
                return HttpResponseRedirect(f"/display/{db}/{collection}")
            context_dict["values"] = form_dict
        elif "textarea" in form_dict:
            attr = form_dict.pop("textarea")
            if attr in context_dict["textareas"]:
                context_dict["textareas"].remove(attr)
            else:
                context_dict["textareas"].append(attr)
            context_dict["values"] = form_dict
    model = dbc.get_model(db, collection)
    context_dict["model"] = model
        
    _set_extra_vars({"textareas": context_dict["textareas"]}, 'add_document')
    context_dict["add_doc"] = True
    return render(request, 'add.html', context_dict)

@_view_inspector
def update_document(request:HttpRequest, db:str, collection:str, doc_id:str) -> HttpResponse:
    context_dict = {"db": db, "collection": collection}
    context_dict["textareas"] = []
    context_dict["values"] = {}
    extra_vars = _get_extra_vars('update_document')
    for var, value in extra_vars.items():
        context_dict[var] = value
    view_params = register.load('view_params')
    if view_params["redirected"]:
        context_dict["textareas"] = []
        
    doc = dbc.find_doc_by_id(db, collection, doc_id)
    context_dict["doc_id"] = doc_id
    context_dict["values"] = doc
    context_dict["model"] = dbc.get_model(db, collection)
    
    form_dict = _clean_form(request.POST)
    if bool(form_dict):
        if "update" in form_dict:
            form_dict.pop("update")
            new_doc = form_dict
            try:
                model = dbc.get_model(db, collection)
                new_doc = _parse_doc_attrs(model, new_doc)
            except Exception as err:
                context_dict["err_msg"] = str(err)
            else:
                dbc.update_document(db, collection, doc_id, new_doc)
                msg = (f"Documento con id '{doc_id}' actualizado con exito")
                _set_extra_vars({"msg": msg}, "display_documents")
                return HttpResponseRedirect(f"/display/{db}/{collection}")
        elif "textarea" in form_dict:
            attr = form_dict.pop("textarea")
            if attr in context_dict["textareas"]:
                context_dict["textareas"].remove(attr)
            else:
                context_dict["textareas"].append(attr)
        context_dict["values"] = form_dict
    
    _set_extra_vars({"textareas": context_dict["textareas"]}, 'update_document')
    context_dict["update_doc"] = True
    return render(request, "update.html", context_dict)

@_view_inspector
def delete_document(request:HttpRequest, db:str, collection:str, doc_id:str) -> HttpResponse:
    doc = dbc.find_doc_by_id(db, collection, doc_id)
    str_doc = json.dumps(doc, indent=4, sort_keys=True)
    context_dict = {"db": db, "collection": collection, "doc_id":doc_id, "doc": str_doc}
    conf_dict = _clean_form(request.POST)
    if bool(conf_dict): 
        if "yes" in conf_dict:
            dbc.delete_document(db, collection, doc_id)
            msg = f"Documento con id '{doc_id}' eliminado con exito"
            context_dict["msg"] = msg
        else:
            err_msg = "Operacion cancelada"
            context_dict["err_msg"] = err_msg
        
        _set_extra_vars(context_dict, "display_documents")
        return HttpResponseRedirect(f"/display/{db}/{collection}")
    
    context_dict["delete_doc"] = True
    return render(request, 'ask_confirmation.html', context_dict)

@_view_inspector
def filter_documents(request:HttpRequest, db:str, collection:str) -> HttpResponse:
    context_dict = _get_extra_vars('filter_documents')
    context_dict.update({"db": db, "collection": collection})
    
    model = dbc.get_model(db, collection)
    context_dict["model"] = model
    context_dict["values"] = {}
    
    return render(request, 'filter.html', context_dict)

@_view_inspector
def sort_documents(request:HttpRequest, db:str, collection:str) -> HttpResponse:
    context_dict = _get_extra_vars('sort_documents')
    context_dict.update({"db": db, "collection": collection})
    
    model = dbc.get_model(db, collection)
    context_dict["model"] = model
    
    return render(request, 'sort.html', context_dict)
    
    