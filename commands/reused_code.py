
import os

from mypy_modules.process import process
from mypy_modules.register import register

GITHUB_URL = f"https://github.com"
SECURE_DIR = "__secure-dir__"

def save_github_info(change=False):
    github_info = register.load('github')
    if github_info is None or change:
        print()
        print(" -> AÑADIR REPOSITORIO")
        user = str(input("    + Introduce el usuario de github: "))
        repo_name = str(input("    + Introduce el nombre del repositorio: "))
        msg = ("    + Introduce el nombre del directorio donde se guardara/descargara " + 
               "la informacion: ")
        dir_name = str(input(msg))
        print()
        new_github_info = {'user': user, 'repo_name': repo_name, 'dir_name': dir_name}
        if github_info is None:
            register.add('github', new_github_info)
        else:
            register.update('github', new_github_info)
             
def get_github_info() -> list:
    github_info = register.load('github')
    return list(github_info.values())

def download_repo():
    # Vemos si tenemos los datos del repositorio guardados y si no los pedimos
    github_user, repo_name, dir_name = get_github_info()
    # Descargamos el repositorio de bases de datos almacenado en github
    if os.path.exists(SECURE_DIR):
        remove_repo()
    try:
        process.run(f"git clone {GITHUB_URL}/{github_user}/{repo_name} {SECURE_DIR}", shell=True)
    except process.ProcessErr as err:
        msg = (" Error al descargar el repositorio de github " + 
            f"({GITHUB_URL}/{github_user}/{repo_name}) -> {err}")
        raise process.ProcessErr(msg) 

def remove_repo():
    # Eliminamos la base de datos anterior descargada (carpeta '{REPO_NAME}')
    try:
        process.run(f'del /f/q/s {SECURE_DIR} & rmdir /q/s {SECURE_DIR}', shell=True)
    except process.ProcessErr as err:
        msg = f" Fallo al eliminar el repositorio descargado de github -> {err}"
        raise process.ProcessErr(msg)
    
