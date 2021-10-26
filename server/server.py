
import os
import json
import copy
from contextlib import suppress, contextmanager
from pymongo.errors import ServerSelectionTimeoutError
# django imports
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.http.request import QueryDict
from django.shortcuts import render
from django.core.files.uploadedfile import UploadedFile
# program imports
from controllers import db_controller as dbc
from mypy_modules.register import register
from commands.reused_code import NotInstalledError, check_mongo_installed
from .encryption_lib.encryption import *
import concurrent.futures as conc


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
            
def _parse_doc_attrs(actual_model:dict, doc:dict, filter_=False, new_model:dict=None) -> dict:
    parsed_doc = copy.deepcopy(doc)
    model = actual_model
    if new_model is not None:
        model = new_model
    for attr, attr_dict in model.items():
        name = attr_dict["name"]; str_type = attr_dict["type"]
        try:
            value = doc[name]
        except KeyError:
            # Se ha modificado el nombre del atributo
            if attr in actual_model:
                old_name = actual_model[attr]["name"]
                value = doc[old_name]
            else:
                # Si no esta es que se ha eliminado el atributo y no hay que parsear nada, se van a 
                # eliminar los datos de ese atributo en cada documento
                continue
                    
        if value == "" or value == "-": 
            if not filter_:
                parsed_doc[name] = "-"
            continue
        if str_type == 'str' or str_type == 'password':
            type_func = str
        elif str_type == 'int':
            type_func = int
        elif str_type == 'float':
            type_func = float
        else:
            err_msg = f"EL tipo '{str_type}' no es válido, debe ser "
            err_msg += "(str, int, float o password)"
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
        parsed_doc[name] = parsed
    return parsed_doc

cf_path = 'server/cipher_lib/cipher.py'
cf_test_path = cf_path.replace(".py", "_test.py")

def _check_valid_cf(file:UploadedFile):
    # return False, None
    with open(cf_test_path, 'wb') as test_file:
        for chunk in file.chunks():
            test_file.write(chunk)
    try:
        import server.cipher_lib.cipher_test as cph
        key = b'\xf5\xa8\x18\xc6\x8aHo\xfd\xb99@\xbe\x97~\xc4\xd0'
        ciphered = cph.cipher(key)
        if key != cph.decipher(ciphered):
            raise Exception('NotValidFile: Las funciones cipher y decipher no son inversas')
    except ImportError:
        err_msg = "NotValidFile: El fichero no contiene las funciones 'cipher', 'decipher'"
        os.remove(cf_test_path)
        return False, err_msg
    except Exception as err:
        os.remove(cf_test_path)
        return False, str(err)
    
    return True, None

def _view_inspector(func):
    def view_inspector(*args, **kwargs) -> HttpResponse:
        # Checkear si se ha cambiado el tema  y si si, redirigir a misma view en la que estabamos
        # request.POST
        request:HttpRequest = args[0]
        post_form = _clean_form(request.POST)
        print(post_form)
        # Miramos si hay que evaluar la master key
        if 'validate_mk' in post_form:
            cf_key = post_form.pop('update_cf')
            # in_hash = get_sha256_hash(cf_key)
            # if in_hash != register.load('master_key_hash'):
            #     err_msg = "Incorrect master key"
        if bool(post_form) and "toggle_theme" in post_form:
            # Cambiamos tema
            theme = register.load("theme")
            if theme is None:
                theme = 'light'
                register.add('theme', theme)
            if theme == 'light':
                theme = 'dark'
            elif theme == 'dark':
                theme = 'light'
            register.update('theme', theme)
        elif bool(post_form):
            err_msg = None; msg = None
            if 'add_cf' in post_form:
                file = request.FILES['cf_file']
                valid, err_msg = _check_valid_cf(file)
                if valid:
                    os.rename(cf_test_path, cf_path)
                    encrypt_file(cf_path, )
                    msg = "'Cipher file' añadido y encriptado con exito con exito"
            elif 'update_cf' in post_form:
                file = request.FILES['cf_file']
                valid, err_msg = _check_valid_cf(file)
                if valid:
                    # Cambiar el cifrado de cada key guardada
                    ...
                    msg = "'Cipher file' actualizado con exito"
            elif 'delete_cf' in post_form:
                os.remove(cf_path)
                msg = "'Cipher file' eliminado con exito"
                    
            if msg is not None:
                _set_extra_vars({"msg": msg},func.__name__)
            elif err_msg is not None:
                _set_extra_vars({"err_msg": err_msg},func.__name__)
        # -----------------------------------------------------
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
            check_mongo_installed()
            return func(*args, **kwargs)
        except NotInstalledError as err:
            err_msg = f"ERROR: {err}"
            dic = {"err_msg": err_msg, "conserv_format": True, "failed_path": request.path_info}
            _set_extra_vars(dic, 'error')
            return HttpResponseRedirect('/error/')
        except ServerSelectionTimeoutError as err:
            err_msg = (f"Fallo al conectarse a la base de datos " +
            f"(HOST={dbc.HOST}, PORT={dbc.PORT}), conexión rechazada " +
            f"--> MENSAJE DE ERROR:\n\n({str(err)})")
            dic = {"err_msg": err_msg, "conserv_format": True, "failed_path": request.path_info}
            _set_extra_vars(dic, 'error')
            return HttpResponseRedirect('/error/')
        # except Exception as err:
        #     err_msg = f"ERROR: {err}"
        #     _set_extra_vars({"err_msg": err_msg, "failed_path": args[0].path_info}, 'error')
        #     return HttpResponseRedirect('/error/')
    return view_inspector

def _order_lists(list_to_order:list, order_list:list) -> list:
    ordered_list = ["_._"]*len(order_list)
    new_elements = []
    for elem in list_to_order:
        if elem in order_list:
            index = order_list.index(elem)
            ordered_list[index] = elem
        else:
            new_elements.append(elem)
    # Added databases
    for elem in new_elements:
        ordered_list.insert(0, elem)
    # Deleted databases
    cp_ordered_list = copy.deepcopy(ordered_list)
    for elem in cp_ordered_list:
        if elem == "_._":
            ordered_list.remove(elem)
        
    return ordered_list

config_keys = [
    "extra_vars", "view_params", "tasks", "github", "hide_dbs", "autocomplete", "theme"
]

def _modify_data(name:str, copy_to_name:str=None, delete:bool=False):
    reg = register.load()
    new_reg = copy.deepcopy(reg)
    if reg is not None:
        for key in reg:
            if key not in config_keys:
                values = reg[key]
                type_values = type(values)
                if (type_values is list or type_values is dict) and name in values:
                    if type_values is list:
                        index = values.index(name)
                        if delete:
                            values.pop(index)
                        if copy_to_name is not None:
                            values.insert(index, copy_to_name)
                        new_reg[key] = values
                    elif type_values is dict:
                        new_values = {}
                        for val_key, val in values.items():
                            if val_key != name:
                                new_values[val_key] = val
                            else:
                                if not delete:
                                    new_values[val_key] = val
                                if copy_to_name is not None:
                                    new_values[copy_to_name] = val
                        new_reg[key] = new_values
    register.override(new_reg)
    
def _is_sk_encrypted() -> bool:
    secret_key_path = 'server/secret_key.py'
    if os.path.exists(secret_key_path):
        with open(secret_key_path, 'r') as file:
            content = file.read()
            if "#_ENCRYPTED_#" in content:
                return True
    return False

@contextmanager
def try_unlock_sk_file(sk_file_key):
    if _is_sk_encrypted() and sk_file_key is not None:
        #decrypt_sk_file()
        yield True
    yield False
    if _is_sk_encrypted():
        #encrypt_sk_file()
        ...

def _check_secret_file(sk_file_key:str=None):
    with try_unlock_sk_file(sk_file_key) as has_been_decrypted:
    # sk_info = register. 
    # if os.path.exists('server/secret_key.py'):
        
        try:
            import server.secret_key as sk
            sk.get; sk.hide
            sk.hide(1234, 1213423423); sk.get(187242423478894)
            return True, None
        except ImportError:
            valid = False
            msg = "No se ha implementado un fichero secret_key.py en la carpeta /server. "
        except AttributeError:
            valid = False
            msg = "El fichero server/secret_key.py no contiene alguna de las funciones sk.get o sk.hide. "
        except Exception:
            valid = False
            msg = "En las funciones sk.get o sk.hide saltan excepciones (se ignoraran). "
        if not valid and has_been_decrypted:
            err_msg = msg + "Puede que la clave de acceso al fichero secret_key.py sea incorrecta"
            return valid, err_msg
    err_msg = "Las encriptaciones de las contraseñas no son seguras, las claves son visibles. "
    err_msg += msg
    err_msg += "En caso de haber contraseñas guardadas previamente, sera necesario el fichero "
    err_msg += "con las funciones originales para desbloquearlas (en caso de que se usara algun fichero) "
    err_msg += "(por seguridad, el programa no le avisara cuando las funciones son las correctas)"
    
    return valid, err_msg
    
# --------------------------------------------------------------------
# --------------------------- ERROR VIEW -----------------------------
def error(request:HttpRequest) -> HttpResponse:
    context_dict = _get_extra_vars('error')
    if "err_msg" not in context_dict:
        return HttpResponseRedirect(context_dict["failed_path"])

    _set_extra_vars({"failed_path": context_dict["failed_path"]}, 'error')
    return render(request, 'base.html', context_dict)
    
# --------------------------------------------------------------------
# ------------------------- DATABASE VIEWS --------------------------
@_view_inspector
def home(request:HttpRequest) -> HttpResponse:
    client_ip = request.META['REMOTE_ADDR']; print(client_ip)
    context_dict = _get_extra_vars("home")
    dbs = dbc.list_dbs()
    app_dbs = dbc.list_dbs(only_app_dbs=True)    
    context_dict["dbs"] = dbs
    context_dict["change_theme"] = True

    if not bool(dbs):
        err_msg = "No hay bases de datos creadas, MongoDB esta vacío"
        context_dict["err_msg"] = err_msg
    else:
        order_list = register.load('dbs_order')
        # See if there is an existing predefined order
        if order_list is None:
            for db_app in app_dbs:
                dbs.remove(db_app)
            dbs = app_dbs + dbs
            register.add('dbs_order', dbs)
        else:
            dbs = _order_lists(dbs, order_list)
            register.update('dbs_order', dbs)
        # See if up or down button are pressed
        post_dict = _clean_form(request.POST)
        if bool(post_dict):
            if "up" in post_dict:
                db = post_dict.pop("up")
                index = dbs.index(db) 
                new_index = index-1
                if new_index >= 0:
                    dbs.pop(index)
                    dbs.insert(index-1, db)
                context_dict["id_to_scroll"] = db
            elif "down" in post_dict:
                db = post_dict.pop("down")
                index = dbs.index(db)
                new_index = index+1
                if new_index < len(dbs):
                    dbs.pop(index)
                    dbs.insert(index+1, db)
                context_dict["id_to_scroll"] = db
            register.update('dbs_order', dbs)    
        # Miramos a ver si hay que ocultar las bbdd que no sean de la app
        hidde_form = _clean_form(request.POST)
        if "hidden" in hidde_form:
            hidden = hidde_form.pop('hidden')
            if hidden == 'True':
                hide = False
            else:
                hide = True
            register.update('hide_dbs', hide)
        else:
            hide = register.load('hide_dbs')
            if hide is None:
                hide = False
                register.add('hide_dbs', hide) 
        context_dict["hide"] = hide
        if hide:
            cp_dbs = copy.deepcopy(dbs)
            for db in cp_dbs:
                if db not in app_dbs:
                    dbs.remove(db)
        if len(dbs) == 0:
            err_msg = "No existen bases de datos controladas por la aplicacion"
            context_dict["err_msg"] = err_msg
        # Guardamos los dbs ordenadas y filtradas
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
        elif "/" in new_db or "\\" in new_db:
            err_msg = f"El nombre no puede contener '/' ni '\\'"
            context_dict["err_msg"] = err_msg
        else:
            return HttpResponseRedirect(f'/add/{new_db}')

    context_dict["add_db"] = True
    return render(request, "add.html", context_dict)

@_view_inspector
def duplicate_db(request:HttpRequest, db:str) -> HttpResponse:
    i = 1; cp_name = db + f"({i})"
    db_names = dbc.list_dbs()
    while cp_name in db_names:
        i += 1
        cp_name = db + f"({i})"
    _set_extra_vars({"id_to_scroll": cp_name}, 'home')
    collections = dbc.list_collections(db, only_app_coll=True)
    for collection in collections:
        docs = dbc.get_documents(db, collection, with_app_format=False)
        model = None
        for doc in docs:
            if doc["_id"] == "model":
                model = doc
                docs.remove(doc)
                break
        dbc.add_collection(cp_name, collection, model)
        for doc in docs:
            dbc.add_document(cp_name, collection, doc)
        _modify_data(f'{db}.{collection}', copy_to_name=f'{cp_name}.{collection}')
    _modify_data(db, copy_to_name=cp_name)
    return HttpResponseRedirect('/')

@_view_inspector
def update_db(request:HttpRequest, db:str) -> HttpResponse:
    _set_extra_vars({"id_to_scroll": db}, 'home')
    context_dict = {"db": db}
    form_dict = request.POST.dict()
    if bool(form_dict):
        new_name = form_dict["name"]
        ex_dbs = dbc.list_dbs()
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
        elif "/" in new_name or "\\" in new_name:
            err_msg = "El nombre no puede contener '/' ni '\\'"
            context_dict["err_msg"] = err_msg
        else:
            if new_name != db:
                # Actualizamos del registro la info asociada a la db y sus colecciones
                _modify_data(db, copy_to_name=new_name, delete=True)
                collections = dbc.list_collections(db)
                for colec in collections:
                    _modify_data(f'{db}.{colec}', copy_to_name=f'{new_name}.{colec}', delete=True)
                dbc.rename_db(db, new_name)
            msg = (f"Base de Datos '{db}' actualizada con exito " + 
                    f"-> '{new_name}'")
            _set_extra_vars({"msg": msg}, "home")
            return HttpResponseRedirect("/")
            
    context_dict["update_db"] = True
    return render(request, "update.html", context_dict)

@_view_inspector
def delete_db(request:HttpRequest, db:str) -> HttpResponse:
    _set_extra_vars({"id_to_scroll": db}, 'home')
    context_dict = {"db": db}; conf_dict = _clean_form(request.POST)
    if bool(conf_dict): 
        if "yes" in conf_dict:
            # Eliminamos del registro la info asociada a la db y sus colecciones
            _modify_data(db, delete=True)
            collections = dbc.list_collections(db)
            for colec in collections:
                _modify_data(f'{db}.{colec}', delete=True)
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
    app_collections = dbc.list_collections(db, only_app_coll=True)
    context_dict["db_collections"] = collections
    context_dict["change_theme"] = True
    
    if not bool(collections):
        err_msg = "No existen colecciones en esta base de datos"
        context_dict["err_msg"] = err_msg
    else:
        collec_orders = register.load('db_collec_orders')
        if collec_orders is not None:
            order_list = collec_orders.get(db, None)
        # See if there is an existing predefined order
        if collec_orders is None or order_list is None:
            for collec in app_collections:
                collections.remove(collec)
            collections = app_collections + collections
            if collec_orders is None:
                register.add('db_collec_orders', {db: collections})
            else:
                collec_orders[db] = collections
                register.update('db_collec_orders', collec_orders)
        else:
            collections = _order_lists(collections, order_list)
            collec_orders[db] = collections
            register.update('db_collec_orders', collec_orders)
        # See if up or down button are pressed
        post_dict = _clean_form(request.POST)
        if bool(post_dict):
            if "up" in post_dict:
                collection = post_dict.pop("up")
                index = collections.index(collection) 
                new_index = index-1
                if new_index >= 0:
                    collections.pop(index)
                    collections.insert(index-1, collection)
                context_dict["id_to_scroll"] = collection
            elif "down" in post_dict:
                collection = post_dict.pop("down")
                index = collections.index(collection)
                new_index = index+1
                if new_index < len(collections):
                    collections.pop(index)
                    collections.insert(index+1, collection)
                context_dict["id_to_scroll"] = collection
            register.update('db_collec_orders', collections, override=False, dict_id=db)
        # Miramos a ver si hay que ocultar las colecciones que no sean de la app
        hidde_form = _clean_form(request.POST)
        hide_collections:dict = register.load('hide_collections')
        if "hidden" in hidde_form:
            hidden = hidde_form.pop('hidden')
            if hidden == 'True':
                hide = False
            else:
                hide = True
            hide_collections[db] = hide
            register.update('hide_collections', hide_collections)
        else:
            if hide_collections is None:
                dbs = dbc.list_dbs(); hide_collections = {}
                for db in dbs:
                    hide_collections[db] = False
                register.add('hide_collections', hide_collections)
            hide = hide_collections.get(db, None)
            if hide is None:
                hide_collections[db] = False
                register.update('hide_collections', hide_collections)
        context_dict["hide"] = hide
        if hide:
            cp_collections = copy.deepcopy(collections)
            for collec in cp_collections:
                if collec not in app_collections:
                    collections.remove(collec)
        if len(collections) == 0:
            err_msg = ("No existen colecciones controladas por la aplicacion " +
                            "en esta base de datos")
            context_dict["err_msg"] = err_msg
        # Guardamos los dbs ordenadas y filtradas
        context_dict["db_collections"] = collections
        context_dict["app_db_collections"] = app_collections
        
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
        elif "/" in new_collection or "\\" in new_collection:
            err_msg = "El nombre no puede contener '/' ni '\\'"
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
        context_dict["old_model"] = ex_model
        context_dict["model"] = ex_model
        context_dict["updating_model"] = True
        if "num_attrs" not in context_dict:
            context_dict["num_attrs"] = len(ex_model)
    else:
        if "num_attrs" not in context_dict:
            context_dict["num_attrs"] = 1

    def process_model_from_form(form_dict:dict) -> dict:
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
                        doc = _parse_doc_attrs(ex_model, doc, new_model=valid_model)
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
def duplicate_collection(request:HttpRequest, db:str, collection:str) -> HttpResponse:
    collections = dbc.list_collections(db)
    i = 1; cp_name = collection + f"({i})"
    while cp_name in collections:
        i += 1
        cp_name = collection + f"({i})"
    _set_extra_vars({"id_to_scroll": cp_name}, 'display_collections')
    docs = dbc.get_documents(db, collection, with_app_format=False)
    model = None
    for doc in docs:
        if doc["_id"] == "model":
            model = doc
            docs.remove(doc)
            break
    dbc.add_collection(db, cp_name, model)
    for doc in docs:
        dbc.add_document(db, cp_name, doc)
    _modify_data(f'{db}.{collection}', copy_to_name=f'{db}.{cp_name}')
    
    return HttpResponseRedirect(f'/display/{db}')

@_view_inspector
def update_collection(request:HttpRequest, db:str, collection:str) -> HttpResponse:
    _set_extra_vars({"id_to_scroll": collection}, 'display_collections')
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
        elif "/" in new_name or "\\" in new_name:
            err_msg = "El nombre no puede contener '/' ni '\\'"
            context_dict["err_msg"] = err_msg
        else:
            if new_name != collection:
                # Actualizamos del registro la info asociada a la coleccion
                _modify_data(f'{db}.{collection}', copy_to_name=f'{db}.{new_name}', delete=True)
                dbc.rename_collection(db, collection, new_name)
            msg = (f"Coleccion '{collection}' actualizada con exito " + 
                    f"-> '{new_name}'")
            _set_extra_vars({"msg": msg}, "display_collections")
            return HttpResponseRedirect(f"/display/{db}")
    
    context_dict["update_collection"] = True
    return render(request, "update.html", context_dict)

@_view_inspector
def delete_collection(request:HttpRequest, db:str, collection:str) -> HttpResponse:
    _set_extra_vars({"id_to_scroll": collection}, 'display_collections')
    context_dict = {"db": db, "collection": collection}
    conf_dict = _clean_form(request.POST)
    if bool(conf_dict): 
        if "yes" in conf_dict:
            # Eliminamos del registro la info asociada a la coleccion
            _modify_data(f"{db}.{collection}", delete=True)
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
def validate_key(request:HttpRequest, db:str, collection:str, doc_id:str, attr:str):
    if "--" in doc_id:
        doc_index = ""
        for i, num in enumerate(doc_id[::-1]):
            if num == "-":
                doc_index = int(doc_index[::-1])
                doc_id = doc_id[:len(doc_id)-i-2]
                break
            doc_index += str(num)
        _set_extra_vars({"id_to_scroll": doc_index} ,'display_documents')
    doc = dbc.find_doc_by_id(db, collection, doc_id)
    encrypted = doc[attr]
    context_dict = {"db": db, "collection": collection}
    extra_vars = _get_extra_vars('validate_key')
    for var, val in extra_vars.items():
        context_dict[var] = val
    
    key = None
    pw_info = dbc.get_password_info(db, collection, encrypted)
    seed = int(pw_info["seed"])
    mode = pw_info["mode"]
    
    info = f" + Encrypted Password: {encrypted}\n"
    info += f" + Seed: {seed}\n"
    info += f" + Mode: {mode}\n"
    context_dict["encryption_info"] = info
    
    key_form = _clean_form(request.POST)
    if bool(key_form):
        passed_key = key_form.pop("key")
        import server.secret_key as sk
        key, seed = sk.get(seed)
        if passed_key == str(key):
            info = {
                "encrypted": encrypted,
                "seed": seed,
                "key": key,
                "mode": mode
            }
            if 'display_view' in context_dict:
                _set_extra_vars({"key_confirmed": info}, 'display_documents')
                return HttpResponseRedirect(f'/display/{db}/{collection}')
            elif 'update_view' in context_dict:
                _set_extra_vars({"key_confirmed": info}, 'update_document')
                return HttpResponseRedirect(f'/update/{db}/{collection}/{doc_id}')
        else:
            context_dict["err_msg"] = f"The key '{passed_key}' is incorrect, changing ecryption..."
            pw = decrypt(encrypted, seed, key, mode)
            decrypted = None; timeout = 1000
            while decrypted != pw:
                if timeout == 0:
                    context_dict['err_msg'] += "\n ERR: Chain encryption failed"
                    break
                encrypted, seed, key, mode = encrypt(pw)
                decrypted = decrypt(encrypted, seed, key, mode)
                timeout -= 1
            else:
                seed = sk.hide(key, seed)
                doc[attr] = encrypted
                pw_info = {
                    "encryption_info":{
                        "mode": mode,
                        "seed": str(seed)
                    }
                }
                dbc.add_password(db, collection, encrypted, pw_info)
                dbc.update_document(db, collection, doc_id, doc)
                info = f" + Encrypted Password: {encrypted}\n"
                info += f" + Seed: {seed}\n"
                info += f" + Mode: {mode}\n"
                context_dict["encryption_info"] = info
            
            context_dict["attempt"] = passed_key
    
    recycle_context = copy.deepcopy(context_dict)  
    func_params = ["db", "collection", "doc_id", "attr"]   
    for param in func_params:
        if param in recycle_context:
            recycle_context.pop(param)
    _set_extra_vars(recycle_context, 'validate_key')
    
    return render(request, 'validate_key.html', context_dict)

def _check_cipher_file():
    return os.path.exists('server/cipher_lib/cipher.py')

@_view_inspector
def display_documents(request:HttpRequest, db:str, collection:str, extra_vars:dict={}) -> HttpResponse:
    context_dict = {"db": db, "collection": collection}
    context_dict["change_theme"] = True
    
    secret_file , msg = _check_secret_file()
    
    passwords_stored = dbc.get_passwords(db, collection, with_id=True)
    if bool(passwords_stored) and not _check_cipher_file():
        warning = "Las contraseñas almacenadas no se podran descifrar sin el fichero cipher.py original"
        context_dict["warning"] = warning
    elif not bool(passwords_stored) and not _check_cipher_file():
        warning = "Las claves son vulnerables, no estan cifradas por ningun fichero cipher.py (se debe añadir)"
        context_dict["warning"] = warning
    context_dict["passwords"] = passwords_stored
    
    extra_vars = _get_extra_vars("display_documents")
    for var, val in extra_vars.items():
        context_dict[var] = val
    # Miramos si hay que eliminar todos los docs
    clear_form = _clean_form(request.POST)
    if "yes" in clear_form:
        docs = dbc.get_documents(db, collection)
        for doc in docs:
            dbc.delete_document(db, collection, doc["id"])
        docs = dbc.get_documents(db, collection)
        if not bool(docs):
            msg = "Coleccion vaciada con exito"
            context_dict["msg"] = msg
            context_dict["docs"] = docs
    elif "no" in clear_form:
        err_msg = "Operacion cancelada"
        context_dict["err_msg"] = err_msg
    elif bool(clear_form) and "clear" in clear_form:
        context_dict["delete_docs"] = True
        return render(request, 'ask_confirmation.html', context_dict)
    # Miramos si hay algun filtro que aplicar 
    filters = register.load('filters'); queries = {}  
    filter_form = _clean_form(request.POST)
    if "delete_filter" in filter_form and f"{db}.{collection}" in filters:
        filters.pop(f"{db}.{collection}")
        register.update('filters', filters)
    elif "update_filter" in filter_form:
        _set_extra_vars({"update_filter": True}, 'filter_documents')
        return HttpResponseRedirect(f'/filter/{db}/{collection}')
    else:
        if filters is not None:
            queries = filters.get(f"{db}.{collection}", {}).get('queries', {})
        if bool(queries): context_dict["filtered"] = True
    # Miramos si hay algun clasificador que aplicar     
    sorters = register.load('sorters'); sort_dict = {}  
    sorter_form = _clean_form(request.POST)
    if "delete_sorter" in sorter_form and f"{db}.{collection}" in sorters:
        sorters.pop(f"{db}.{collection}")
        register.update('sorters', sorters)
    elif "update_sorter" in sorter_form:
        _set_extra_vars({"update_sorter": True}, 'sort_documents')
        return HttpResponseRedirect(f'/sort/{db}/{collection}')
    else:
        if sorters is not None:
            sort_dict = sorters.get(f"{db}.{collection}", {})
        if bool(sort_dict): context_dict["sorted"] = True
    # Buscamos los documentos con el filtro y clasificador que haya aplicados
    docs = dbc.get_documents(db, collection, queries=queries, sort_dict=sort_dict, invert_sort=True)
    # Miramos si hay alguna estadistica que aplicar sobre algun campo
    stats_form = _clean_form(request.POST)
    if "tick" in stats_form:
        stats_form.pop("tick")
        register.update('stats', stats_form, override=False, dict_id=f"{db}.{collection}")
    elif "bin" in stats_form:
        stats_form = {}
        register.update('stats', stats_form, override=False, dict_id=f"{db}.{collection}")
    else:
        stats = register.load('stats')
        if stats is not None:
            stats_form = stats.get(f"{db}.{collection}", None)
            if stats_form is None:
                stats_form = {}
                stats[f"{db}.{collection}"] = stats_form
                register.update('stats', stats)
            else:
                model = dbc.get_model(db, collection)
                if bool(model):
                    # Comprobamos que no se han cambiado los tipos de datos
                    for attr_dict in model.values():
                        if attr_dict["name"]+"_stat" in stats_form:
                            tp = attr_dict["type"]
                            if tp != 'int' and tp != 'float':
                                stats_form.pop(attr_dict["name"]+"_stat")
                    stats[f"{db}.{collection}"] = stats_form
                    register.update('stats', stats)
        else:
            stats_form = {}
            register.add('stats', {f"{db}.{collection}": stats_form})
    context_dict["stats"] = stats_form
    # Calculamos las estadisticas
    if bool(stats_form):
        calculated_stats = {}
        for field, operator in stats_form.items():
            if operator == '-': continue
            field = field.removesuffix("_stat")
            if operator == 'avg' or operator == 'sum':
                lenght = len(docs)
                sum_ = 0
                for doc in docs:
                    if doc[field] == '-': lenght -= 1
                    else: sum_ += doc[field]
                if operator == 'avg': 
                    if lenght > 0:
                        result = round(sum_/lenght, 2)
                    else:
                        result = 0
                elif operator == 'sum': result = sum_
            calculated_stats[field] = result
        context_dict["calculated_stats"] = calculated_stats 
    # Desencriptamos la contraseña seleccionada
    unlock_form = _clean_form(request.POST)
    if "unlock" in unlock_form or "key_confirmed" in context_dict:
        key = None
        if "unlock" in unlock_form:
            enc_pw = unlock_form.pop('unlock')
            pw_info = dbc.get_password_info(db, collection, enc_pw)
            if "key" in pw_info:
                key = pw_info["key"]
                seed = int(pw_info["seed"])
                mode = pw_info["mode"]
        elif "key_confirmed" in context_dict:
            enc_pw = context_dict["key_confirmed"]["encrypted"]
            key = context_dict["key_confirmed"]["key"]
            seed = context_dict["key_confirmed"]["seed"]
            mode = context_dict["key_confirmed"]["mode"]
            
        target_doc = None; target_attr = None
        for doc in docs:
            for attr in doc:
                val = doc[attr]
                if val == enc_pw:
                    target_doc = doc
                    target_attr = attr
                    break
            else:
                continue
            break
        # # Comprobamos que la clave de desbloqueo del fichero es correcto
        # sk_file_key = unlock_form.pop('sk_file_key')
        # secret_file, check_msg = _check_secret_file(sk_file_key=sk_file_key)
        # if not secret_file:
        #     context_dict["warning"] = check_msg
            
        if key is not None:
            if target_doc is not None:
                try:
                    decrypted = decrypt(enc_pw, seed, key, mode)
                    index = docs.index(doc)
                    target_doc[target_attr] = decrypted
                    docs.pop(index)
                    docs.insert(index, target_doc)
                    context_dict["msg"] = f"Contraseña '{enc_pw}' desbloqueada"
                except Exception:
                    msg = "Fallo al desencriptar, comprueba que el fichero "
                    msg += "'server/secret_key.py' es el correcto"
                    context_dict["err_msg"] = msg
        elif secret_file:
            _set_extra_vars({'display_view': True}, 'validate_key')
            target_doc_id = target_doc["id"]
            if type(docs) is dict:
                index = 1
            elif type(docs) is list:
                index = docs[::-1].index(target_doc) + 1
            return HttpResponseRedirect(f'/validate/{db}/{collection}/{target_doc_id}--{index}/{target_attr}')
        else:
            msg = "Es necesario un fichero 'server/secret_key.py' para "
            msg += f"desbloquear la contraseña '{enc_pw}'"
            context_dict["err_msg"] = msg
    elif "lock" in unlock_form:
        doc_id = unlock_form.pop('lock')
        for i, doc in enumerate(docs[::-1]):
            if doc["id"] == doc_id:
                index = i
        context_dict["id_to_scroll"] = index + 1
        
    # Mostramos los documentos segun si hay o no hay modelo establecido
    model_doc = dbc.get_model(db, collection)
    context_dict["model"] = model_doc
    if bool(model_doc):
        # Miramos si hay algun atributo que sea un numero 
        has_passwords = False
        for attr_dict in model_doc.values():
            tp = attr_dict["type"]
            if tp != 'str' and tp != 'password':
                context_dict["numbers"] = True
                break
            elif tp == 'password':
                has_passwords = True
        else:
            context_dict["numbers"] = False
        # Quitamos el warning si no hay contraseñas en el modelo
        if not has_passwords and 'warning' in context_dict:
            context_dict.pop("warning")
            
        if not bool(docs):
            err_msg = "No existen documentos en esta coleccion"
            if "filtered" in context_dict:
                err_msg = "No se han encontrado coincidencias"
            context_dict["err_msg"] = err_msg
        else:
            docs = docs[::-1]
            context_dict["docs"] = docs
    else:
        num = 20; context_dict["show_more"] = True
        form_dict = _clean_form(request.GET); docs_len = len(docs)
        if "show_more" in form_dict:
            actual_num = form_dict["show_more"]
            context_dict["id_to_scroll"] = actual_num
            num = int(actual_num) + 10
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

def _encrypt(doc:dict, model:dict, db:str, collection:str):
    for attr_dict in model.values():
        name = attr_dict["name"]
        if attr_dict["type"] == "password":
            value = doc[name]; ex_passwords = dbc.get_passwords(db, collection)
            if value != "-" and value not in ex_passwords:
                encrypted = None; decrypted = None; attempts = 1000
                while (encrypted is None or encrypted in ex_passwords
                    or decrypted != value):
                    encrypted, seed, key, mode = encrypt(value)
                    decrypted = decrypt(encrypted, seed, key, mode=mode)
                    attempts -= 1
                    if attempts == 0:
                        msg = f" No se ha podido encryptar la contraseña '{value}'"
                        raise EncryptionError(msg)
                doc[name] = encrypted
                is_valid, _ = _check_secret_file()
                if is_valid:
                    import server.secret_key as sk
                    seed = sk.hide(key, seed)
                    pw_info = {
                        "encryption_info":
                            {"mode": mode, "seed": str(seed)}
                    }
                else:
                    pw_info = {
                        "encryption_info":
                            {"mode": mode, "seed": str(seed), "key": key}
                    }
                dbc.add_password(db, collection, encrypted, pw_info)
                
@_view_inspector
def add_document(request:HttpRequest, db:str, collection:str) -> HttpResponse:
    context_dict = {"db": db, "collection": collection}
    context_dict["textareas"] = []; context_dict["show_pwds"] = []
    context_dict["values"] = {}
    extra_vars = _get_extra_vars('add_document')
    for var, value in extra_vars.items():
        context_dict[var] = value
    view_params = register.load('view_params')
    if view_params["redirected"]:
        context_dict["textareas"] = []
        context_dict["show_pwds"] = []
        
    form_dict = _clean_form(request.POST)
    if bool(form_dict):
        if "add" in form_dict:
            form_dict.pop("add")
            doc = form_dict
            model = dbc.get_model(db, collection)
            try:
                doc = _parse_doc_attrs(model, doc)
                _encrypt(doc, model, db, collection)
            except EncryptionError as err:
                context_dict["err_msg"] = str(err)
            except Exception as err:
                context_dict["err_msg"] = str(err)
            else:
                dbc.add_document(db, collection, doc)
                msg = "Documento añadido con exito"
                _set_extra_vars({"msg": msg}, "display_documents")
                return HttpResponseRedirect(f"/display/{db}/{collection}")
        elif "textarea" in form_dict:
            attr = form_dict.pop("textarea")
            if attr in context_dict["textareas"]:
                context_dict["textareas"].remove(attr)
            else:
                context_dict["textareas"].append(attr)
        elif "show" in form_dict:
            attr = form_dict.pop("show")
            if attr in context_dict["show_pwds"]:
                context_dict["show_pwds"].remove(attr)
            else:
                context_dict["show_pwds"].append(attr)
                
        context_dict["values"] = form_dict
    
    model = dbc.get_model(db, collection)
    context_dict["model"] = model
        
    _set_extra_vars(
        {"textareas": 
            context_dict["textareas"],
         "show_pwds": 
            context_dict["show_pwds"]},
        'add_document')
    context_dict["add_doc"] = True
    return render(request, 'add.html', context_dict)

@_view_inspector
def duplicate_document(request:HttpRequest, db:str, collection:str, doc_id:str) -> HttpResponse:
    if "--" in doc_id:
        doc_index = ""
        for i, num in enumerate(doc_id[::-1]):
            if num == "-":
                doc_index = int(doc_index[::-1])
                doc_id = doc_id[:len(doc_id)-i-2]
                break
            doc_index += str(num)
        print(doc_index)
        _set_extra_vars({"id_to_scroll": doc_index} ,'display_documents')
    docs = dbc.get_documents(db, collection, with_app_format=False)
    for doc in docs:
        if doc["_id"] == "model" or doc["_id"] == "passwords": continue
        dbc.delete_document(db, collection, doc["_id"], delete_pwds=False)
    for doc in docs:
        if doc["_id"] == "model" or doc["_id"] == "passwords": continue
        elif doc["_id"] == doc_id: 
            dbc.add_document(db, collection, doc)
            doc.pop("_id")
            model = dbc.get_model(db, collection)
            for attr_dict in model.values():
                name = attr_dict["name"]
                if attr_dict["type"] == 'password':
                    doc[name] = "-" 
                
        dbc.add_document(db, collection, doc)
    
    _set_extra_vars({"msg": f"Documento con id '{doc_id}' duplicado con exito"}, 'display_documents')
    return HttpResponseRedirect(f'/display/{db}/{collection}')


@_view_inspector
def update_document(request:HttpRequest, db:str, collection:str, doc_id:str) -> HttpResponse:
    if "--" in doc_id:
        doc_index = ""
        for i, num in enumerate(doc_id[::-1]):
            if num == "-":
                doc_index = int(doc_index[::-1])
                doc_id = doc_id[:len(doc_id)-i-2]
                break
            doc_index += str(num)
        _set_extra_vars({"id_to_scroll": doc_index} ,'display_documents')        
    secret_file, _ = _check_secret_file()
    context_dict = {"db": db, "collection": collection}
    context_dict["textareas"] = []; context_dict["show_pwds"] = []; context_dict["locked_pwds"] = {}
    context_dict["values"] = {}
    extra_vars = _get_extra_vars('update_document')
    
    for var, value in extra_vars.items():
        context_dict[var] = value
    view_params = register.load('view_params')
        
    doc = dbc.find_doc_by_id(db, collection, doc_id)
    context_dict["doc_id"] = doc_id
    context_dict["values"] = doc
    model = dbc.get_model(db, collection)
    context_dict["model"] = model
    # Miramos si hay contraseñas vacías
    void_pwds = []
    for attr_dict in model.values():
        name = attr_dict["name"]; val = doc[name]
        if attr_dict["type"] == 'password' and val == "-":
            void_pwds.append(name)
    context_dict["void_pwds"] = void_pwds
    
    # Vemos si nos han redirigido o ha sido un boton de la view (textareas ...)
    if view_params["redirected"]:
        # 1. Vemos si algun texto supera los 22 caracteres para que se
        # presente directamente con textarea y no pierda el formato de
        # saltos de linea etc
        # 2. Bloqueamos los inputs de contraseñas hasta que se desbloqueen con la clave
        # para que no se puedan editar
        model = context_dict["model"]
        initial_textareas = []; initial_locked = {}
        for attr_dict in model.values():
            tp = attr_dict["type"]; name = attr_dict["name"]
            if tp == 'str' :
                string = doc[name]
                cond2 = "\n" in string or "\r" in string
                if len(string) > 21 or cond2:
                    initial_textareas.append(name)
            elif tp == 'password' and doc[name] != "-":
                initial_locked[name] = doc[name]
        context_dict["textareas"] = initial_textareas
        context_dict["locked_pwds"] = initial_locked
        context_dict["show_pwds"] = []
    
    form_dict = _clean_form(request.POST)
    if bool(form_dict):
        form_dict.update(context_dict["locked_pwds"])
        if "update" in form_dict:
            form_dict.pop("update")
            new_doc = form_dict
            try:
                model = dbc.get_model(db, collection)
                new_doc = _parse_doc_attrs(model, new_doc)
                _encrypt(new_doc, model, db, collection)
            except EncryptionError as err:
                context_dict["err_msg"] = str(err)
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
        elif "show" in form_dict:
            attr = form_dict.pop("show")
            if attr in context_dict["show_pwds"]:
                context_dict["show_pwds"].remove(attr)
            else:
                context_dict["show_pwds"].append(attr)
                
        context_dict["values"] = form_dict
    # Desencriptamos la contraseña seleccionada
    if "unlock" in form_dict or "key_confirmed" in context_dict:
        key = None
        if "unlock" in form_dict:
            attr = form_dict.pop("unlock")
            enc_pw = doc[attr]
            pw_info = dbc.get_password_info(db, collection, enc_pw)
            if pw_info is None:
                msg = f"La contraseña '{enc_pw}' no se encuentra almacenada en el sistema"
                context_dict["err_msg"] = msg
            elif "key" in pw_info:
                key = pw_info["key"]
                seed = int(pw_info["seed"])
                mode = pw_info["mode"]
        elif "key_confirmed" in context_dict:
            enc_pw = context_dict["key_confirmed"]["encrypted"]
            key = context_dict["key_confirmed"]["key"]
            seed = context_dict["key_confirmed"]["seed"]
            mode = context_dict["key_confirmed"]["mode"]
        if key is not None:
            try:
                decrypted = decrypt(enc_pw, seed, key, mode)
                for key in doc:
                    if doc[key] == enc_pw:
                        doc[key] = decrypted
                        context_dict["locked_pwds"].pop(key)  
                        context_dict["show_pwds"].append(key)
                        break   
                context_dict["msg"] = f"Contraseña '{enc_pw}' desbloqueada"
                context_dict["values"] = doc
            except Exception:
                msg = "Fallo al desencriptar, comprueba que el fichero "
                msg += "'server/secret_key.py' es el correcto"
                context_dict["err_msg"] = msg
        elif secret_file:
            _set_extra_vars({'update_view': True, "doc_id": doc_id}, 'validate_key')
            attr = None
            for key in doc:
                if doc[key] == enc_pw:
                    attr = key
                    break
            return HttpResponseRedirect(f'/validate/{db}/{collection}/{doc_id}/{attr}')
        else:
            msg = "Es necesario un fichero 'server/secret_key.py' para "
            msg += f"desbloquear la contraseña '{enc_pw}'"
            context_dict["err_msg"] = msg
            
    _set_extra_vars(
        {"textareas": 
            context_dict["textareas"],
         "show_pwds": 
            context_dict["show_pwds"],
         "locked_pwds": 
             context_dict["locked_pwds"],}, 'update_document')
    context_dict["update_doc"] = True
    return render(request, "update.html", context_dict)

@_view_inspector
def delete_document(request:HttpRequest, db:str, collection:str, doc_id:str) -> HttpResponse:
    if "--" in doc_id:
        doc_index = ""
        for i, num in enumerate(doc_id[::-1]):
            if num == "-":
                doc_index = int(doc_index[::-1])
                doc_id = doc_id[:len(doc_id)-i-2]
                break
            doc_index += str(num)
        _set_extra_vars({"id_to_scroll": doc_index} ,'display_documents')
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

def _form_to_mongo_queries(form_dict:dict, model:dict) -> dict:
    queries = {}
    for attr_dict in model.values():
        name = attr_dict["name"]; tp = attr_dict["type"]
        operator = form_dict[f"{name}_select"]; value:str = form_dict[name]
        if value == "": continue
        if tp == 'str' or tp == 'password':
            case = form_dict[f"{name}_case"]
            if operator == 'equals': 
                query = {name: value}
                if case == 'ignore_case': 
                    query = {"$or":[
                        {name: value}, 
                        {name: value.lower()}, 
                        {name: value.upper()}
                    ]}      
            elif operator == 'contains': 
                query = {name: {"$regex": value}}
                if case == 'ignore_case': 
                    query[name].update({"$options": 'i'})
        elif tp == 'int' or tp == 'float':
            if operator == 'eq': query = {name: value}
            elif operator == 'gt': query = {name: {"$gt": value}}
            elif operator == 'gte': query = {name: {"$gte": value}}
            elif operator == 'lt': query = {name: {"$lt": value}}
            elif operator == 'lte': query = {name: {"$lte": value}}
        queries.update(query)
        
    return queries
            
@_view_inspector
def filter_documents(request:HttpRequest, db:str, collection:str) -> HttpResponse:
    context_dict = _get_extra_vars('filter_documents')
    context_dict.update({"db": db, "collection": collection})
    model = dbc.get_model(db, collection)
    context_dict["model"] = model
    if "update_filter" in context_dict:
        context_dict["values"] = register.load('filters')[f"{db}.{collection}"]["filter"]
    else:
        context_dict["values"] = {}
    extra_vars = _get_extra_vars('filter_documents')
    for var, value in extra_vars.items():
        context_dict[var] = value
    view_params = register.load('view_params')
    if view_params["redirected"]:
        context_dict["textareas"] = []
    
    form_dict = _clean_form(request.POST)
    if bool(form_dict):
        if 'filter' in form_dict:
            form_dict.pop('filter')
            try:
                filter_dict = _parse_doc_attrs(model, form_dict, filter_=True)
            except Exception as err:
                context_dict["err_msg"] = str(err)
            else:
                queries = _form_to_mongo_queries(filter_dict, model)
                filters:dict = register.load('filters')
                if filters is None:
                    filters = {f"{db}.{collection}": {"queries":queries, "filter": filter_dict}}
                    register.add('filters', filters)
                else:
                    filters[f"{db}.{collection}"] = {"queries":queries, "filter": filter_dict}
                    register.update('filters', filters)
                return HttpResponseRedirect(f'/display/{db}/{collection}')
        elif 'textarea' in form_dict:
            attr = form_dict.pop("textarea")
            if attr in context_dict["textareas"]:
                context_dict["textareas"].remove(attr)
            else:
                context_dict["textareas"].append(attr)
        context_dict["values"] = form_dict
                
    _set_extra_vars({"textareas": context_dict["textareas"]}, 'filter_documents')
    return render(request, 'filter.html', context_dict)

@_view_inspector
def sort_documents(request:HttpRequest, db:str, collection:str) -> HttpResponse:
    context_dict = _get_extra_vars('sort_documents')
    context_dict.update({"db": db, "collection": collection})
    if "update_sorter" in context_dict:
        sorter:dict = register.load('sorters')[f"{db}.{collection}"]
        context_dict["values"] = sorter
        context_dict["sort_attrs"] = list(sorter.keys())
    else:
        context_dict["values"] = {}
        view_params= register.load('view_params')
        if "sort_attrs" not in context_dict or view_params["redirected"]:
            context_dict["sort_attrs"] = []
    
    form_dict = _clean_form(request.POST)
    if bool(form_dict):
        if "plus" in form_dict:
            attr = form_dict.pop("plus")
            context_dict["sort_attrs"].append(attr)
        elif "minus" in form_dict:
            attr = form_dict.pop("minus")
            context_dict["sort_attrs"].remove(attr)
        elif "sort" in form_dict:
            form_dict.pop("sort"); sorter = form_dict
            sorters = register.load('sorters')
            if sorters is None:
                sorters = {f"{db}.{collection}": sorter}
                register.add('sorters', sorters)
            else:
                sorters[f"{db}.{collection}"] = sorter
                register.update('sorters', sorters)
            return HttpResponseRedirect(f'/display/{db}/{collection}')
        context_dict["values"] = form_dict

    model = dbc.get_model(db, collection)
    context_dict["model"] = model
    _set_extra_vars({"sort_attrs": context_dict["sort_attrs"]}, 'sort_documents')
    return render(request, 'sort.html', context_dict)