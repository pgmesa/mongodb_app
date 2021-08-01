
import os

from mypy_modules.process import process

REPO_NAME = "databases"
DDBB_CLOUD_NAME = "mongoapp"

def download_repo():
    # Descargamos el repositorio de bases de datos almacenado en github
    if os.path.exists(REPO_NAME):
        os.remove(REPO_NAME)
    try:
        process.run(f"git clone https://github.com/pgmesa/{REPO_NAME}", shell=True)
    except process.ProcessErr as err:
        msg = (" Error al descargar la base de datos en la nube " + 
            f"(https://github.com/pgmesa/{REPO_NAME}) -> {err}")
        raise process.ProcessErr(msg)

def remove_repo():
    # Eliminamos la base de datos anterior descargada (carpeta '{REPO_NAME}')
    try:
        process.run(f'del /f/q/s {REPO_NAME} & rmdir /q/s {REPO_NAME}', shell=True)
    except process.ProcessErr as err:
        msg = f" Fallo al eliminar carpeta '{REPO_NAME}' descargada de github -> {err}"
        raise process.ProcessErr(msg)