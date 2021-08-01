import subprocess

class ProcessErr(Exception):
    pass

def run(cmd, stdout=True, stderr=True, shell=False) -> str:
    """Ejecuta un comando mediante subprocess y controla los 
    errores que puedan surgir. Espera a que termine el proceso
    (Llamada bloqueante)

    Args:
        cmd (list): Comando a ejecutar. Se debe pasar como una lista de
            strings cuando shell sea False. Si shell es True, 'cmd' debe 
            ser un string
        stdout (bool): Captura la salida estandar del programa ejecutado 
            con el comando introducido
        stderr (bool): Captura la salida estandar de errores del programa 
            ejecutado con el comando introducido
        shell (bool): Indica si la orden se ejecuta directamente en una
            terminal de SO en el que se encuentre o en el interprete de 
            ordenes de python
    Raises:
        LxcError: Si surge algun error ejecutando el comando
        LxcNetworkError: Si surge algun error ejecutando en comando
            relacioneado con los bridge (networks)
    """
    options = {}
    if stdout:
        options["stdout"] = subprocess.PIPE
    options["stderr"] = subprocess.PIPE
    try:
        process = subprocess.run(cmd, **options, shell=shell)
    except Exception as err:
        err_msg = f"El comando introducido no es valido: '{err}'"
        raise ProcessErr(err_msg)
    outcome = process.returncode
    if outcome != 0:
        err_msg = f" Fallo al ejecutar el comando '{cmd}'"
        if stderr:
            err = process.stderr.decode()[:-1]
            err_msg += f"\nMensaje de error: -> '{err}'"
        elif stdout:
            err_msg = process.stdout.decode()
        raise ProcessErr(err_msg)
    if stdout:
        try:
            return process.stdout.decode()
        except:
            return "No se ha podido decodificar la salida estandar con utf-8"

def Popen(order:str, shell=False) -> None:
    if not shell: 
        if type(order) is not list:
            msg = ("Si 'shell' no se activa, la orden introducida"
             + " debe ser un lista")
            raise ProcessErr(msg)
    subprocess.Popen(order, shell=shell) 