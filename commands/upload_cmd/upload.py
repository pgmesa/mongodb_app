
import os
import json
import logging
import subprocess

# Imports de definicionde comando
from mypy_modules.cli import Command, Flag, Option
# Imports para la funcion del comando
from controllers import db_controller as dbc
from configs.settings import BASE_DIR
from ..reused_code import (
    MongoNotInstalledError, download_repo, check_input_time, check_mongo_installed, remove_repo, 
    GITHUB_URL, get_github_info, save_github_info, SECURE_DIR, TASKS_DIR
)
from mypy_modules.process import process
from mypy_modules.register import register

def get_upload_cmd() -> Command:
    msg = f"""uploads the mongoapp to the github repository specified"""
    upload = Command(
        'upload', description=msg
    )
    # --------------------------------
    create_task_cmd = def_create_task_opt()
    upload.add_option(create_task_cmd)
    # --------------------------------
    show_task_cmd = def_show_task_opt()
    upload.add_option(show_task_cmd)
    # --------------------------------
    delete_task_cmd = def_delete_task_opt()
    upload.add_option(delete_task_cmd)

    return upload

# --------------------------------------------------------------------
def def_create_task_opt():
    msg = f"""<HH:MM> schedules an automatic upload. By default the
    task will be completed daily at the specified time"""
    create_task = Option(
        '--create-task', description=msg,
        extra_arg=True, mandatory=True
    )
    
    return create_task

def def_show_task_opt():
    msg = f"""shows the created task information"""
    show_task = Option(
        '--show-task', description=msg
    )
    
    return show_task

def def_delete_task_opt():
    msg = f"""Deletes the task previously created"""
    delete_task = Option(
        '--delete-task', description=msg
    )
    
    return delete_task

# --------------------------------------------------------------------
# --------------------------------------------------------------------
upload_logger = logging.getLogger(__name__)
def upload(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    try:
        check_mongo_installed()
    except MongoNotInstalledError as err:
        upload_logger.error(err)
        return
    # Procesamos las Opciones
    tasks = register.load('tasks')
    if tasks is None:
        tasks = {}
        register.add('tasks', tasks)
    if '--create-task' in options:
        task = tasks.get('upload', None)
        if task is not None:
            upload_logger.error(" Ya existe una tarea creada")
            return
        time = options['--create-task'][0]
        try:
            check_input_time(time)
        except Exception as err:
            msg = (f" El tiempo introducido '{time}' no es correcto" + 
                   f"\n     ERR MSG -> {err}")
            upload_logger.error(msg)
            return
        cmd = (f'SCHTASKS /CREATE /SC DAILY /TN "{TASKS_DIR}\\upload" ' +
                f'/TR "mongoapp upload" /ST {time}')
        try:
            process.run(cmd, shell=True)
            tasks['upload'] = {'type': 'daily', 'time': time}
            register.update('tasks', tasks)
            upload_logger.info(f" Tarea creada con exito a las '{time}'")
        except Exception as err:
            err_msg = (" Error al intentar programar la tarea\n" + 
                        f"      ERR MSG: {err}")
            upload_logger.error(err_msg)
        return
    elif '--show-task' in options:
        task:dict = tasks.get('upload', None)
        if task is None:
            msg = " No existe ninguna tarea creada para este comando"
            upload_logger.error(msg)
        else:
            pretty = json.dumps(task, indent=4, sort_keys=True)
            print();print(pretty);print()
        return
    elif '--delete-task' in options:
        task = tasks.get('upload', None)
        if task is None:
            msg = " No existe ninguna tarea que eliminar para este comando"
            upload_logger.error(msg)
            return
        cmd = (f'SCHTASKS /DELETE /TN "{TASKS_DIR}\\upload" /F')
        try:
            process.run(cmd, shell=True)
            tasks.pop('upload')
            register.update('tasks', tasks)
            upload_logger.info(" Tarea eliminada con exito")
        except Exception as err:
            err_msg = (" Error al intentar eliminar la tarea\n" + 
                        f"      ERR MSG: {err}")
            upload_logger.error(err_msg)
        return
    # Ejecutamos el comando principal
    # Descargamos la base de datos de github y eliminamos el registro 
    # anterior de la mongoapp para reemplazarlo
    save_github_info()
    try:
        download_repo()
    except process.ProcessErr as err:
        upload_logger.error(err); return
    github_user, repo_name, dir_name = get_github_info()
    ddbb_path = BASE_DIR/f'{SECURE_DIR}'
    rel_db_app_path = f'{SECURE_DIR}/{dir_name}'
    files = os.listdir(ddbb_path)
    if dir_name in files:
        try:
            process.run(f'cd {SECURE_DIR} & del /f/q/s "{dir_name}" '
                        + f'& rmdir /q/s "{dir_name}"', shell=True)
        except process.ProcessErr as err:
            msg = f" Fallo al eliminar carpeta mongoapp para reemplazar -> {err}"
            upload_logger.error(msg) 
            return
    # Metemos la info de mongo en la nueva carpeta (la estamos reemplazando)
    msg = " Descargando documentos de mongodb pertenecientes a la aplicacion..."
    upload_logger.info(msg)
    process.run(f'cd {SECURE_DIR} & mkdir "{dir_name}"', shell=True)
    dbs = dbc.list_dbs(only_app_dbs=True)
    for db in dbs:
        process.run(f'cd "{rel_db_app_path}" & mkdir "{db}"', shell=True)
        collections = dbc.list_collections(db, only_app_coll=True)
        for collection in collections:
            docs = dbc.get_documents(db, collection, with_app_format=False)
            path = BASE_DIR/f'{rel_db_app_path}/{db}/{collection}.json'
            with open(path, "w") as file:
                json.dump(docs, file, indent=4, sort_keys=True)
    # Actualizamos la informacion en github
    msg = f" Actualizando base de datos '{dir_name}' en github..."
    upload_logger.info(msg)
    # git config --global --unset user.name
    # git config --global user.email "you@example.com"
    orders = []
    order1 = 'git add .'
    orders.append(order1)
    order2 = f'git commit -m "Actualizando {dir_name}"'
    orders.append(order2)
    branches = process.run(f"cd {SECURE_DIR} & git branch", shell=True)
    if branches == "":
        order3 = 'git branch -M main'
        orders.append(order3)
    order4 = 'git push origin main'
    orders.append(order4)
    for order in orders:
        proc = subprocess.Popen(order, shell=True, cwd=SECURE_DIR)
        proc.wait()
        if proc.returncode != 0:
            msg = f" No se ha podido actualizar la informacion en github"
            upload_logger.error(msg)
            break
    else:
        upload_logger.info(" Cambios actualizados en github con exito")
    # Eliminamos el repositorio descargado anteriormente
    try:
        remove_repo()
    except process.ProcessErr as err:
        upload_logger.error(err); return